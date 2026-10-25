"""Kiểm tra bằng ví dụ 4 nút tính tay trong báo cáo: A->C, B->C, C->D, p=0.5."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import numpy as np
from im import Graph, Snapshots, simulate_ic, celf, brute_force

A, B, C, D = 0, 1, 2, 3
G = Graph(4, np.array([A, B, C], dtype=np.int32), np.array([C, C, D], dtype=np.int32))
P = np.full(3, 0.5)


def test_sigma_single_by_ic():
    assert abs(simulate_ic(G, P, [A], 200000).mean() - 1.75) < 0.02


def test_sigma_pair_by_ic():
    assert abs(simulate_ic(G, P, [A, B], 200000).mean() - 3.125) < 0.02


def test_snapshots_match_hand_calc():
    s = Snapshots(G, P, 20000, seed=1)
    assert abs(s.spread([A]) - 1.75) < 0.03
    assert abs(s.spread([A, B]) - 3.125) < 0.03


def test_greedy_picks_A_B_and_is_optimal():
    s = Snapshots(G, P, 5000, seed=2)
    S, _ = celf(s, 2)
    assert set(S) == {A, B}
    assert set(brute_force(s, 2)[0]) == {A, B}


def test_greedy_equals_celf():
    from im import greedy, synthetic_graph, edge_probs
    g = synthetic_graph(80, 6, 1)
    s = Snapshots(g, edge_probs(g, "uniform:0.1"), 60, seed=3)
    assert greedy(s, 5)[0] == celf(s, 5)[0]
