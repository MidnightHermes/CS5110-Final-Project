import networkx as nx
import random

def ramsey(g: nx.Graph):
    """
    Respectively approximates the largest clique and independent set in a graph.
    """
    if g.number_of_nodes() == 0:
        return set(), set()
   
    v = random.choice(sorted(g.nodes))

    node_set = set(g.nodes)

    neighbors = set(g.adj[v])
    non_neighbors = node_set - neighbors

    neighbor_graph = g.copy()
    neighbor_graph.remove_node(v)
    neighbor_graph.remove_nodes_from(non_neighbors)

    c1, i1 = ramsey(neighbor_graph)

    non_neighbor_graph = g.copy()
    non_neighbor_graph.remove_node(v)
    non_neighbor_graph.remove_nodes_from(neighbors)

    c2, i2 = ramsey(non_neighbor_graph)

    c1.add(v)
    i2.add(v)

    return max(c1, c2, key=len), max(i1, i2, key=len)
