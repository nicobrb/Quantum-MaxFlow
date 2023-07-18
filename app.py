import cProfile
import pstats
import random
import networkx as nx
from implementation.cpu_max_flow import edmonds_karp, capacity_scaling
import matplotlib.pyplot as plt

import os
from fnmatch import fnmatch
import time
import pandas as pd
from tqdm import tqdm


def load_graph(path, prob):
    g = nx.DiGraph()
    s = None
    t = None
    with open(path) as f:
        for line in f:
            if line.startswith('p'):
                num_nodes = int(line.split(' ')[2])
                nodes = {x + 1 for x in range(num_nodes)}
                for n in nodes:
                    g.add_node(n)
            elif line.startswith('a'):
                vals = [int(x) for x in line.split(' ')[1:]]
                if (vals[0] == s or vals[1] == t) or (random.uniform(0, 1) >= prob and vals[2] > 1):
                    g.add_edge(vals[0], vals[1], capacity=vals[2])
            elif line.startswith('n'):
                line = line.strip().split(' ')
                if line[2] == 's':
                    s = int(line[1])
                elif line[2] == 't':
                    t = int(line[1])
    return g, s, t


def time_max_flow_algorithm(prob):
    paths = []
    for path, subdirs, files in os.walk('data/'):
        paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))

    data = []
    lib_time = 0
    for graph_path in paths[9:10]:
        graph, source, sink = load_graph(graph_path, prob)
        # edge_labels = nx.get_edge_attributes(graph, 'capacity')
        # pos = nx.spring_layout(graph)
        # nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_weight='bold')
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        # plt.show(block=False)

        start_time = time.time()
        copy_graph = graph.copy()
        lib_mxflow, flow_dict = nx.maximum_flow(copy_graph, _s=source, _t=sink)
        print("\n", lib_mxflow)
        lib_time = time.time() - start_time
        lib_time += lib_time

        start_time = time.time()
        copy_graph = graph.copy()
        impl_mxflow, residual_graph = capacity_scaling(copy_graph, source, sink)
        impl_time = time.time() - start_time

        data.append([graph_path, lib_time, impl_time, lib_mxflow, impl_mxflow, lib_mxflow == impl_mxflow])

        if lib_mxflow != impl_mxflow:
            continue

    data = pd.DataFrame(data, columns=['Graph path', 'Time lib', 'Time custom', 'Val lib', 'Val custom', 'Correct'])
    data.to_csv('export/results.csv')
    print(data)
    print(data.describe())
    print(f'Total time of library computation {lib_time}')


if __name__ == "__main__":
    # with cProfile.Profile() as profile:
    for i in range(1):
        time_max_flow_algorithm(0.75)
    # results = pstats.Stats(profile)
    # results.sort_stats(pstats.SortKey.TIME)
    # # results.print_stats()
