from tqdm import tqdm
import random
from multiprocessing import Pool
import networkx as nx
from implementation.cpu_max_flow import edmonds_karp, capacity_scaling
from implementation.q_max_flow import q_max_flow, get_max_flow_from_cut_edges,q_max_flow_big

import os
from fnmatch import fnmatch
import time
import pandas as pd


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
                if (vals[2] > 0) and ((vals[0] == s or vals[1] == t) or (random.uniform(0, 1) >= prob)):
                    g.add_edge(vals[0], vals[1], capacity=vals[2])
            elif line.startswith('n'):
                line = line.strip().split(' ')
                if line[2] == 's':
                    s = int(line[1])
                elif line[2] == 't':
                    t = int(line[1])
    return g, s, t


def cut(graph, residual_graph, source):
    n_s = {source}
    for i, j in list(nx.bfs_edges(residual_graph, source)):
        n_s.add(i)
        n_s.add(j)
    n_t = set(graph.nodes).difference(n_s)
    # print(f'{len(n_s)=}, {len(n_t)=}')
    x_c = sum(
        cap['capacity']
        for i, j, cap in graph.edges(data=True)
        if i in n_s and j in n_t
    )
    return x_c, n_s, n_t


def convert_to_graph(origin_graph, flow_dict):
    graph = nx.DiGraph()
    for i in flow_dict:
        graph.add_node(i)
        for j in flow_dict[i]:
            graph.add_node(j)
    for i in flow_dict:
        for j, flow in flow_dict[i].items():
            residual = origin_graph[i][j]['capacity'] - flow

            if residual > 0:
                graph.add_edge(i, j, capacity=residual)
            if residual < origin_graph[i][j]['capacity']:
                graph.add_edge(j, i, capacity=flow)
    return graph


def calc_max_flow(graph_path, percentage):
    graph, source, sink = load_graph(graph_path, percentage)

    start_time = time.time()
    q_cut = q_max_flow_big(graph, source, sink)
    q_mxflow = get_max_flow_from_cut_edges(graph, q_cut, 'omega')
    q_time = time.time() - start_time
    result = graph_path.split('/')[1], q_mxflow, q_time
    print(result)


def time_max_flow_algorithm(prob=0, start=0, stop=0):
    paths = []
    for path, subdirs, files in os.walk('data/'):
        paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))
    stop = len(paths) if stop == 0 else stop
    inputs = [(path, prob) for path in sorted(paths)[start:stop]]

    with Pool(1) as pool:
        pool.starmap(calc_max_flow, inputs)


if __name__ == "__main__":
    time_max_flow_algorithm(prob=0, start=0, stop=0)
