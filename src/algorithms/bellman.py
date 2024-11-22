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

    distance = {v: inf * 2 for v in g.nodes}
    predecessor = {v: None for v in g.nodes}

    distance[source] = 0

    for _ in range(n - 1):
        for (u, v) in edges:
            w = edges[u, v]['weight']
            relax = distance[u] + w
            if relax < inf and relax < distance[v]:
                distance[v] = distance[u] + w
                predecessor[v] = u

    for (u, v) in edges:
        w = edges[u, v]['weight']
        if distance[u] + w < distance[v]:
            raise NegativeCycleException(u, v, predecessor)

    return distance, predecessor
