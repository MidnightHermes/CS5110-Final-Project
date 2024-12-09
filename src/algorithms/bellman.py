import networkx as nx
from networkx.classes.function import get_edge_attributes

class NegativeCycleException(Exception):
    @staticmethod
    def build_cycle(u, v, preds):
        preds[v] = u

        visited = {k: False for k in preds.keys()}
        visited[v] = True

        while not visited[u]:
            visited[u] = True
            u = preds[u]

        cycle = [u]
        v = preds[u]
        while v != u:
            cycle.append(v)
            v = preds[v]

        cycle.reverse()

        return tuple(cycle)


    def __init__(self, u, v, preds):
        self._cycle = NegativeCycleException.build_cycle(u, v, preds)

        super().__init__(f"Negative cycle composed of {self._cycle}")

    @property
    def cycle(self):
        return self._cycle
    
    @property
    def edges(self):
        cyc = self.cycle
        mod = len(cyc)
        return [(cyc[i], cyc[(i + 1) % mod]) for i in range(mod)]

def bellman_ford(g, source):
    """
    Computes all the shortest paths in a directed weighted graph with negative edge weights
    (but not negative cycles) between every node and some source node s.
    :param g: the graph to perform the algorithm on
    :param source: the source node to query in g
    :return: None if a negative cycle exists. Otherwise returns a pair of dictionaries containing (1) the distances of each node from source (2) the predecessors of each node u in the shortest path from source to u.
    """

    n = g.number_of_nodes()
    edges = g.edges

    all_weights = get_edge_attributes(g, 'weight').values()
    inf = sum(map(abs, all_weights)) + 1

    # assign impossibly large number to be "infinity"

    distance = {v: inf * 2 for v in g.nodes}
    predecessor = {v: None for v in g.nodes}

    distance[source] = 0

    for _ in range(n - 1):
        for (u, v) in edges:
            w = edges[u, v]['weight']
            relax = distance[u] + w

            # If True, a new shortest path has been discovered
            if relax < inf and relax < distance[v]:
                distance[v] = distance[u] + w
                predecessor[v] = u

    # Detect negative cycle
    for (u, v) in edges:
        w = edges[u, v]['weight']
        if distance[u] + w < distance[v] and distance[v] < inf:
            raise NegativeCycleException(u, v, predecessor)

    return distance, predecessor

if __name__ == '__main__':
    from random_graph import RandomGraphBuilder
    from visualize_runtime import measure_runtime, plot_results

    import random

    def graph_gen_function(nodes, nedges):
        max_edges = (nodes * (nodes - 1)) / 2
        edge_density = nedges / max_edges

        return RandomGraphBuilder().nodes(nodes).strongly_connected(False).random_edges(edge_density).connected().weighted(range(-1, 50)).build()
    
    runtime_function = lambda n, m: n * m

    algorithm = lambda g: bellman_ford(g, random.choice(sorted(g.nodes())))

    count = 0
    while True:
        MAX_ATTEMPTS = 50
        if count > MAX_ATTEMPTS:
            raise Exception(f"Failed to generate a valid graph after {MAX_ATTEMPTS} attempts")
        count += 1

        results = measure_runtime(algorithm, graph_gen_function, runtime_function)
        print(results)
        break

    plot_results(results, 'Bellman-Ford', \
                 expected_runtime="Expected Runtime: $O(|V||E|)$", \
                 line_color="#13ff50"\
                )
