import networkx as nx


def girvan_newman(G: nx.Graph | nx.DiGraph, return_extra_info: bool = False):
    """
    Implementation of the Girvan-Newman algorithm for detecting communities in a graph
    by iteratively removing edges from the original graph. 
    :param G: The input networkx Graph or DiGraph object
    :return: A tuple of communities in the graph
    """
    components = list(nx.connected_components(G))
    btwnss = {}
    while len(components) == 1:
        # Get the dictionary of edges to betweenness values using networkx
        btwnss = betweenness(G)
        # Store the highest betweenness value 
        max_btwnss = max(btwnss.values())

        # Remove the edge(s) from the graph
        for key, value in btwnss.items():
            if value == max_btwnss:
                G.remove_edge(*key)

        # Check the connected components after edge removal
        components = list(nx.connected_components(G))
    # and stop removing edges when the number of connected components increases
    if return_extra_info:
        yield tuple(components), G.edges(data=True)
    else:
        yield tuple(components)


from collections import deque
from typing import Mapping


def betweenness(G: nx.Graph | nx.DiGraph) -> Mapping:
    """
    Implementation of the edge betweenness calculation for all edges in the graph
      as given by Ulrik Brandes (2008)
    :param G: The input networkx Graph or DiGraph object
    :return: A dictionary of edges to betweenness values
    """
    # G = (V, E)
    V = G.nodes()
    E = G.edges()

    c_B = {e: 0.0 for e in E}     # Output dictionary accumulator

    for s in V:
    # single-source shortest-paths problem
        # intialization

        # Per https://docs.python.org/3/tutorial/datastructures.html#using-lists-as-stacks
        #   use collections.deque for a queue and a list for a stack
        Q = deque()  # Queue
        S = []       # Stack
        dist = {}    # Distance from source
        Pred = {}    # List of predecessors on shortest paths from source
        sigma = {}   # Number of shortest paths from source to v \in V
        delta = {}   # Dependency of source on v \in V

        for w in V:
            Pred[w] = []
        for t in V:
            dist[t] = -1
            sigma[t] = 0
        dist[s] = 0
        sigma[s] = 1
        Q.append(s)

        # while Q not empty do
        while len(Q) > 0:
            v = Q.popleft()
            S.append(v)
            # foreach vertex w such that (v, w) \in E do
            for w in G[v]:
                # path discovery
                if dist[w] == -1:
                    dist[w] = dist[v] + 1
                    Q.append(w)
                # path counting
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    Pred[w].append(v)
    # accumulation
        for v in V:
            delta[v] = 0
        while len(S) > 0:
            w = S.pop()
            for v in Pred[w]:
                c = (sigma[v] / sigma[w]) * (1 + delta[w])
                edge = (v, w) if G.is_directed() or (v, w) in c_B else (w, v)
                c_B[edge] += c
                delta[v] += c
            # if w != s:
            #     c_B[w] += delta[w]

    # -----------
    # End Brandes
    # -----------
    
    # Implement scaling to match networkx output
    scale = 1 / (len(V) * (len(V) - 1))
    for v in c_B:
        c_B[v] *= scale

    return c_B
