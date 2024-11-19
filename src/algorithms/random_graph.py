import itertools
import networkx as nx
import random


def _edge_gen(nodes, directed):
    f = itertools.permutations if directed else itertools.combinations

    return f(nodes, 2)

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

def _connected_components(g):
    g = g.copy().to_undirected()

    components = []

    while g.number_of_nodes() > 0:
        u = random.choice(list(g.nodes))

        cc = _scour(g, u)
        components.append(cc)
        g.remove_nodes_from(cc)

    return components


class RandomGraphBuilder:
    def __init__(self, directed=False):
        self._init = nx.DiGraph if directed else nx.Graph

        self._directed = directed

        self._nodes = 0

        self._transforms = []

    def __copy__(self):
        new_builder = RandomGraphBuilder()

        new_builder._init = self._init
        new_builder._directed = self._directed
        new_builder._nodes = self._nodes
        new_builder._transforms = self._transforms.copy()

        return new_builder
    
    def _next(self, f):
        new_builder = self.__copy__()

        new_builder._transforms.append(f)

        return new_builder

    def nodes(self, n):
        new_builder = self.__copy__()
        new_builder._nodes = n

        return new_builder

    def random_edges(self, p):
        def _random_edges(g, p):
            edges_left = (e for e in _edge_gen(g.nodes, g.is_directed()) if e not in g.edges)
            for e in edges_left:
                if random.random() < p:
                    g.add_edge(*e)

            return g
        
        return self._next(lambda g: _random_edges(g, p))

    def build(self):
        g = self._init()

        g.add_nodes_from(range(self._nodes))

        for f in self._transforms:
            g = f(g)

        return g

    @property
    def directed(self):
        return self._directed
    
    def directed(self, will_be_directed):
        new_builder = self.__copy__()

        if will_be_directed:
            new_builder._init = nx.DiGraph
            new_builder._directed = True
        else:
            new_builder._init = nx.Graph
            new_builder._directed = False

        return new_builder

    def complete(self):
        def _complete(g):
            g.add_edges_from(_edge_gen(g.nodes, g.is_directed()))

            return g
        
        return self._next(_complete)

    def clique(self, size, add_new_nodes=False):
        def _clique(g, size, add_new_nodes):
            n = g.number_of_nodes()

            if not add_new_nodes and size > n:
                raise ValueError("Tried to build clique larger than the graph")
            
            if add_new_nodes:
                new_nodes = range(n, n + size)

                g.add_nodes_from(new_nodes)

                subset = new_nodes
            else:
                subset = random.sample(list(g.nodes), size)

            g.add_edges_from(_edge_gen(subset, g.is_directed()))

            return g
        
        return self._next(lambda g: _clique(g, size, add_new_nodes))
    
    def connected(self):
        def _connected(g):
            if g.number_of_nodes() == 0:
                return g

            ccs =_connected_components(g)

            if len(ccs) == 1:
                return g
            
            while len(ccs) > 1:
                c1, c2 = random.sample(ccs, 2)

                ccs.remove(c1)
                ccs.remove(c2)

                n1 = random.choice(list(c1))
                n2 = random.choice(list(c2))

                g.add_edge(n1, n2)

                c1 |= c2

                ccs.append(c1)

            return g
        
        return self._next(_connected)
    
    @staticmethod
    def _spanning_tree(g, return_start=False):
        if g.number_of_nodes == 0:
            raise ValueError('Cannot make spanning tree with zero nodes')
        
        start = random.choice(sorted(g.nodes))
        connected = {start}

        disconnected = set(g.nodes)
        disconnected.remove(start)

        while len(disconnected) > 0:
            v = random.choice(sorted(disconnected))
            disconnected.remove(v)

            u = random.choice(sorted(connected))

            g.add_edge(u, v)

            connected.add(v)

        if return_start:
            return start
        else:
            return g
    
    def spanning_tree(self):
        return self._next(RandomGraphBuilder._spanning_tree)
    
    def weighted(self, weight_range):
        def _weighted(g, weight_range):
            for e in g.edges:
                g.edges[e]['weight'] = random.choice(weight_range)

            return g
        
        return self._next(lambda g: _weighted(g, weight_range))

    def cycle(self, length, negative_weight=False):
        def _cycle(g, length, negative_weight):
            nodes = random.sample(list(g.nodes), length)

            for i in range(len(nodes)):
                j = (i + 1) % len(nodes)

                g.add_edge(nodes[i], nodes[j])

                if negative_weight:
                    g.edges[nodes[i], nodes[j]]['weight'] = -1

            return g
        
        return self._next(lambda g: _cycle(g, length, negative_weight))
