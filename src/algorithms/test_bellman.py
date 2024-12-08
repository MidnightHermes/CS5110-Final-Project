import unittest
import networkx as nx

from bellman import NegativeCycleException, bellman_ford
from random_graph import RandomGraphBuilder

def add_weighted_edges(g, edges):
    """
    Take a graph and a list of triples representing weighted edges to
    quickly add edges to a graph.
    :param g: the graph we are adding edges to
    :param edges: the list of edge triples
    """
    for u, v, w in edges:
        g.add_edge(u, v, weight=w)

class Cycle:
    """
    Represents cycles so they can be tested for equivalence even if their
    tuples start in different places
    """
    @staticmethod
    def _succs(tup):
        """
        Generates every pair consisting of a node and its successor in a cycle
        """
        for i in range(len(tup)):
            yield tup[i], tup[(i + 1) % len(tup)]

    def __init__(self, cycle):
        self._successors = {u: v for u, v in Cycle._succs(cycle)}

    def __eq__(self, value):
        if not isinstance(value, Cycle):
            return False
        
        return self._successors == value._successors


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

class TestNegativeCycles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.twoCycle = nx.DiGraph()
        cls.twoCycle.add_nodes_from([0, 1])

        add_weighted_edges(cls.twoCycle, [(0, 1, 7),
                                          (1, 0, -8)])

        cls.nonTrivialCycle = nx.DiGraph()
        cls.nonTrivialCycle.add_nodes_from(range(6))

        add_weighted_edges(cls.nonTrivialCycle, [(1, 0, 3),
                                                 (2, 1, -5),
                                                 (0, 2, 4),
                                                 (1, 5, -17),
                                                 (5, 2, 30),
                                                 (5, 4, 2),
                                                 (4, 3, 16),
                                                 (3, 2, 3)])
        
        cls.nonSourceCycle = nx.DiGraph()
        cls.nonSourceCycle.add_nodes_from(range(8))

        add_weighted_edges(cls.nonSourceCycle, [(0, 1, -3),
                                                (0, 7, 3),
                                                (1, 2, 4),
                                                (1, 6, -5),
                                                (2, 3, -5),
                                                (2, 6, 3),
                                                (3, 0, 1),
                                                (4, 0, 8),
                                                (4, 5, 1),
                                                (4, 2, 7),
                                                (5, 1, 1),
                                                (6, 1, 6),
                                                (7, 3, -2)])
        
        cls.nonConnectedCycle = RandomGraphBuilder().nodes(10).directed().strongly_connected(False).weighted(range(1, 100)).cycle(3, True, True).build()

    def checkCycle(self, g, s, cycle):
        self.assertRaises(NegativeCycleException, bellman_ford, g, s)

        try:
            bellman_ford(g, s)
            self.assertTrue(False)
        except NegativeCycleException as e:
            c1 = Cycle(e.cycle)
            c2 = Cycle(cycle)
            self.assertEqual(c1, c2)
        except:
            self.assertTrue(False)

    def test_twoCycle(self):
        self.checkCycle(self.twoCycle, 0, (0, 1))
    
    def test_nonTrivialCycle(self):
        self.checkCycle(self.nonTrivialCycle, 1, (1, 5, 4, 3, 2))

    def test_nonSourceCycle(self):
        self.checkCycle(self.nonSourceCycle, 4, (0, 1, 2, 3))

    def test_nonConnectedCycle(self):
        # shouldn't raise an exception
        bellman_ford(self.nonConnectedCycle, 0)

        # should raise exception
        self.assertRaises(NegativeCycleException, bellman_ford, self.nonConnectedCycle, 11)

if __name__ == '__main__':
    unittest.main()
