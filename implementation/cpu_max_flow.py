import time
import numpy as np
import networkx as nx
from collections import deque
from networkx import NetworkXNoPath


def edmonds_karp(graph, source, sink):
    max_flow = k = 0
    while True:
        path, capacity = find_augmenting_path(graph, source, sink)
        if path is None:
            break
        max_flow += capacity
        if max_flow > 100 * k:
            # print(f'{max_flow=}')
            k += 1
        for val in range(len(path) - 1):
            u, v = path[val], path[val + 1]
            graph[u][v]['capacity'] -= capacity
            if graph[u][v]['capacity'] == 0:
                graph.remove_edge(u, v)
            if (v, u) not in graph.edges:
                graph.add_edge(v, u, capacity=0)
            graph[v][u]['capacity'] += capacity

    return max_flow, graph


def find_augmenting_path(graph, source, sink):
    deq = deque([(source, [source])])
    visited = {source}

    while deq:
        u, path = deq.popleft()

        for v in graph[u]:
            # if v not in visited and graph[u][v]['capacity'] > 0:
            if v not in visited:
                new_path = path + [v]
                if v == sink:
                    return new_path, min(graph[u][v]['capacity'] for u, v in zip(new_path, new_path[1:]))
                deq.append((v, new_path))
                visited.add(v)

    return None, 0


# CAPACITY SCALING

def capacity_scaling(graph, source, sink):
    max_flow = k = 0
    u = 2 ** int(np.log10(max([edge['capacity'] for _, _, edge in graph.edges(data=True)])))
    u_residual = u_based_residual_graph(graph, u)
    while u > 0:
        res = provisional_augm_path(u_residual, source, sink)
        while res:
            max_flow += res['cap']
            '''if max_flow > 100 * k:
                print(f'{max_flow=}')
                k += 1'''
            for val in range(len(res['path']) - 1):
                i, j = res['path'][val], res['path'][val + 1]
                graph[i][j]['capacity'] -= res['cap']
                u_residual[i][j]['capacity'] -= res['cap']
                if graph[i][j]['capacity'] == 0:
                    graph.remove_edge(i, j)
                    u_residual.remove_edge(i, j)
                if (j, i) not in graph.edges:
                    graph.add_edge(j, i, capacity=0)
                graph[j][i]['capacity'] += res['cap']
            res = provisional_augm_path(u_residual, source, sink)

        u_residual = u_based_residual_graph(graph, u) if u > 1 else graph.copy()
        res = provisional_augm_path(u_residual, source, sink)
        if not res:
            u //= 2
            u_residual = u_based_residual_graph(graph, u)

    return max_flow, graph


def u_based_residual_graph(graph, u):
    u_graph = graph.copy()
    for *edge, data in graph.edges(data=True):
        if data['capacity'] < u:
            u_graph.remove_edge(*edge)
    return u_graph


def provisional_augm_path(graph, source, sink):
    try:
        path = nx.shortest_path(graph, source, sink)
        min_cap = min(graph[path[val]][path[val + 1]]['capacity'] for val in range(len(path) - 1))
        return {'path': path, 'cap': min_cap}
    except NetworkXNoPath:
        return False


def u_based_augmenting_path(graph, source, sink):
    deq = deque([(source, [source])])
    visited = {source}
    while deq:
        i, path = deq.popleft()
        for j in graph[i]:
            if j not in visited:
                new_path = path + [j]
                if j == sink:
                    return {'path': new_path,
                            'cap': min(graph[i][j]['capacity'] for i, j in zip(new_path, new_path[1:]))}
                deq.append((j, new_path))
                visited.add(j)
    return False
