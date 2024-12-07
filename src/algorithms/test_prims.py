import unittest
import networkx as nx

from prims import prims
from random_graph import RandomGraphBuilder as randG


class TestPrimsAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate a random complete connected weighted graph
        cls.graph = randG().nodes(10).complete().connected().weighted(range(1, 10)).build()
        
        # then apply Prim's algorithm to it
        cls.mst = prims(cls.graph)

    def test_is_valid_tree(self):
        # Check if the MST is a valid spanning tree
        self.assertTrue(nx.is_tree(self.mst), "The result is not a valid tree")
        
    def test_spans_all_nodes(self):
        # Check if the MST has the same number of Nodes as the original graph
        self.assertEqual(len(self.mst.nodes), len(self.graph.nodes), "The MST does not span all nodes")
        
    def test_correct_number_of_edges(self):
        # Check if the MST has the minimum number of edges based on the number of Nodes
        self.assertEqual(len(self.mst.edges), len(self.graph.nodes) - 1, "The MST does not have the correct number of edges")

    def test_all_edges_in_mst_are_in_original_graph(self):
        # Check if all edges in the MST are present in the original graph
        for origin, link, data in self.mst.edges(data=True):
            self.assertTrue(
                (link, origin, data) in list(self.graph.edges(data=True)) or 
                (origin, link, data) in list(self.graph.edges(data=True)), 
                "An edge in the MST is not in the original graph"
            )

    def test_mst_is_connected(self):
        # Check if the MST is connected
        self.assertTrue(nx.is_connected(self.mst), "The MST is not connected")

    def test_mst_has_minimum_weight(self):
        # Check if the MST has the minimum total weight

        # Sum all weights in the MST
        mst_weight = sum(data['weight'] for origin, link, data in self.mst.edges(data=True))
        # Generate the minimum spanning tree using NetworkX's built-in function
        nx_mst = nx.minimum_spanning_tree(self.graph)
        # and sum all weights in that MST
        min_weight = sum(data['weight'] for origin, link, data in nx_mst.edges(data=True))
        # then compare them
        self.assertEqual(mst_weight, min_weight, "The MST does not have the minimum possible weight")


if __name__ == "__main__":
    unittest.main()
