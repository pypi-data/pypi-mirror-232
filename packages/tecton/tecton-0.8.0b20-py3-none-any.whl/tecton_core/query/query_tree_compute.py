import dataclasses
import logging
import threading
import typing
from abc import ABC
from abc import abstractmethod
from typing import Optional

import attrs
import pandas as pd
import pyarrow
import sqlparse

from tecton_core import conf
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.sql_compat import Dialect
from tecton_core.time_utils import convert_pandas_df_for_snowflake_upload


if typing.TYPE_CHECKING:
    import snowflake.snowpark
    from duckdb import DuckDBPyConnection

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class StagingConfig:
    sql_string: str
    table_name: str
    num_partitions: Optional[int]


class QueryTreeCompute(ABC):
    """
    Base class for compute (e.g. DWH compute or Python compute) which can be
    used for different stages of executing the query tree.
    """

    @abstractmethod
    def get_dialect(self) -> Dialect:
        pass

    @abstractmethod
    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        pass

    @abstractmethod
    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        pass

    # TODO(danny): remove this once we convert connectors to return arrow tables instead of pandas dataframes
    @abstractmethod
    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        pass

    @abstractmethod
    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        pass


@attrs.define
class SnowflakeCompute(QueryTreeCompute):
    session: "snowflake.snowpark.Session"
    lock: threading.RLock = threading.RLock()
    is_debug: bool = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")

    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        if self.is_debug:
            sql_string = sqlparse.format(sql_string, reindent=True)
            logging.warning(f"SNOWFLAKE QT: run SQL {sql_string}")
        # Snowflake connections are not thread-safe. Launch Snowflake jobs without blocking the result. The lock is
        # released after the query is sent
        with self.lock:
            snowpark_df = self.session.sql(sql_string)
            if return_dataframe:
                # TODO(TEC-16169): check types are converted properly
                async_job = snowpark_df.toPandas(block=False)
            else:
                async_job = snowpark_df.collect(block=False)

        if return_dataframe:
            df = async_job.result(result_type="pandas")
            df = self._post_process_pandas(snowpark_df, df)
            return pyarrow.Table.from_pandas(df)
        else:
            async_job.result(result_type="no_result")
            return None

    @staticmethod
    def _post_process_pandas(snowpark_df: "snowflake.snowpark.DataFrame", pandas_df: pd.DataFrame) -> pd.DataFrame:
        """Converts a Snowpark DataFrame to a Pandas DataFrame while preserving types."""
        import snowflake.snowpark

        snowpark_schema = snowpark_df.schema

        for field in snowpark_schema:
            # TODO(TEC-16169): Handle other types.
            if field.datatype == snowflake.snowpark.types.LongType():
                pandas_df[field.name] = pandas_df[field.name].astype("int64")

        return pandas_df

    def get_dialect(self) -> Dialect:
        return Dialect.SNOWFLAKE

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        # Not quoting identifiers / keeping the upload case-insensitive to be consistent with the query tree sql
        # generation logic, which is also case-insensitive. (i.e. will upper case selected fields).
        df_to_write = pandas_df.copy()
        convert_pandas_df_for_snowflake_upload(df_to_write)
        self.session.write_pandas(
            df_to_write,
            table_name=table_name,
            auto_create_table=True,
            table_type="temporary",
            quote_identifiers=False,
            overwrite=True,
        )

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        self.register_temp_table_from_pandas(table_name, pa_table.to_pandas())

    def stage(self, staging_config: StagingConfig) -> pyarrow.Table:
        return self.run_sql(staging_config.sql_string, return_dataframe=True)


# TODO(danny): consider cleaning up tables, which are dropped for in memory duckdb, but not for persistent DuckDB
@attrs.define
class DuckDBCompute(QueryTreeCompute):
    session: "DuckDBPyConnection"
    is_debug: bool = attrs.field(init=False)

    def __attrs_post_init__(self):
        self.is_debug = conf.get_bool("DUCKDB_DEBUG")

    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        # Notes on case sensitivity:
        # 1. DuckDB is case insensitive when referring to column names, though preserves the
        #    underlying data casing when exporting to e.g. parquet.
        #    See https://duckdb.org/2022/05/04/friendlier-sql.html#case-insensitivity-while-maintaining-case
        #    This means that when using Snowflake for pipeline compute, the view + m13n schema is auto upper-cased
        # 2. When there is a spine provided, the original casing of that spine is used (since DuckDB separately
        #    registers the spine).
        # 3. When exporting values out of DuckDB (to user, or for ODFVs), we coerce the casing to respect the
        #    explicit schema specified. Thus ODFV definitions should reference the casing specified in the dependent
        #    FV's m13n schema.
        if self.is_debug:
            sql_string = sqlparse.format(sql_string, reindent=True)
            logging.warning(f"DUCKDB: run SQL {sql_string}")
        # Need to use DuckDB cursor (which creates a new connection based on the original connection)
        # to be thread-safe. It avoids a mysterious "unsuccessful or closed pending query result" error too.
        duckdb_relation = self.session.cursor().sql(sql_string)
        if return_dataframe:
            return duckdb_relation.arrow()
        return None

    def get_dialect(self) -> Dialect:
        return Dialect.DUCKDB

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        self.run_sql(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM pandas_df")

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        # NOTE: alternatively, can page through table + insert with SELECT *
        # FROM pa_table LIMIT 100000 OFFSET 100000*<step>. This doesn't seem
        # to offer any memory benefits and only slows down the insert.
        self.run_sql(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM pa_table")

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        # TODO: leverage duckdb udfs
        pass

    def stage(self, staging_config: StagingConfig) -> pyarrow.Table:
        # First stage into an in memory table in DuckDB before exporting
        create_table_sql = f"CREATE OR REPLACE TABLE {staging_config.table_name} AS ({staging_config.sql_string})"
        self.run_sql(create_table_sql)
        return self.run_sql(f"SELECT * FROM {staging_config.table_name}", return_dataframe=True)


@attrs.frozen
class PandasCompute(QueryTreeCompute):
    # For executing pipelines, Pandas will execute only the data source scan + pipeline nodes. Other
    # logic e.g. around asof joins are executed using DuckDB.
    sql_compute: DuckDBCompute

    def run_sql(self, sql_string: str, return_dataframe: bool = False) -> Optional[pyarrow.Table]:
        return self.sql_compute.run_sql(sql_string, return_dataframe)

    def get_dialect(self) -> Dialect:
        return Dialect.DUCKDB

    def register_temp_table_from_pandas(self, table_name: str, pandas_df: pd.DataFrame) -> None:
        self.sql_compute.register_temp_table_from_pandas(table_name, pandas_df)

    def register_temp_table(self, table_name: str, pa_table: pyarrow.Table) -> None:
        self.sql_compute.register_temp_table(table_name, pa_table)

    def run_odfv(self, qt_node: NodeRef, input_df: pd.DataFrame) -> pd.DataFrame:
        from tecton_core.query.pandas.translate import pandas_convert_odfv_only

        if conf.get_bool("DUCKDB_DEBUG"):
            logger.warning(f"Input dataframe to ODFV execution: {input_df.dtypes}")

        pandas_node = pandas_convert_odfv_only(qt_node, input_df)
        return pandas_node.to_dataframe()

    def stage(self, staging_config: StagingConfig) -> Optional[pyarrow.Table]:
        return self.sql_compute.stage(staging_config)
