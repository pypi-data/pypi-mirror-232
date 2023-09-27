from abc import ABC
from abc import abstractmethod
from typing import Type

from tecton_core.query.executor_params import QueryTreeStep
from tecton_core.query.node_interface import NodeRef
from tecton_core.query.node_interface import QueryNode
from tecton_core.query.query_tree_compute import QueryTreeCompute


class Rewrite(ABC):
    @abstractmethod
    def rewrite(self, node: NodeRef) -> None:
        raise NotImplementedError


class QueryTreeRewriter(ABC):
    @abstractmethod
    def rewrite(self, tree: NodeRef, query_tree_step: QueryTreeStep, query_tree_compute: QueryTreeCompute) -> None:
        raise NotImplementedError


def tree_contains(tree: NodeRef, node_type: Type[QueryNode]) -> bool:
    """Returns True if the tree contains a NodeRef of the given type, False otherwise."""
    if isinstance(tree.node, node_type):
        return True

    return any(tree_contains(subtree, node_type) for subtree in tree.inputs)
