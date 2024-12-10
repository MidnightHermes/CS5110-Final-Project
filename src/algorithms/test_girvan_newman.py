import unittest
import networkx as nx
import random
import time
import matplotlib.pyplot as plt

from girvan_newman import girvan_newman, betweenness
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


class TestGirvanNewmanBetweenness(unittest.TestCase):
    def test_actual_solution(self):
        # Test our algorithm against built-in networkx function
        self.graph = randG().nodes(random.randint(10, 20)).random_edges(0.5).build()

        actual = nx.edge_betweenness_centrality(self.graph.copy())
        expected = betweenness(self.graph.copy())

        print(actual, '\n\n', expected, '\n\n')

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

            avg_runtimes = []
            for _ in range(10):
                start_time = time.time()
                girvan_newman(G)
                avg_runtimes.append(time.time() - start_time)
            runtimes.append(sum(avg_runtimes) / len(avg_runtimes))

            # Girvan-Newman should have a runtime of VE**2 for unweighted graphs
            expected_runtime = (n * num_edges**2) / 1e20
            expected_times.append(expected_runtime)

        for actual, expected in zip(runtimes, expected_times):
            self.assertLess(expected - actual, TOL)

        plt.figure(figsize=(6, 4), facecolor="#16242f")
        ax = plt.axes()
        ax.set_facecolor("#16242f")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_color('white')
        ax.spines['left'].set_color('white')
        ax.xaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='y', colors='white')

        line_color = "#b9d4b4"
        # Plot measured runtimes
        plt.plot(node_counts, runtimes, label=f"Measured Runtime", color=line_color)
        # Plot expected runtimes
        plt.plot(node_counts, expected_times, linestyle="dotted", label="Expected Runtime: $O(|E| \cdot |V|^2)$", color=line_color)

        plt.xlabel("Number of Vertices ($V$)")
        plt.ylabel("Execution Time (seconds)")
        plt.title(f"Time Complexity of Girvan-Newman", color="white")
        plt.legend(facecolor="#16242f", labelcolor='linecolor')
        plt.xlim(10, 1000)
        plt.ylim(0, 0.1e-5)
        plt.xticks(node_counts[::2])
        plt.savefig(f"src/algorithms/girvan_newman_time_complexity.png")
        # plt.show()


if __name__ == "__main__":
    unittest.main()
