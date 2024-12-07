import networkx as nx


def girvan_newman(G: nx.Graph | nx.DiGraph):
    """
    Implementation of the Girvan-Newman algorithm for detecting communities in a graph
    by iteratively removing edges from the original graph. 
    :param G: The input networkx Graph or DiGraph object
    :return: A graph with a singular contracted node and zero edges
    """
    components = list(nx.connected_components(G))
    while len(components) == 1:
        # Get the dictionary of edges to betweenness values using networkx
        btwnss = nx.edge_betweenness_centrality(G)
        # Store the highest betweenness value 
        max_btwnss = max(btwnss.values())

        # Remove the edge(s) from the graph
        for key, value in btwnss.items():
            if value == max_btwnss:
                G.remove_edge(*key)

        # Check the connected components after edge removal
        components = list(nx.connected_components(G))
    # and stop removing edges when the number of connected components increases
    yield tuple(components)
