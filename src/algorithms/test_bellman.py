import unittest
import networkx as nx

from bellman import bellman_ford

class TestWikipediaExample(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = nx.DiGraph()

        cls.graph.add_nodes_from(['s', 't', 'x', 'y', 'z'])
        cls.graph.add_edge('s', 't', weight=6)
        cls.graph.add_edge('s', 'y', weight=7)
        cls.graph.add_edge('t', 'y', weight=8)
        cls.graph.add_edge('t', 'x', weight=5)
        cls.graph.add_edge('t', 'z', weight=-4)
        cls.graph.add_edge('y', 'x', weight=-3)
        cls.graph.add_edge('y', 'z', weight=9)
        cls.graph.add_edge('x', 't', weight=-2)
        cls.graph.add_edge('z', 'x', weight=7)

        cls.distance, cls.predecessor = bellman_ford(cls.graph, 's')

    def check_dist(self, node, exp):
        self.assertEqual(self.distance[node], exp)

    def test_distances(self):
        self.check_dist('s', 0)
        self.check_dist('t', 2)
        self.check_dist('y', 7)
        self.check_dist('z', -2)
        self.check_dist('x', 4)

    def check_pred(self, node, exp):
        self.assertEqual(self.predecessor[node], exp)

    def test_predecessors(self):
        self.check_pred('s', None)
        self.check_pred('x', 'y')
        self.check_pred('t', 'x')
        self.check_pred('y', 's')
        self.check_pred('z', 't')

if __name__ == '__main__':
    unittest.main()
