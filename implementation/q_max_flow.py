import networkx as nx
from pyqubo import Binary, Placeholder, Constraint
from neal import SimulatedAnnealingSampler
import time
# from dwave.system import LeapHybridSampler
from dimod import BinaryQuadraticModel, Binary


def q_max_flow(graph: nx.DiGraph, source: int, target: int):
    obj = []
    omega_vars = {(i, j): Binary(f'omega_{i}_{j}') for i, j in graph.edges}
    pi_vars = {n: Binary(f'pi_{n}') for n in graph.nodes}
    c1 = Constraint((pi_vars[target] - pi_vars[source] - 1) ** 2,
                    label='constraint_1', condition=lambda x: x == 0)  # First constraint
    c2 = []

    for y_count, (i, j, cap) in enumerate(graph.edges(data=True)):
        obj.append(omega_vars[(i, j)] * cap['capacity'])  # Obj function
        c2.append(Constraint(
            (pi_vars[i] - pi_vars[j] + omega_vars[(i, j)] -
             (Binary(f'y_2^0-{y_count}') + 2 * Binary(f'y_2^1-{y_count}'))) ** 2,
            label='constraint_2', condition=lambda x: x == 0
        ))  # Second constraint

    lagrange = Placeholder('L')
    obj = sum(obj) + lagrange * c1 + sum(lagrange * c2_i for c2_i in c2)
    start = time.time()
    bqm = obj.compile().to_bqm(feed_dict={'L': 15})
    time_before_starting_annealer = time.time() - start
    print(f'{time_before_starting_annealer=}')

    res = SimulatedAnnealingSampler().sample(bqm, num_reads=100)

    # sampler = LeapHybridSampler(solver={'category': 'hybrid'}, token='')
    # res = sampler.sample(bqm)

    return res.first


def q_max_flow_big(graph: nx.DiGraph, source: int, target: int):
    lagrange = 10

    # fill with obj
    linear = {f'omega_{i}_{j}': cap["capacity"] for i, j, cap in graph.edges(data=True)}

    # fill with second constraints
    quadratic = {}
    for y_count, (i, j, cap) in enumerate(graph.edges(data=True)):
        quadratic[(f'pi_{i}', f'pi_{i}')] = 1 * lagrange
        quadratic[(f'pi_{j}', f'pi_{j}')] = 1 * lagrange
        quadratic[(f'omega_{i}_{j}', f'omega_{i}_{j}')] = 1 * lagrange
        quadratic[(f'y_2^0_{y_count}', f'y_2^0_{y_count}')] = 1 * lagrange
        quadratic[(f'y_2^1_{y_count}', f'y_2^1_{y_count}')] = 4 * lagrange
        quadratic[(f'pi_{i}', f'pi_{j}')] = -2 * lagrange
        quadratic[(f'pi_{i}', f'omega_{i}_{j}')] = 2 * lagrange
        quadratic[(f'pi_{i}', f'y_2^0_{y_count}')] = -2 * lagrange
        quadratic[(f'pi_{i}', f'y_2^1_{y_count}')] = -4 * lagrange
        quadratic[(f'pi_{j}', f'omega_{i}_{j}')] = -2 * lagrange
        quadratic[(f'pi_{j}', f'y_2^0_{y_count}')] = 2 * lagrange
        quadratic[(f'pi_{j}', f'y_2^1_{y_count}')] = 4 * lagrange
        quadratic[(f'omega_{i}_{j}', f'y_2^0_{y_count}')] = -2 * lagrange
        quadratic[(f'omega_{i}_{j}', f'y_2^1_{y_count}')] = -4 * lagrange
        quadratic[(f'y_2^0_{y_count}', f'y_2^1_{y_count}')] = 4 * lagrange

    # fill with first constraint
    quadratic[(f'pi_{target}', f'pi_{target}')] = 1 * lagrange
    quadratic[(f'pi_{source}', f'pi_{source}')] = 1 * lagrange
    quadratic[(f'pi_{target}', f'pi_{source}')] = -2 * lagrange  # cambio segno
    linear[f'pi_{target}'] = 0 * lagrange
    linear[f'pi_{source}'] = (len(graph.nodes) - 2) * lagrange

    for i in graph.nodes():
        if i != source and i != target:
            linear[f'pi_{i}'] = (graph.degree(i) - 1) * lagrange

    bqm = BinaryQuadraticModel(linear, quadratic, -1 * lagrange, 'BINARY')
    sampler = SimulatedAnnealingSampler()
    res = sampler.sample(bqm, num_reads=1)

    return res.first


def get_max_flow_from_cut_edges(graph, sample, var_name):
    cut_edges = {key: value for key, value in sample[0].items() if key.startswith(var_name) and value == 1}
    edges = set()
    for e in cut_edges:
        parts = e.split('_')
        edges.add((int(parts[1]), int(parts[2])))
    return sum(graph[i][j]['capacity'] for i, j in edges)
