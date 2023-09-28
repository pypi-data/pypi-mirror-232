import contextlib
import logging
from concurrent.futures import Future
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

import attrs
import pandas as pd
import pyarrow

from tecton_core import conf
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_core.query.node_interface import recurse_query_tree
from tecton_core.query.node_utils import get_pipeline_dialect
from tecton_core.query.node_utils import get_staging_nodes
from tecton_core.query.nodes import DataSourceScanNode
from tecton_core.query.nodes import MultiOdfvPipelineNode
from tecton_core.query.nodes import StagingNode
from tecton_core.query.nodes import UserSpecifiedDataNode
from tecton_core.query.pandas.rewrite import PandasTreeRewriter
from tecton_core.query.query_tree_compute import QueryTreeCompute
from tecton_core.query.query_tree_compute import StagingConfig
from tecton_core.query.rewrite import QueryTreeRewriter
from tecton_core.query.sql_compat import Dialect


NUM_STAGING_PARTITIONS = 10
logger = logging.getLogger(__name__)


@dataclass
class QueryTreeOutput:
    # A map from table name to pyarrow table
    staged_data: Dict[str, pyarrow.Table]
    odfv_input: Optional[pyarrow.Table] = None
    odfv_output: Optional[pd.DataFrame] = None

    @property
    def result_df(self) -> pd.DataFrame:
        if self.odfv_output is not None:
            return self.odfv_output
        assert self.odfv_input is not None
        return self.odfv_input.to_pandas()

    @property
    def result_table(self) -> pyarrow.Table:
        assert self.odfv_output is None, "Can't retrieve ODFV output as a pyarrow table"
        return self.odfv_input


