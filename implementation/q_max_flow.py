import networkx as nx
from pyqubo import Binary, Placeholder, Constraint
from neal import SimulatedAnnealingSampler


def q_max_flow(graph: nx.DiGraph, source: int, target: int):
    obj = 0
    omega_vars = {(i, j): Binary(f'omega_{i}_{j}') for i, j in graph.edges}
    pi_vars = {n: Binary(f'pi_{n}') for n in graph.nodes}
    c1 = Constraint((pi_vars[target] - pi_vars[source] - 1) ** 2,
                    label='constraint_1', condition=lambda x: x == 0)  # First constraint
    c2 = 0
    y_count = 0

    for i in graph.adj:
        for j, cap in graph[i].items():
            obj += omega_vars[(i, j)] * cap['capacity']  # Obj function
            c2 += Constraint(
                (pi_vars[i] - pi_vars[j] + omega_vars[(i, j)] -
                 (Binary(f'y_2^0-{y_count}') + 2 * Binary(f'y_2^1-{y_count}'))) ** 2,
                label='constraint_2', condition=lambda x: x == 0
            )  # Second constraint
            y_count += 1

    lagrange = Placeholder('L')
    obj +=  lagrange * c1 + lagrange * c2
    bqm = obj.compile().to_bqm(feed_dict={'L': 100})
    res = SimulatedAnnealingSampler().sample(bqm, num_reads=10)
    # print(res)

    return res.first


def q_max_flow_wiki(graph: nx.DiGraph, source, target):
    d_vars = {(i, j): Binary(f'd_{i}_{j}') for i, j in graph.edges}
    nodes = list(graph.nodes)
    nodes.remove(source)
    nodes.remove(target)
    z_vars = {n: Binary(f'z_{n}') for n in nodes}
    y_count = 0
    obj = 0
    c1 = 0
    c2 = 0
    c3 = 0
    edges = graph.edges

    for u in graph.adj:
        for v, cap in graph[u].items():
            obj += d_vars[(u, v)] * cap['capacity']  # Obj function

            if u != source and v != target:
                c1 += Constraint(
                    (d_vars[(u, v)] - z_vars[u] + z_vars[v] -
                     Binary(f'y_1^0-{y_count}') - 2 * Binary(f'y_1^1-{y_count}')) ** 2,
                    label='constraint_1', condition=lambda x: x == 0
                )
                y_count += 1

    for v in graph[source]:
        if v != target:
            c2 += Constraint(
                (d_vars[(source, v)] + z_vars[v] - Binary(f'y_2^0-{y_count}') - 1) ** 2,
                label='constraint_2', condition=lambda x: x == 0
            )
            y_count += 1

    for u in graph.adj:
        if u != source and (u, target) in edges:
            c3 += Constraint(
                (d_vars[(u, target)] - z_vars[u] - Binary(f'y_3^0-{y_count}')) ** 2,
                label='constraint_3', condition=lambda x: x == 0
            )
            y_count += 1

    lagrange = Placeholder('L')
    obj += lagrange * c1 + lagrange * c2 + lagrange * c3
    if (source, target) in graph.edges:
        obj += lagrange * Constraint(
            (d_vars[(source, target)] - 1) ** 2,
            label='constraint_4', condition=lambda x: x == 0
        )
    bqm = obj.compile().to_bqm(feed_dict={'L': 100})
    res = SimulatedAnnealingSampler().sample(bqm, num_reads=10)
    # print(res)
    return res.first


def get_max_flow_from_cut_edges(graph, sample, var_name):
    cut_edges = {key: value for key, value in sample[0].items() if key.startswith(var_name)}
    cut_edges = {key for key, value in cut_edges.items() if value == 1}
    edges = set()
    for e in cut_edges:
        parts = e.split('_')
        edges.add((int(parts[1]), int(parts[2])))
    # print(edges)
    return sum(graph[i][j]['capacity'] for i, j in edges)
