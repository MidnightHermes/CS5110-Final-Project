import networkx as nx
from networkx.algorithms.approximation.clique import large_clique_size

from itertools import combinations
from math import log

def partition(s, partition_sizes):
    (quot, rem) = divmod(len(s), partition_sizes)

    as_list = list(s)

    for _ in range(quot):
        size = partition_sizes

        if rem > 0:
            size += 1
            rem -= 1

        part = as_list[:size]
        as_list = as_list[size+1:]

        yield set(part)

def is_induced_clique(g, inducing_set):
    """
    Confirms if a graph induced on a given set is a clique.
    :param g: the graph being queried
    :param inducing_set: the set of vertices the graph will be induced on
    :return: true if the induced subgraph is a clique, false otherwise
    """
    induced = g.induced_subgraph(inducing_set)

    n = g.number_of_nodes()

    return all(d == (n-1) for (_, d) in induced.degree)

def neighbor_set(g, node_subset):
    """
    Given a graph and a subset of nodes in that graph, finds the set of nodes outside
    the subset that are all neighbors of the nodes in the subset.
    :param g: the graph being queried
    :param node_subset: a subset of nodes to query on g
    :return: the set of nodes that are neighbors to every node in the subset
    """

    neighbors = g.restricted_view(node_subset).nodes()

    for v in node_subset:
        neighbors &= g[v]

    return neighbors


def feige(graph: nx.Graph, t=None):
    """

    """

    n = graph.number_of_nodes()

    if t is None:
        t = log(n) / log(log(n))

    # A large clique size must already be known
    clique_size = large_clique_size(graph)
    k = n / clique_size

    def iteration(subgraph, c):
        n = subgraph.number_of_nodes()

        # Step 1
        if n < 6 * k * t:
            return True, c

        # Step 2: Partition nodes into sets of size 2kt
        partition_size = round(2 * k * t)
        nodes = subgraph.nodes()
        for part in partition(nodes, partition_size):
            # Step 3: For each partition, consider all subgraphs with a node count of t
            t_floor = int(t)
            for subset in combinations(part, t_floor):
                # Step 4: Call a subset of vertices good if the graph induced on it is
                #         a clique and the cardinality of its neighbor set is >= n/2k-t
                if not is_induced_clique(subgraph, subset):
                    continue

                neighbors = neighbor_set(subgraph, subset)

                if len(neighbors) >= n/(2 * k - t):
                    # Step 5: If the subset is good, add it to c and do the next iteration
                    #         on the subgraph induced by the neighbor set

                    new_subgraph = subgraph.induced_subgraph(neighbors)
                    c |= set(subset)

                    return iteration(n, c)
        # Step 6: If all subsets are poor, then end the phase
        return False, nodes

    # If a sufficiently large clique is not found,
    # then a poor subgraph was found and will be removed
    is_good = False
    verts = set()
    while not is_good:
        g = g.restricted_view(verts)

        is_good, verts = iteration(g, verts)

    return verts

