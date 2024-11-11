import networkx as nx
from networkx.classes.function import get_edge_attributes

def bellman_ford(g, source):
    """
    Computes all the shortest paths in a directed weighted graph with negative edge weights
    (but not negative cycles) between every node and some source node s.
    :param g: the graph to perform the algorithm on
    :param source: the source node to query in g
    """

    n = g.number_of_nodes()
    edges = g.edges

    inf = abs(max(get_edge_attributes(g, 'weight').values())) + 1

    distance = {v: inf for v in g.nodes}
    predecessor = {v: None for v in g.nodes}

    distance[source] = 0

    for _ in range(n - 1):
        for (u, v) in edges:
            w = edges[u, v]['weight']
            if distance[u] + w < distance[v]:
                distance[v] = distance[u] + w
                predecessor[v] = u

    for (u, v) in edges:
        w = edges[u, v]['weight']
        if distance[u] + w < distance[v]:
            return None

    return distance, predecessor
