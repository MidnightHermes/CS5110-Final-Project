import networkx as nx
from networkx.classes.function import get_edge_attributes

def bellman_ford(g, source):
    n = g.number_of_nodes()
    edges = g.edges

    inf = abs(max(get_edge_attributes(g, 'weight').values())) + 1

    distance = [inf] * n
    predecessor = [None] * n

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
