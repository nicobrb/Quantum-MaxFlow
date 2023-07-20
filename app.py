from tqdm import tqdm
import random
import networkx as nx
from implementation.cpu_max_flow import edmonds_karp, capacity_scaling
from implementation.q_max_flow import q_max_flow, get_max_flow_from_cut_edges, q_max_flow_wiki

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
    print(f'{len(n_s)=}, {len(n_t)=}')
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

def time_max_flow_algorithm(prob):
    paths = []
    for path, subdirs, files in os.walk('data/'):
        paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))

    data = []
    for graph_path in tqdm(sorted(paths)):
        graph, source, sink = load_graph(graph_path, prob)

        # edge_labels = nx.get_edge_attributes(graph, 'capacity')
        # pos = nx.spring_layout(graph)
        # nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_weight='bold')
        # nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
        # plt.show(block=False)

        start_time = time.time()
        lib_mxflow, flow_dict = nx.maximum_flow(graph, _s=source, _t=sink)
        lib_time = time.time() - start_time

        start_time = time.time()
        cs_mxflow, residual_graph = capacity_scaling(graph.copy(), source, sink)
        cs_time = time.time() - start_time

        start_time = time.time()
        # q_cut = q_max_flow(graph, source, sink)
        # q_mxflow = get_max_flow_from_cut_edges(graph, q_cut, 'omega')
        q_mxflow = -1 # dummy value, just for testing
        q_time = time.time() - start_time

        data.append([graph_path, round(lib_time, 5), round(cs_time, 5), round(q_time, 5),
                     lib_mxflow, cs_mxflow, q_mxflow])

    data = pd.DataFrame(data, columns=['graph-path', 'time-lib(s)', 'time-cs(s)', 'time-q(s)',
                                       'val-lib', 'val-cs', 'val-q'])
    print(data.to_string())
    data.to_csv('export/results.csv')
    data.describe().to_csv('export/summary.csv')


if __name__ == '__main__':
    time_max_flow_algorithm(0)
