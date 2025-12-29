import json
import networkx as nx

def load_dependency_graph(path):
    with open(path) as f:
        deps = json.load(f)

    graph = nx.DiGraph()

    for service, dependencies in deps.items():
        graph.add_node(service)
        for dep in dependencies:
            graph.add_edge(dep, service)  # dep → service

    return graph
