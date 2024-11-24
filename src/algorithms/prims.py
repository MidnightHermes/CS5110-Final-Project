import random
import networkx as nx
import heapq


def prims(graph: nx.Graph | nx.DiGraph) -> nx.Graph | nx.DiGraph:
    """
    Implementation of Prim's algorithm for finding the minimum spanning tree of a graph
    :param graph: The input networkx Graph or DiGraph object
    :return: The minimum spanning tree of the input graph
    """
    start = list(graph.nodes)[random.randint(0, len(graph.nodes) - 1)]  # Randomly select a starting node from the graph
    mst = type(graph)()  # Create a new graph of the same type as the input graph
    mst.add_node(start)  # Initialize the MST with the start node

    p_queue = []  # Initialize the priority queue
    for origin, link, data in graph.edges(start, data=True):  # Add all edges from the start node to the priority queue
        weight = data['weight']
        edge_tuple = (origin, link)
        # heapq orders items based on the zeroth element so we set that to weight
        heapq.heappush(p_queue, (weight, edge_tuple))

    while mst.nodes != graph.nodes:
        edge = heapq.heappop(p_queue)

        if edge[1][1] not in mst.nodes:
            mst.add_node(edge[1][1])
            mst.add_edge(*edge[1], weight=edge[0])

            for origin, link, data in graph.edges(edge[1][1], data=True):
                if link not in mst.nodes:
                    weight = data['weight']
                    edge_tuple = (origin, link)
                    heapq.heappush(p_queue, (weight, edge_tuple))

    return mst
