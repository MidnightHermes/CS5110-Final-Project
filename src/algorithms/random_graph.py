import itertools
import networkx as nx
import random


DEFAULT_SEED = 10

def _edge_gen(n, directed):
    f = itertools.permutations if directed else itertools.combinations

    return f(range(n), 2)

def _adjust_probability(p, n, m, directed):
    m_total = n * (n - 1)
    if directed:
        m_total /= 2

    if m == m_total:
        return 1.0

    assert(m < m_total)

    m_expected = m_total * p
    
    edges_left = m_total - m

    return (m_expected - m) / edges_left


def _finish_random_graph(g, p):
    already_existing_edges = g.edges

    n = g.number_of_nodes()
    m = len(already_existing_edges)

    directed = isinstance(g, nx.DiGraph)

    p = _adjust_probability(p, n, m, directed)
    
    edges_left = (e for e in _edge_gen(n, directed) if e not in already_existing_edges)
    for e in edges_left:
        if random.random() < p:
            g.add_edge(*e)

    return g

def complete_graph(n, directed):
    g = nx.DiGraph() if directed else nx.Graph()

    for e in _edge_gen(n, directed):
        g.add_edge(*e)

    return g

def with_clique(n, clique_size, p):
    g = complete_graph(clique_size, False)

    g.add_nodes_from(range(clique_size, n))
    return _finish_random_graph(g, p)

class RandomGraph:
    # TODO: Create different graph generation methods and pass type of graph as parameter
    def __init__(self, directed=False, seed=DEFAULT_SEED):
        self.graph = self.gen_random_complete_connected_weighted_graph(directed=directed, seed=seed)

    def gen_random_complete_connected_weighted_graph(self, directed: bool, seed: int):
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
            G.edges[edge]['weight'] = random.randint(1, seed)  # Assign random weights between 1 and 10
        return G
