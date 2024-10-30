import networkx as nx
import random


DEFAULT_SEED = 10


class RandomGraph:
    # TODO: Create different graph generation methods and pass type of graph as parameter
    def __init__(self, directed=False, seed=DEFAULT_SEED):
        self.graph = self.gen_random_complete_connected_weighted_graph(directed=directed, seed=seed)

    def gen_random_complete_connected_weighted_graph(self, directed: bool, seed: int) -> nx.Graph | nx.DiGraph:
        # We assume a graph with less than 3 nodes is trivial so we ensure the seed is at least 3
        if seed < 3:
            seed = 3
        # For a connected graph, the number of edges must be at least the number of
        #   vertices minus 1
        # For a complete graph, given a number of vertices, the number of edges is
        #   n(n-1) (divided by 2 for undirected graphs)
        num_nodes = random.randint(3, seed)

        max_edges = num_nodes * (num_nodes - 1) // 2 if not directed else num_nodes * (num_nodes - 1)
        min_edges = num_nodes - 1
        num_edges = random.randint(min_edges, max_edges)

        G = nx.gnm_random_graph(num_nodes, num_edges, directed=directed)
        for edge in G.edges():
            G.edges[*edge]['weight'] = random.randint(1, seed)  # Assign random weights between 1 and 10
        return G
