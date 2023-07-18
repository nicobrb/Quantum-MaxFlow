import time
import networkx as nx
from collections import deque
import numpy as np
from networkx import NetworkXNoPath
from networkx.algorithms.flow import shortest_augmenting_path


def edmonds_karp(graph, source, sink):
    max_flow = 0

    while True:
        path, capacity = find_augmenting_path(graph, source, sink)
        if path is None:
            break
        max_flow += capacity
        print(f"{max_flow=}")
        for u, v in zip(path, path[1:]):
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
            if v not in visited and graph[u][v]['capacity'] > 0:
                new_path = path + [v]
                if v == sink:
                    return new_path, min(graph[u][v]['capacity'] for u, v in zip(new_path, new_path[1:]))
                deq.append((v, new_path))
                visited.add(v)

    return None, 0


# CAPACITY SCALING

def capacity_scaling(graph, source, sink):
    max_flow = 0
    u_max = max([edge["capacity"] for _, _, edge in graph.edges(data=True)])
    u = 2 ** int(np.log(u_max))
    start = time.time()
    u_residual = u_based_residual_graph(graph, u)
    end = time.time()
    # print(f"1) {end - start}")
    k = 0
    while u > 0:
        start = time.time()
        res = provisional_augm_path(u_residual, source, sink)
        end = time.time()
        # print(f"2) {end - start}")
        while res:
            max_flow += res["cap"]
            if max_flow > 100 * k:
                print(f"{max_flow=}")
                k += 1
            start = time.time()
            for i, j in zip(res["path"], res["path"][1:]):
                graph[i][j]["capacity"] -= res["cap"]
                u_residual[i][j]["capacity"] -= res["cap"]
                if graph[i][j]["capacity"] == 0:
                    graph.remove_edge(i, j)
                    u_residual.remove_edge(i, j)
            end = time.time()
            # print(f"3) {end - start}")
            start = time.time()
            res = provisional_augm_path(u_residual, source, sink)
            end = time.time()
            # print(f"4) {end - start}")
        u //= 2
        start = time.time()
        u_residual = u_based_residual_graph(graph, u)
        end = time.time()
        # print(f"5) {end - start}")
    return max_flow, u_residual


def u_based_residual_graph(graph, u):
    u_graph = graph.copy()
    for *edge, data in graph.edges(data=True):
        if data["capacity"] < u:
            u_graph.remove_edge(*edge)
    return u_graph


def provisional_augm_path(graph, source, sink):
    # nozero_graph = u_based_residual_graph(graph, 1)
    try:
        path = nx.shortest_path(graph, source, sink)
        min_cap = min(graph[i][j]["capacity"] for i, j in zip(path, path[1:]))
        return {"path": path, "cap": min_cap}
    except NetworkXNoPath:
        return False


def u_based_augmenting_path(graph, source, sink):
    deq = deque([(source, [source])])
    visited = {source}
    while deq:
        i, path = deq.popleft()
        for j in graph[i]:
            if j not in visited and graph[i][j]["capacity"] > 0:
                new_path = path + [j]
                if j == sink:
                    return {"path": new_path,
                            "cap": min(graph[i][j]["capacity"] for i, j in zip(new_path, new_path[1:]))}
                deq.append((j, new_path))
                visited.add(j)
    return False
