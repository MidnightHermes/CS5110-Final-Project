import unittest
import networkx as nx
import random
import time
import numpy as np

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


class TestGirvanNewmanRuntime(unittest.TestCase):
    def test_runtime(self):
        TOL = 0.25
        node_counts = range(10, 1000, 50)
        runtimes = []
        expected_times = []
        for n in node_counts:
            max_edges = n * (n - 1)
            G = randG().nodes(n).random_edges(0.5).build()
            num_edges = len(G.edges())

            start_time = time.time()
            girvan_newman(G)
            runtimes.append(time.time() - start_time)

            # Girvan-Newman should have a runtime of EV**2 for unweighted graphs
            expected_runtime = (num_edges * n**2) / 1e12
            expected_times.append(expected_runtime)

        for actual, expected in zip(runtimes, expected_times):
            self.assertLess(expected - actual, TOL)


if __name__ == "__main__":
    unittest.main()
