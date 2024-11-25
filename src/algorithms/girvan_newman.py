import networkx as nx

def girvan_newman(G: nx.Graph | nx.DiGraph) -> nx.Graph | nx.DiGraph:
    """
    Implementation of the Girvan-Newman algorithm for detecting communities in a graph
    by iteratively removing edges from the original graph. 
    :param G: The input networkx Graph or DiGraph object
    :return: A graph with a singular contracted node and zero edges
    """

    while G.number_of_edges() > 0 or G.number_of_nodes() > 1:
        # Get the dictionary of edges to betweenness values using networkx
        btwnss = nx.edge_betweenness_centrality(G)
        # Store the highest betweenness value 
        max_btwnss = max(btwnss.values())
        # Identify the list of all edges with the highest betweenness value
        edges = []
        for e in btwnss:
            if btwnss[e] == max_btwnss:
                edges.append(e)

        # Contract the edge(s) with the highest rank from the graph
        for e in edges:
            # print(f'Iterating over list of edges tied for highest betweenness {max_btwnss}: edge = ', e, '\nset of tied edges = ', edges)
            # print('G.nodes = ', G.nodes, 'G.edges = ', G.edges, '\n')
            if G.has_edge(*e):
                G = nx.algorithms.minors.contracted_edge(G, e, self_loops=False)
                # Relabel the new contracted node $e_0$ where $e_1$ is the linked node
                # We use a formatted string to concatenate the labels of both nodes
                G = nx.relabel_nodes(G, {e[0]: f'{e[0]}, {e[1]}'})
            else:
                print("\rNode involved in tie for highest betweenness has already been contracted", end='')

    # Finally, return the modified graph which should only have one node and zero edges
    return G