@attrs.define
class QueryTreeExecutor:
    pipeline_compute: QueryTreeCompute
    agg_compute: QueryTreeCompute
    # TODO(danny): Consider separating aggregation from AsOfJoin, so we can process sub nodes and delete old
    #  tables in duckdb when doing `from_source=True`
    odfv_compute: QueryTreeCompute
    query_tree_rewriter: QueryTreeRewriter
    executor: ThreadPoolExecutor = attrs.field(init=False)
    is_debug: bool = attrs.field(init=False)
    is_benchmark: bool = attrs.field(init=False)
    _temp_table_registered: Optional[Dict[str, set]] = None

    def __attrs_post_init__(self):
        # TODO(danny): Expose as configs
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")
        self.is_benchmark = conf.get_bool("DUCKDB_BENCHMARK")

    def cleanup(self):
        self.executor.shutdown()
        # TODO(danny): drop temp tables

    @contextlib.contextmanager
    def _measure_stage(self, step: QueryTreeStep, node: NodeRef) -> Iterator[None]:
        if self.is_debug:
            logger.warning(f"------------- Executing stage: {step} -------------")
            logger.warning(f"QT: \n{node.pretty_str(description=False)}")
        start_time = datetime.now()
        yield
        if self.is_benchmark:
            stage_done_time = datetime.now()
            logger.warning(f"{step.name}_TIME_SEC: {(stage_done_time - start_time).total_seconds()}")

    def exec_qt(self, qt_root: NodeRef) -> QueryTreeOutput:
        # TODO(danny): make ticket to avoid needing setting a global SQL_DIALECT conf
        orig_dialect = conf.get_or_raise("SQL_DIALECT")
        try:
            if self.is_debug:
                logger.warning(
                    "---------------------------------- Executing overall QT ----------------------------------"
                )
                logger.warning(f"QT: \n{qt_root.pretty_str(columns=True)}")
            # TODO(danny): refactor this into separate QT type
            if isinstance(qt_root.node, DataSourceScanNode):
                # This is used if the user is using GHF(entities=) or if the spine is tecton_ds.get_data_frame()
                conf.set("SQL_DIALECT", self.pipeline_compute.get_dialect())
                output_pa = self.pipeline_compute.run_sql(qt_root.to_sql(), return_dataframe=True)
                return QueryTreeOutput(staged_data={}, odfv_input=output_pa, odfv_output=None)

            # Executes the feature view pipeline and stages into memory or S3
            with self._measure_stage(QueryTreeStep.PIPELINE, qt_root):
                output = self._execute_pipeline_stage(qt_root)
                self.query_tree_rewriter.rewrite(qt_root, QueryTreeStep.PIPELINE, self.pipeline_compute)
            # Does partial aggregations (if applicable) and spine joins
            with self._measure_stage(QueryTreeStep.AGGREGATION, qt_root):
                output = self._execute_agg_stage(output, qt_root)
                self.query_tree_rewriter.rewrite(qt_root, QueryTreeStep.AGGREGATION, self.agg_compute)
            # Runs ODFVs (if applicable)
            with self._measure_stage(QueryTreeStep.ODFV, qt_root):
                output = self._execute_odfv_stage(output, qt_root)
            return output
        finally:
            # TODO(danny): remove staged data
            conf.set("SQL_DIALECT", orig_dialect)

    def _execute_pipeline_stage(self, qt_node: NodeRef) -> QueryTreeOutput:
        pipeline_dialect = get_pipeline_dialect(qt_node)
        if pipeline_dialect == Dialect.PANDAS:
            pd_rewrite_start = datetime.now()
            rewriter = PandasTreeRewriter()
            rewriter.rewrite(qt_node, QueryTreeStep.INIT, self.pipeline_compute)
            if self.is_debug:
                logger.warning(f"PANDAS PRE INIT: \n{qt_node.pretty_str(description=False)}")
            if self.is_benchmark:
                logger.warning(f"PD_REWRITE_TIME_SEC: {(datetime.now() - pd_rewrite_start).total_seconds()}")

        conf.set("SQL_DIALECT", self.pipeline_compute.get_dialect())
        # TODO(danny): handle case where the spine is a sql query string, so no need to pull down as dataframe
        self._maybe_register_temp_tables(qt_root=qt_node, compute=self.pipeline_compute)

        # For STAGING: concurrently stage nodes matching the QueryTreeStep.PIPELINE filter
        staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.PIPELINE)
        if len(staging_nodes_to_process) == 0:
            # There are no FV that rely on raw data (e.g. ODFV with request source)
            return QueryTreeOutput(staged_data={})
        staging_futures = self._stage_tables_and_load_pa(
            nodes_to_process=staging_nodes_to_process,
            compute=self.pipeline_compute,
        )
        staged_data = {}
        for future in staging_futures:
            table_name, pa_table = future.result()
            staged_data[table_name] = pa_table

        return QueryTreeOutput(staged_data=staged_data)

    def _execute_agg_stage(self, output: QueryTreeOutput, qt_node: NodeRef) -> QueryTreeOutput:
        # Need to explicitly set this dialect since it's used for creating the SQL command in QT `to_sql` commands
        conf.set("SQL_DIALECT", self.agg_compute.get_dialect())

        # The AsOfJoins need access to a spine, which are registered here.
        self._maybe_register_temp_tables(qt_root=qt_node, compute=self.agg_compute)

        visited_tables = set()
        # Register staged pyarrow tables in agg compute
        for table_name, pa_table in output.staged_data.items():
            if self.is_debug:
                logger.warning(f"Registering staged table to agg compute with schema:\n{pa_table.schema}")
            self.agg_compute.register_temp_table(table_name, pa_table)
            visited_tables.add(table_name)

        try:
            return self._process_agg_join(output, self.agg_compute, qt_node)
        finally:
            for table in visited_tables:
                self.agg_compute.run_sql(f"DROP TABLE IF EXISTS {table}")

    def _execute_odfv_stage(self, prev_step_output: QueryTreeOutput, qt_node: NodeRef) -> QueryTreeOutput:
        assert prev_step_output
        assert prev_step_output.odfv_input is not None
        has_odfvs = self._tree_has_odfvs(qt_node)
        if has_odfvs:
            # TODO(meastham): Use pyarrow typemapper after upgrading pandas
            output_df = self.odfv_compute.run_odfv(qt_node, prev_step_output.odfv_input.to_pandas())
        else:
            output_df = None
        return QueryTreeOutput(
            staged_data=prev_step_output.staged_data,
            odfv_input=prev_step_output.odfv_input,
            odfv_output=output_df,
        )

    def _tree_has_odfvs(self, qt_node):
        has_odfvs = False

        def check_for_odfv(node):
            if isinstance(node, MultiOdfvPipelineNode):
                nonlocal has_odfvs
                has_odfvs = True

        recurse_query_tree(
            qt_node,
            lambda node: check_for_odfv(node) if not has_odfvs else None,
        )
        return has_odfvs

    def _process_agg_join(
        self, output: QueryTreeOutput, compute: QueryTreeCompute, qt_node: NodeRef
    ) -> QueryTreeOutput:
        # TODO(danny): change the "stage" in the StagingNode to be more for the destination stage
        staging_nodes_to_process = get_staging_nodes(qt_node, QueryTreeStep.AGGREGATION)

        if len(staging_nodes_to_process) > 0:
            # There should be a single StagingNode. It is either there for materialization or ODFVs.
            assert len(staging_nodes_to_process) == 1
            staging_futures = self._stage_tables_and_load_pa(
                nodes_to_process=staging_nodes_to_process,
                compute=self.agg_compute,
            )
            assert len(staging_futures) == 1
            _, pa_table = staging_futures[0].result()
            return QueryTreeOutput(staged_data=output.staged_data, odfv_input=pa_table)

        # There are no StagingNodes, so we can execute the remainder of the query tree.
        output_df_pa = compute.run_sql(qt_node.to_sql(), return_dataframe=True)
        return QueryTreeOutput(staged_data=output.staged_data, odfv_input=output_df_pa)

    def _stage_tables_and_load_pa(
        self,
        nodes_to_process: Dict[str, QueryNode],
        compute: QueryTreeCompute,
    ) -> List[Future]:
        staging_futures = []
        for _, node in nodes_to_process.items():
            # TODO(danny): also process UserSpecifiedDataNode
            if isinstance(node, StagingNode):
                future = self.executor.submit(self._process_staging_node, node, compute)
                staging_futures.append(future)
        return staging_futures

    def _process_staging_node(self, qt_node: StagingNode, compute: QueryTreeCompute) -> Tuple[str, pyarrow.Table]:
        start_time = datetime.now()
        staging_table_name = qt_node.staging_table_name_unique()
        staging_config = StagingConfig(
            sql_string=qt_node._to_staging_query_sql(),
            table_name=staging_table_name,
            num_partitions=NUM_STAGING_PARTITIONS,
        )
        memory_table = compute.stage(staging_config=staging_config)
        staging_done_time = datetime.now()
        if self.is_benchmark:
            elapsed_staging_time = (staging_done_time - start_time).total_seconds()
            logger.warning(f"STAGE_{staging_table_name}_TIME_SEC: {elapsed_staging_time}")

        return staging_table_name, memory_table

    def _maybe_register_temp_tables(self, qt_root: NodeRef, compute: QueryTreeCompute) -> None:
        self._temp_table_registered = self._temp_table_registered or {}

        dialect = compute.get_dialect()
        if dialect not in self._temp_table_registered:
            self._temp_table_registered[dialect] = set()

        def maybe_register_temp_table(node):
            if isinstance(node, UserSpecifiedDataNode):
                tmp_table_name = node.data._temp_table_name
                if tmp_table_name in self._temp_table_registered[dialect]:
                    return
                df = node.data.to_pandas()
                if self.is_debug:
                    logger.warning(
                        f"Registering user specified data to {compute.get_dialect()} with schema:\n{df.dtypes}"
                    )
                compute.register_temp_table_from_pandas(tmp_table_name, df)
                self._temp_table_registered[dialect].add(tmp_table_name)

        recurse_query_tree(
            qt_root,
            maybe_register_temp_table,
        )
