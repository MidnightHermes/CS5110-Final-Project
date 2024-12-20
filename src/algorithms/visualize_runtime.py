import time
import numpy as np
import random
import networkx as nx
import matplotlib.pyplot as plt
from typing import Callable, Tuple


def measure_runtime(algorithm: Callable[[nx.Graph], any], graph_gen_function: Callable[[int, int], nx.Graph], runtime_function: Callable[[int, int], float]) -> Tuple[range, list, list]:
    """
    Measure the runtime of the given algorithm on graphs with various numbers of nodes `range(10, 1000, 50)`.

    :param algorithm: The algorithm to measure the runtime of. (Assumes a single argument *G*)
    :param graph_gen_function: A function that generates a random graph. (Assumes two arguments *num_nodes* and *num_edges*)
    :param runtime_function: A function that calculate the expected runtime of the algorithm. (Assumes two arguments, *num_nodes* and *num_edges*)
    :return results: A tuple of 3 lists containing the number of nodes, the measured runtimes, and the expected runtimes.
    """
    node_counts = range(10, 1000, 50)
    runtimes = []
    expected_times = []
    ratios = []
    for n in node_counts:
        max_edges = n * (n - 1)
        num_edges = max_edges * 0.1
        G = graph_gen_function(n, num_edges)

        start_time = time.time()
        algorithm(G)
        runtime = time.time() - start_time
        runtimes.append(runtime)

        expected_runtime = runtime_function(n, num_edges) / 1e6  # Convert time units down
        expected_times.append(expected_runtime)

        # calculate how much faster the actual runtime is over the expected runtime
        ratio = runtime / expected_runtime
        ratios.append(ratio)

    # find the average ratio and multiply the expected times by it to better fit the runtime curve
    ratios.sort()
    c = ratios[len(ratios) // 2]
    expected_times = [t * c for t in expected_times]

    return [(node_counts, runtimes, expected_times)]


def plot_results(results, algorithm_name: str, expected_runtime: str, line_color: str):
    plt.figure(figsize=(6, 4), facecolor="#16242f")
    ax = plt.axes()
    ax.set_facecolor("#16242f")
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.xaxis.label.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='y', colors='white')

    for node_counts, runtimes, expected_times in results:
        # Plot measured runtimes
        plt.plot(node_counts, runtimes, label=f"Measured Runtime", color=line_color)
        # Plot expected runtimes
        plt.plot(node_counts, expected_times, linestyle="dotted", label=expected_runtime, color=line_color)

    plt.xlabel("Number of Vertices ($V$)")
    plt.ylabel("Execution Time (seconds)")
    plt.title(f"Time Complexity of {algorithm_name.capitalize()}", color="white")
    plt.legend(facecolor="#16242f", labelcolor='linecolor')
    plt.xlim(10, 1000)
    plt.ylim(0, 1)
    plt.xticks(node_counts[::2])
    plt.savefig(f"src/algorithms/{algorithm_name}_time_complexity.png")
    plt.show()


def main():
    # Intended usage using prims algorithm as an example:
    from prims import prims
    from random_graph import RandomGraphBuilder

    algorithm = prims

    def graph_gen_function(num_nodes, num_edges):
        max_edges = (num_nodes * (num_nodes - 1)) // 2
        edge_density = num_edges / max_edges

        return RandomGraphBuilder() \
               .nodes(num_nodes) \
               .random_edges(edge_density) \
               .weighted(range(1, 100)) \
               .build()

    def runtime_function(num_nodes, num_edges):
        return num_edges * np.log(num_nodes)

    count = 0
    while True:
        MAX_ATTEMPTS = 50
        if count > MAX_ATTEMPTS:
            raise Exception(f"Failed to generate a valid graph after {MAX_ATTEMPTS} attempts")
        count += 1

        try:
            results = measure_runtime(algorithm, graph_gen_function, runtime_function)
            print(results)
            break
        except:
            pass

    plot_results(results, algorithm.__name__, \
                 expected_runtime="Expected Runtime: $O(|E| \log |V|)$", \
                 line_color="#eb8fd8"\
                )


if __name__ == "__main__":
    main()
