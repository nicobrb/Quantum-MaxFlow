import cProfile
import pstats
import random
import networkx as nx
from implementation.cpu_max_flow import edmonds_karp, capacity_scaling
from implementation.q_max_flow import q_max_flow, get_max_flow_from_cut_edges, q_max_flow_wiki
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
    n_t = set()
    x_c = 0
    for i, j, val in residual_graph.edges(data=True):
        try:
            if (val['capacity'] - graph[j][i]['capacity']) == 0:
                if (not list(nx.all_simple_paths(residual_graph, source, i))) and \
                        (source == j or len(list(nx.all_simple_paths(residual_graph, source, j))) > 0):
                    n_t.add(i)
                    x_c += graph[j][i]['capacity']
                else:
                    n_s.add(i)
        except Exception:
            pass
    '''for i in n_s:
        for j in n_t:
            try:
                x_c += graph[i][j]['capacity']
            except Exception:
                pass'''
    '''for i in graph.adj:
        for j, cap in graph[i].items():
            if i in n_s and j in n_t:
                x_c += cap['capacity']'''
    return x_c, n_s, n_t

def convert_to_graph(origin_graph, flow_dict):
    graph = nx.DiGraph()
    x_c = 0
    for i in flow_dict:
        graph.add_node(i)
        for j in flow_dict[i]:
            graph.add_node(j)
    for i in flow_dict:
        for j, flow in flow_dict[i].items():
            residual = origin_graph[i][j]['capacity'] - flow
            if residual > 0:
                graph.add_edge(i, j, capacity=residual)
            else:
                graph.add_edge(j, i, capacity=flow)
    return graph

def time_max_flow_algorithm(prob):
    paths = []
    for path, subdirs, files in os.walk('computable/'):
        paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))

    data = []
    for graph_path in tqdm(sorted(paths)[7:8]):
        print(graph_path)
        graph, source, sink = load_graph(graph_path, prob)

        # edge_labels = nx.get_edge_attributes(graph, 'capacity')
        # pos = nx.spring_layout(graph)
        # nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_weight='bold')
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        # plt.show(block=False)

        start_time = time.time()
        copy_graph = graph.copy()
        lib_mxflow, flow_dict = nx.maximum_flow(copy_graph, _s=source, _t=sink)
        print(f'{lib_mxflow=}')
        new_g = convert_to_graph(graph, flow_dict)

        # print(list(nx.all_simple_paths(new_g, source, sink)))
        # cut_value, cut_partition = nx.minimum_cut(new_g, _s=source, _t=sink)
        cut_val, *_ = cut(graph, new_g, source)
        print(f'{cut_val=}')
        lib_time = time.time() - start_time

        #start_time = time.time()
        #copy_graph = graph.copy()
        #karp_mxflow, residual_graph = edmonds_karp(copy_graph, source, sink)
        #cut_custom = nx.minimum_cut(residual_graph, _s=source, _t=sink)
        #karp_time = time.time() - start_time

        start_time = time.time()
        copy_graph = graph.copy()
        cap_mxflow, residual_graph = capacity_scaling(copy_graph, source, sink)
        # print(cap_mxflow)
        # cut_custom_val, cut_custom_partition = nx.minimum_cut(residual_graph, _s=source, _t=sink)
        cut(copy_graph, residual_graph, source)
        cap_time = time.time() - start_time

        #start_time = time.time()
        #q_mxflow = q_max_flow(graph, source, sink)
        #q_mxflow = get_max_flow_from_cut_edges(graph, q_mxflow, 'omega')
        #q_time = time.time() - start_time

        #start_time = time.time()
        #q_mxflow_wiki = q_max_flow_wiki(graph, source, sink)
        #q_mxflow_wiki = get_max_flow_from_cut_edges(graph, q_mxflow_wiki, 'd')
        #q_time_wiki = time.time() - start_time

        #data.append([graph_path, round(lib_time, 5), round(karp_time, 5), round(cap_time, 5), round(q_time, 5), round(q_time_wiki, 5),
                     #lib_mxflow, karp_mxflow, cap_mxflow, q_mxflow, q_mxflow_wiki])

    data = pd.DataFrame(data, columns=['graph-path', 'time-lib', 'time-edmonds-karp', 'time-capacity-scaling', 'time-quantum', 'time-quantum-wiki',
                                       'val-lib', 'val-edmonda-karp', 'val-capacity-scaling', 'val-quantum', 'val-quantum-wiki'])
    print(data.to_string())
    data.to_csv('export/results.csv')
    print(data.describe().to_string())


if __name__ == '__main__':
    # with cProfile.Profile() as profile:
    for _ in range(1):
        time_max_flow_algorithm(0)
    # results = pstats.Stats(profile)
    # results.sort_stats(pstats.SortKey.TIME)
    # # results.print_stats()
