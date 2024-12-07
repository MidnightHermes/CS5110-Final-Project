import unittest
import networkx as nx
import random

from girvan_newman import girvan_newman
from random_graph import RandomGraphBuilder as randG


class TestGirvanNewmanAlgorithm(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Generate a random graph
        cls.graph = randG().nodes(random.randint(10, 20)).random_edges(0.5).build()
        
        # then apply the Girvan-Newman algorithm to it
        cls.out = girvan_newman(cls.graph)
    
    def test_actual_solution(self):
        # Test our algorithm against built-in networkx function
        actual = next(nx.community.girvan_newman(self.graph))
        expected = next(self.out)

        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
