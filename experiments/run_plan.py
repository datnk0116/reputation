"""Thực nghiệm đúng theo kế hoạch gốc (giai đoạn C-D):
  - So sánh Random, Degree, Greedy trên cùng đồ thị, cùng k, cùng p.
  - p in {0.01, 0.05, 0.1}, k in {1, 3, 5, 10}.
  - Chọn seed bằng R snapshot (100-300); đánh giá nghiệm cuối bằng 1000 lần mô phỏng IC độc lập.
  - Lặp --repeats lần với random seed khác nhau; ghi spread trung bình, độ biến động, thời gian chạy.

Greedy chạy một lần tới k lớn nhất; nghiệm cho k nhỏ hơn là tiền tố của nó (Greedy tất định
nên kết quả y hệt chạy riêng từng k).
"""
import argparse
import time

import numpy as np
import pandas as pd
from common import ROOT, get_graph
from im import (Snapshots, edge_probs, simulate_ic, random_seeds, degree_seeds,
                greedy, top_degree_subgraph)

ap = argparse.ArgumentParser()
ap.add_argument("--data"); ap.add_argument("--labels")
ap.add_argument("--synthetic", type=int, default=0, help="n nút giả, CHỈ để thử code")
ap.add_argument("--subgraph", type=int, default=0, help="0 = đồ thị đầy đủ; N = N nút bậc cao nhất")
ap.add_argument("--ps", nargs="+", type=float, default=[0.01, 0.05, 0.1])
ap.add_argument("--ks", nargs="+", type=int, default=[1, 3, 5, 10])
ap.add_argument("--repeats", type=int, default=5, help="số lần lặp với random seed khác nhau")
ap.add_argument("--R", type=int, default=200, help="số snapshot dùng để CHỌN seed (100-300)")
ap.add_argument("--eval-runs", type=int, default=1000, help="số lần mô phỏng IC để ĐÁNH GIÁ")
ap.add_argument("--random-sets", type=int, default=10, help="số tập Random mỗi lần lặp (lấy trung bình)")
ap.add_argument("--out", default=str(ROOT / "results"))
a = ap.parse_args()

g = get_graph(a.data, a.labels, a.synthetic)
if a.subgraph:
    g = top_degree_subgraph(g, a.subgraph)
print(f"Graph: n={g.n}, m={g.m}, mean out-deg={g.m / g.n:.1f}")
kmax = max(a.ks)
rows = []
# khởi động numba (biên dịch JIT) trước khi đo thời gian, tránh tính vào lần chạy đầu
_w = Snapshots(g, edge_probs(g, "uniform:0.05"), 2, seed=0); _w.gain(0); _w.add(0)
simulate_ic(g, edge_probs(g, "uniform:0.05"), [0], 2)


def evaluate(probs, S, seed):
    x = simulate_ic(g, probs, S, a.eval_runs, rng_seed=seed)
    return float(x.mean()), float(x.std(ddof=1))  # trung bình và độ lệch chuẩn giữa các lần cascade


for p in a.ps:
    probs = edge_probs(g, f"uniform:{p}")
    for t in range(a.repeats):
        eval_seed = 10_000 + t                       # cùng seed đánh giá cho mọi thuật toán ở lần lặp t
        # --- Greedy ---
        snap = Snapshots(g, probs, a.R, seed=1000 + t)
        S_gr, info = greedy(snap, kmax)
        # --- Degree ---
        t0 = time.perf_counter(); S_deg = degree_seeds(g, kmax); t_deg = time.perf_counter() - t0
        # --- Random: nhiều tập, lấy trung bình trong lần lặp ---
        rng = np.random.default_rng(t)
        t0 = time.perf_counter()
        rand_sets = [random_seeds(g, kmax, rng) for _ in range(a.random_sets)]
        t_rand = (time.perf_counter() - t0) / a.random_sets
        for k in a.ks:
            m, sd = evaluate(probs, S_gr[:k], eval_seed)
            rows.append(dict(p=p, k=k, rep=t, algo="Greedy", spread=m, cascade_sd=sd, runtime=info["times"][k - 1]))
            m, sd = evaluate(probs, S_deg[:k], eval_seed)
            rows.append(dict(p=p, k=k, rep=t, algo="Degree", spread=m, cascade_sd=sd, runtime=t_deg))
            ev = [evaluate(probs, Sr[:k], eval_seed) for Sr in rand_sets]
            rows.append(dict(p=p, k=k, rep=t, algo="Random", spread=np.mean([e[0] for e in ev]),
                             cascade_sd=np.mean([e[1] for e in ev]), runtime=t_rand))
        print(f"p={p} lần lặp {t + 1}/{a.repeats} xong; Greedy {kmax} seed mất {info['time']:.1f}s")

pd.DataFrame(rows).to_csv(f"{a.out}/plan_raw.csv", index=False)
print("Đã lưu results/plan_raw.csv. Chạy tiếp: python summarize_plan.py")
