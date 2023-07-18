import concurrent.futures
import networkx as nx
import os
from fnmatch import fnmatch
import shutil
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
                if vals[2] < 0:
                    return None, None, None, False
                g.add_edge(vals[0], vals[1], capacity=vals[2])
            elif line.startswith('n'):
                line = line.strip().split(' ')
                if line[2] == 's':
                    s = int(line[1])
                elif line[2] == 't':
                    t = int(line[1])
    return g, s, t, True


def check_graph(p):
    graph, source, target, is_valid = load_graph(p)
    if not is_valid:
        return
    max_flow_lib = nx.maximum_flow_value(graph, _s=source, _t=target)
    if max_flow_lib != 0:
        shutil.copy(p, f'./filtered/{p.split("/")[-1]}')


def main():
    timeout = 5
    paths = []
    for path, _, files in os.walk('./ready/'):
        paths.extend(os.path.join(path, name) for name in files if fnmatch(name, '*.max'))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for p in tqdm(paths):
            future = executor.submit(check_graph, p)

            try:
                _ = future.result(timeout=timeout)
            except concurrent.futures.TimeoutError:
                future.cancel()


if __name__ == "__main__":
    main()
