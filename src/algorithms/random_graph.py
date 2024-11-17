import itertools
import networkx as nx
import random


DEFAULT_SEED = 10

class RandomGraphBuilder:
    def __init__(self, n, directed=False):
        self._graph = nx.DiGraph() if directed else nx.Graph()

        self._graph.add_nodes_from(range(n))

    def random_edges(self, p):
        edges_left = (e for e in self._edge_gen() if e not in self._graph.edges)
        for e in edges_left:
            if random.random() < p:
                self._graph.add_edge(*e)

        return self        

    @staticmethod
    def _adjust_probability(p, n, m, directed):
        m_total = n * (n - 1)
        if directed:
            m_total /= 2

        if m == m_total:
            return 1.0

        assert(m < m_total)

        m_expected = m_total * p
        
        edges_left = m_total - m

        if m_expected - m < 0:
            raise ValueError("Current edge density exceeds desired edge density")

        return (m_expected - m) / edges_left

    def finalize(self):
        already_existing_edges = self._graph.edges

        n = self._graph.number_of_nodes()
        m = len(already_existing_edges)

        p = RandomGraphBuilder._adjust_probability(self._p, n, m, self.directed)
        
        edges_left = (e for e in self._edge_gen() if e not in already_existing_edges)
        for e in edges_left:
            if random.random() < p:
                self._graph.add_edge(*e)

        return self

    def build(self):
        return self._graph

    @property
    def directed(self):
        return self._graph.is_directed()
    
    def directed(self, will_be_directed):
        if will_be_directed:
            self._graph = self._graph.to_directed()
        else:
            self._graph = self._graph.to_undirected()

        return self
        
    def _edge_gen(self, subset=None):
        if subset is None:
            subset = self._graph.nodes

        f = itertools.permutations if self.directed else itertools.combinations

        return f(subset, 2)

    def complete(self):
        self._graph.add_edges_from(self._edge_gen())

        return self

    def clique(self, size, add_new_nodes=False):
        n = self._graph.number_of_nodes()

        if not add_new_nodes and size > n:
            raise ValueError("Tried to build clique large than the graph")
        
        if add_new_nodes:
            new_nodes = range(n, n + size)

            self._graph.add_nodes_from(new_nodes)

            subset = new_nodes
        else:
            subset = random.sample(list(self._graph.nodes), size)

        self._graph.add_edges_from(self._edge_gen(subset=subset))

        return self
    
    @staticmethod
    def _scour(g, node):
        visited = set()

        stack = [node]

        while len(stack) > 0:
            u = stack.pop()

            if u in visited:
                continue

            visited.add(u)

            stack.extend(g.adj[u])

        return visited
    
    def _connected_components(self, strongly=False):
        g = self._graph.copy()

        if not strongly:
            g = g.to_undirected()

        components = []

        while g.number_of_nodes() > 0:
            u = random.choice(list(g.nodes))

            cc = RandomGraphBuilder._scour(g, u)
            components.append(cc)
            g.remove_nodes_from(cc)

        return components
    
    def connected(self):
        if self._graph.number_of_nodes() == 0:
            return self

        ccs = self._connected_components()

        if len(ccs) == 1:
            return self
        
        while len(ccs) > 1:
            c1, c2 = random.sample(ccs, 2)

            ccs.remove(c1)
            ccs.remove(c2)

            n1 = random.choice(list(c1))
            n2 = random.choice(list(c2))

            self._graph.add_edge(n1, n2)

            c1.union(c2)

            ccs.append(c1)

        return self
    
    def weighted(self, weight_range):
        for e in self._graph.edges:
            if 'weight' not in self._graph.edges[e].keys():
                self._graph.edges[e]['weight'] = random.choice(weight_range)

        return self

    def cycle(self, length, negative_weight=False):
        nodes = random.sample(list(self._graph.nodes), length)

        for i in range(len(nodes)):
            j = (i + 1) % len(nodes)

            self._graph.add_edge(nodes[i], nodes[j])

            if negative_weight:
                self._graph.edges[nodes[i], nodes[j]]['weight'] = -1

        return self


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
        for edge in G.edges:
            G.edges[edge]['weight'] = random.randint(1, seed)  # Assign random weights between 1 and 10
        return G
