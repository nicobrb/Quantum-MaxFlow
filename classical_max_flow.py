import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import os
from fnmatch import fnmatch
import time
import pandas as pd
from tqdm import tqdm

def load_graph(path):
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
                g.add_edge(vals[0], vals[1], capacity=vals[2])
            elif line.startswith('n'):
                line = line.strip().split(' ')
                if line[2] == 's':
                    s = int(line[1])
                elif line[2] == 't':
                    t = int(line[1])
    return g, s, t

def construct_residual_graph(graph):
    residual_graph = graph.copy()

    for u, v, _ in graph.edges(data=True):
        residual_graph.add_edge(v, u, capacity=0)

    return residual_graph

def edmonds_karp(graph, source, target):
    max_flow = 0
    residual_graph = construct_residual_graph(graph)
    
    while True:
        path, capacity = find_augmenting_path(residual_graph, source, target)
        if path is None:
            break
        max_flow += capacity
        for u, v in zip(path, path[1:]):
            residual_graph[u][v]['capacity'] -= capacity
            if u not in residual_graph[v]:
                residual_graph[v][u] = {'capacity': 0}
            residual_graph[v][u]['capacity'] += capacity
    
    return max_flow

def find_augmenting_path(graph, source, target):
    queue = deque([(source, [source])])
    visited = {source}

    while queue:
        u, path = queue.popleft()
        for v in graph[u]:
            if v not in visited and graph[u][v]['capacity'] > 0:
                new_path = path + [v]
                if v == target:
                    return new_path, min(graph[u][v]['capacity'] for u, v in zip(new_path, new_path[1:]))
                queue.append((v, new_path))
                visited.add(v)
                
    return None, 0

paths = []
for path, subdirs, files in os.walk('./data/'):
    paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))

datas = []
tot = 0
for p in tqdm(paths):
    graph, source, target = load_graph(p)

    # edge_labels = nx.get_edge_attributes(graph, 'capacity')
    # pos = nx.spring_layout(graph)
    # nx.draw(graph, pos, with_labels=True, node_size=500, node_color='lightblue', font_weight='bold')
    # nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels)
    # plt.show(block=False)

    start_time = time.time()
    max_flow_lib = nx.maximum_flow_value(graph, _s=source, _t=target)
    lib_time = time.time() - start_time
    tot += lib_time

    start_time = time.time()
    max_flow_custom = edmonds_karp(graph, source, target)
    custom_time = time.time() - start_time

    datas.append([p, lib_time, custom_time, max_flow_lib, max_flow_custom, max_flow_lib == max_flow_custom])

datas = pd.DataFrame(datas, columns=['Graph path', 'Time lib', 'Time custom', 'Val lib', 'Val custom', 'Correct'])
datas.to_csv('dataset.csv')
print(datas)
print(datas.describe())
print(f'Total time of library computation {tot}')
