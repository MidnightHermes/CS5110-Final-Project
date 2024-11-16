import unittest
import networkx as nx

from bellman import NegativeCycleException, bellman_ford

class Cycle:
    @staticmethod
    def _succs(tup):
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

        cls.twoCycle.add_edge(0, 1, weight=7)
        cls.twoCycle.add_edge(1, 0, weight=-8)

        cls.nonTrivialCycle = nx.DiGraph()
        cls.nonTrivialCycle.add_nodes_from(range(6))

        cls.nonTrivialCycle.add_edge(1, 0, weight=3)
        cls.nonTrivialCycle.add_edge(2, 1, weight=-5)
        cls.nonTrivialCycle.add_edge(0, 2, weight=4)
        cls.nonTrivialCycle.add_edge(1, 5, weight=-17)
        cls.nonTrivialCycle.add_edge(5, 2, weight=30)
        cls.nonTrivialCycle.add_edge(5, 4, weight=2)
        cls.nonTrivialCycle.add_edge(4, 3, weight=16)
        cls.nonTrivialCycle.add_edge(3, 2, weight=3)

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
    
    def testNonTrivialCycle(self):
        self.checkCycle(self.nonTrivialCycle, 1, (1, 5, 4, 3, 2))

if __name__ == '__main__':
    unittest.main()
