import networkx as nx
import random

def ramsey(g: nx.Graph):
    """
    Respectively approximates the largest clique and independent set in a graph.
    """

    # base case, return empty clique and independent set
    if g.number_of_nodes() == 0:
        return set(), set()

    # choose random node as pivot
    v = random.choice(sorted(g.nodes))

    node_set = set(g.nodes)

    # determine the neighbors and non-neighbors of v in g
    neighbors = set(g.adj[v])
    non_neighbors = node_set - neighbors

    # recurse on the subgraph induced on the neighbors of v
    neighbor_graph = g.copy()
    neighbor_graph.remove_node(v)
    neighbor_graph.remove_nodes_from(non_neighbors)

    c1, i1 = ramsey(neighbor_graph)

    # recurse on the subgraph induced on the non-neighbors of v
    non_neighbor_graph = g.copy()
    non_neighbor_graph.remove_node(v)
    non_neighbor_graph.remove_nodes_from(neighbors)

    c2, i2 = ramsey(non_neighbor_graph)

    # since c1 is a clique of neighbors of v, {v} | c1 is still
    # a clique. And likewise, since i2 is an independent set of
    # non-neighbors of v, {v} | i2 is still an independent set.
    c1.add(v)
    i2.add(v)

    # return the largest of the found cliques and independent sets, respectively
    return max(c1, c2, key=len), max(i1, i2, key=len)

if __name__ == '__main__':
    from random_graph import RandomGraphBuilder as RGB

    import sys
    import timeit

    gen_graph = lambda n, k, d: RGB().nodes(n).clique(k, False).random_edges(d).connected().build()

    fn = sys.argv[1] if len(sys.argv) > 1 else ''

    stmt = 'nx.approximation.ramsey_R2(g)' if fn == '--nx' else 'ramsey(g)'

    setup = lambda n, k, d: gen_graph(n, k, d)

    graph10 = setup(10, 2, .35)
    graph100 = setup(100, 20, .35)
    graph1000 = setup(1000, 200, .35)

    # calculate actual edge-density of a given graph
    dof = lambda g: len(g.edges()) / ((g.number_of_nodes() * (g.number_of_nodes() - 1)) / 2)   

    def fmt(times, n, k, d, t):
        return f'Running {stmt[:-3]} {times} times on a graph of size {n} with a clique of size {k} and overall edge density of {d: .2f} took {t} seconds' 

    run10 = timeit.timeit(stmt, setup='g = graph10', number=10000, globals=globals())
    print(fmt(10000, 10, 2, dof(graph10), run10))

    run100 = timeit.timeit(stmt, setup='g = graph100', number=1000, globals=globals())
    print(fmt(1000, 100, 20, dof(graph100), run100))

    run1000 = timeit.timeit(stmt, setup='g = graph1000', number=100, globals=globals())
    print(fmt(100, 1000, 200, dof(graph1000), run1000))
