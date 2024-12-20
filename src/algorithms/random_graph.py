import functools
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

class transform:
    def __init__(self, f):
        self.f = f
        self.name = f.__name__

    def __get__(self, obj, type=None):
        if obj is None:
            return self.f

        def newfunc(inst, *args, **kwargs):
            return inst._next(lambda g: self.f(g, *args, **kwargs))
        return functools.partial(newfunc, obj)


class RandomGraphBuilder:
    def __init__(self, directed=False):
        self._init = nx.DiGraph if directed else nx.Graph

        self._directed = directed

        self._num_nodes = 0

        self._transforms = []

    def __copy__(self):
        new_builder = RandomGraphBuilder()

        new_builder._init = self._init
        new_builder._directed = self._directed
        new_builder._num_nodes = self._num_nodes
        new_builder._transforms = self._transforms.copy()

        return new_builder
    
    def _next(self, f):
        new_builder = self.__copy__()

        new_builder._transforms.append(f)

        return new_builder

    def nodes(self, n):
        new_builder = self.__copy__()
        new_builder._num_nodes = n

        return new_builder

    @transform
    def random_edges(g, p, backwards_edges=True):
        edges_left = (e for e in _edge_gen(g.nodes, g.is_directed()) if e not in g.edges)
        for e in edges_left:
            erev = tuple(reversed(e))
            allow_insertion = backwards_edges or erev not in g.edges
            if allow_insertion and random.random() < p:
                g.add_edge(*e)

        return g

    def build(self):
        g = self._init()

        g.add_nodes_from(range(self._num_nodes))

        for f in self._transforms:
            g = f(g)

        return g

    @property
    def directed(self):
        return self._directed
    
    def directed(self, will_be_directed=True):
        new_builder = self.__copy__()

        if will_be_directed:
            new_builder._init = nx.DiGraph
            new_builder._directed = True
        else:
            new_builder._init = nx.Graph
            new_builder._directed = False

        return new_builder
    
    def undirected(self, will_be_undirected=True):
        return self.directed(not will_be_undirected)

    @transform
    def complete(g):
        g.add_edges_from(_edge_gen(g.nodes, g.is_directed()))

        return g
    
    @transform
    def clique(g, size, add_new_nodes):
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
    
    @transform
    def connected(g):
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
    
    @transform
    def strongly_connected(g, backwards_edges=True):
        if g.number_of_nodes() == 2:
            backwards_edges = True

        global_time = -1
        start_time = {n: -1 for n in g.nodes}
        time_node_map = dict()
        low = dict()

        if len(g.edges) > 0:
            raise ValueError('Cannot construct strongly connected graph with edges already existing')
        
        start = RandomGraphBuilder.spanning_tree(g, True)

        # Custom DFS for identifying SCCs and connecting them
        def _dfs(g, node):
            nonlocal start_time
            nonlocal global_time
            nonlocal time_node_map
            nonlocal low

            global_time += 1
            start_time[node] = global_time
            time_node_map[global_time] = node
            low[node] = global_time

            for v in g.adj[node]:
                if start_time[v] == -1:
                    _dfs(g, v)

                    low[node] = min(low[node], low[v])

                low[node] = min(low[node], start_time[v])

            if low[node] > 0 and low[node] == start_time[node]:
                x_choices = list(range(start_time[node], global_time + 1))
                
                y = None
                while y is None:
                    if len(x_choices) == 0:
                        raise ValueError("cannot make this graph strongly connected with no backwards edges")

                    x = random.choice(x_choices)
                    x_choices.remove(x)

                    y_choices = [y for y in range(0, start_time[node]) if backwards_edges or (time_node_map[x], time_node_map[y]) not in g.edges]

                    if len(y_choices) > 0:
                        y = random.choice(y_choices)

                u = time_node_map[x]
                v = time_node_map[y]

                g.add_edge(u, v)

                low[node] = y

        _dfs(g, start)

        return g
    
    @transform
    def spanning_tree(g, return_start=False):
        # TODO: make return_start a kwarg so it's not user-facing

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
    
    @transform
    def weighted(g, weight_range):
        for e in g.edges:
            g.edges[e]['weight'] = random.choice(weight_range)

        return g
    
    @transform
    def cycle(g, length, add_new_nodes=False, negative_weight=False):
        if add_new_nodes:
            last_node = g.number_of_nodes()
            new_nodes = range(last_node, last_node + length)

            g.add_nodes_from(new_nodes)

            nodes = list(new_nodes)
        else:
            nodes = random.sample(list(g.nodes), length)

        for i in range(len(nodes)):
            j = (i + 1) % len(nodes)

            g.add_edge(nodes[i], nodes[j])

            if negative_weight:
                g.edges[nodes[i], nodes[j]]['weight'] = -1

        return g
    
    @transform
    def shuffle_nodes(g):
        domain = list(g.nodes)

        codomain = list(g.nodes)
        random.shuffle(codomain)

        mapping = {x: y for (x, y) in zip(domain, codomain)}

        return nx.relabel_nodes(g, mapping)
    
    @transform
    def remove_negative_cycles(g):
        from bellman import bellman_ford, NegativeCycleException

        has_negative_cycle = True
        while has_negative_cycle:
            try:
                for v in g.nodes():
                    bellman_ford(g, v)

                has_negative_cycle = False
            except NegativeCycleException as nce:
                edges = nce.edges

                cycle_weight = sum(g.edges[e]['weight'] for e in edges)

                nonneg_edges = list(filter(lambda e: g.edges[e]['weight'] >= 0, edges))

                # would rather make a positive edge bigger than make a negative edge non-negative
                if len(nonneg_edges) > 0:
                    choice = random.choice(nonneg_edges)
                else:
                    choice = random.choice(edges)
                g.edges[choice]['weight'] += -cycle_weight

        return g
