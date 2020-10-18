import community as community_louvain
import pandas as pd
import networkx as nx
from typing import List, Tuple


class DeepPartitionNode(object):
    def __init__(self,
                 index: int,
                 partition_index: int,
                 subset_index: pd.DataFrame,
                 leaf_indexes: List[Tuple[int, pd.Index]],
                 depth: int):
        self.index = index
        self.partition_index = partition_index
        self.subset_index = subset_index
        self.leaf_indexes = leaf_indexes
        self.depth = depth


class DeepPartition(object):
    def __init__(self,
                 nodes_df: pd.DataFrame,
                 node_column: str,
                 edges_df: pd.DataFrame,
                 edge_columns: List[str]) -> None:
        self.nodes_df = nodes_df
        self.node_column = node_column
        self.edges_df = edges_df
        self.edge_columns = edge_columns

        self.nodes = {}
        self.node_index = 0
        self.add_node(index=self.node_index,
                      partition_index=0,
                      subset_index=self.nodes_df.index,
                      leaf_indexes=self.partition_indexes(indexes=None),
                      depth=0)

    def add_node(self,
                 index: int,
                 partition_index: int,
                 subset_index: pd.DataFrame,
                 leaf_indexes: List[Tuple[int, pd.Index]],
                 depth: int):
        if depth not in self.nodes.keys():
            self.nodes[depth] = []

        self.nodes[depth].append(DeepPartitionNode(index=index,
                                                   partition_index=partition_index,
                                                   subset_index=subset_index,
                                                   leaf_indexes=leaf_indexes,
                                                   depth=depth))

    def partition(self, depth: int):
        for step in range(1, depth + 1):
            for node in self.nodes[step - 1]:
                for part, index in node.leaf_indexes:
                    self.node_index += 1
                    self.add_node(index=self.node_index,
                                  partition_index=part,
                                  subset_index=index,
                                  leaf_indexes=self.partition_indexes(indexes=index),
                                  depth=step)

    def to_pandas(self, depth: int = None) -> pd.DataFrame:
        if not depth:
            nodes = []
            for node in self.nodes.values():
                nodes += node
        else:
            nodes = self.nodes[depth]

        df = self.nodes_df.copy()
        for node in nodes:
            df.loc[df.index.isin(node.subset_index), 'partition_{}'.format(node.depth)] = node.partition_index

        return df

    def partition_indexes(self, indexes: pd.Index = None) -> List[Tuple[int, pd.Index]]:
        if indexes is None:
            subset_nodes = self.nodes_df.copy()
            subset_edges = self.edges_df.copy()
        else:
            subset_nodes = self.nodes_df[self.nodes_df.index.isin(indexes)].copy()
            statement = True
            for edge_column in self.edge_columns:
                statement &= self.edges_df[edge_column].isin(subset_nodes[self.node_column])
            subset_edges = self.edges_df[statement].copy()

        graph = nx.Graph()
        graph.add_nodes_from(subset_nodes[self.node_column].values)
        graph.add_edges_from([(e0, e1) for e0, e1 in subset_edges[self.edge_columns].values])

        partition = community_louvain.best_partition(graph)
        subset_nodes['partition'] = partition.values()
        return [(part, subset_nodes[subset_nodes['partition'] == part].index)
                for part in subset_nodes['partition'].drop_duplicates()]
