import logging

from tecton_core.query import nodes
from tecton_core.query import rewrite
from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.pandas import nodes as pandas_nodes
from tecton_core.query.query_tree_compute import QueryTreeCompute


logger = logging.getLogger(__name__)


class PandasTreeRewriter(rewrite.QueryTreeRewriter):
    node_mapping = {
        nodes.DataSourceScanNode: pandas_nodes.PandasDataSourceScanNode,
        nodes.FeatureViewPipelineNode: pandas_nodes.PandasFeatureViewPipelineNode,
        nodes.FeatureTimeFilterNode: pandas_nodes.PandasFeatureTimeFilterNode,
    }

    def rewrite(self, tree: NodeRef, prev_query_tree_step: QueryTreeStep, query_tree_compute: QueryTreeCompute) -> None:
        if prev_query_tree_step == QueryTreeStep.INIT:
            self._rewrite_init(tree, query_tree_compute)
            return

    def _rewrite_init(self, tree: NodeRef, query_tree_compute: QueryTreeCompute) -> None:
        tree_node = tree.node
        if tree.node.__class__ in self.node_mapping.values():
            # Don't rewrite something that already is mapped. This can happen if the same QT node is referenced
            # multiple times in the tree.
            #
            # e.g. in GHF(start,end time), the pipeline node output is used for partial
            # agg and for spine construction
            return

        if isinstance(tree_node, nodes.FeatureViewPipelineNode):
            self._rewrite_pipeline_tree_node(tree)
            pipeline_node = tree.node
            assert isinstance(pipeline_node, pandas_nodes.PandasFeatureViewPipelineNode)

            # Compute results of pipeline node, register as temp table, and replace the tree with a staged table scan
            # node
            pipeline_result_df = pipeline_node.to_dataframe()
            staging_table_name = f"{pipeline_node.feature_definition_wrapper.name}_{id(pipeline_node)}_pandas"
            tree.node = nodes.StagedTableScanNode(
                staged_columns=pipeline_node.columns,
                staging_table_name=staging_table_name,
            )
            query_tree_compute.register_temp_table_from_pandas(staging_table_name, pipeline_result_df)
        else:
            for i in tree.inputs:
                self._rewrite_init(tree=i, query_tree_compute=query_tree_compute)

    def _rewrite_pipeline_tree_node(self, tree: NodeRef) -> NodeRef:
        tree_node = tree.node
        is_fv_pipeline_node = isinstance(tree_node, nodes.FeatureViewPipelineNode)
        if len(tree.inputs) > 1 and not is_fv_pipeline_node:
            msg = f"Unexpected node count {[node_ref.node.__class__ for node_ref in tree.inputs]}"
            raise Exception(msg)
        input_node = None
        if len(tree.inputs) == 1:
            input_node = self._rewrite_pipeline_tree_node(tree=tree.inputs[0]).node
        elif is_fv_pipeline_node:
            for _, fv_input_node_ref in tree_node.inputs_map.items():
                input_node_class = fv_input_node_ref.node.__class__
                if input_node_class in self.node_mapping:
                    self._rewrite_pipeline_tree_node(fv_input_node_ref)
        node_class = tree_node.__class__
        if node_class in self.node_mapping:
            tree.node = self.node_mapping[node_class].from_node_inputs(query_node=tree_node, input_node=input_node)
        else:
            msg = f"Unexpected Pandas node: {node_class.__name__}"
            raise Exception(msg)

        return tree
