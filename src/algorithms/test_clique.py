import unittest
import random

from max_clique import ramsey
from random_graph import RandomGraphBuilder

class TestCorrectness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        num_nodes = random.randint(50, 100)
        clique_size = random.randint(20, (4 * num_nodes) // 5)
        desired_num_edges = random.random()
        cls.graph = RandomGraphBuilder().nodes(num_nodes).clique(clique_size, False).random_edges(desired_num_edges, False).build()

        clique, independent = ramsey(cls.graph)

        cls.clique = clique
        cls.independent = independent

    def test_clique_is_clique(self):
        '''Tests if the clique found by ramsey is actually a clique'''
        for u in self.clique:
            others = self.clique - {u}

            for v in others:
                self.assertTrue((u,v) in self.graph.edges())

    def test_independent_is_independent(self):
        '''Tests if the independent set found by ramsey is actually an independent set'''
        for u in self.independent:
            others = self.independent - {u}

            for v in others:
                self.assertTrue((u, v) not in self.graph.edges())

if __name__ == '__main__':
    unittest.main()