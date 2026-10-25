"""Influence Maximization (Kempe-Kleinberg-Tardos) - experiment toolkit."""
from .graph import (Graph, load_edgelist, synthetic_graph, edge_probs,
                    induced_subgraph, top_degree_subgraph)
from .ic import Snapshots, simulate_ic, mean_ci
from .algos import random_seeds, degree_seeds, greedy, celf, brute_force
