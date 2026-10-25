"""RQ2 (Greedy vs tối ưu tuyệt đối), RQ5 (kiểm tra submodular), độ nhạy theo R."""
import argparse
import numpy as np
import pandas as pd
from common import ROOT, get_graph
from im import Snapshots, edge_probs, top_degree_subgraph, celf, brute_force, simulate_ic, mean_ci

ap = argparse.ArgumentParser()
ap.add_argument("--data"); ap.add_argument("--labels")
ap.add_argument("--synthetic", type=int, default=0)
ap.add_argument("--models", nargs="+", default=["uniform:0.05", "uniform:0.1", "wc"])
ap.add_argument("--sub-size", type=int, default=35, help="số nút đồ thị con cho brute-force")
ap.add_argument("--R", type=int, default=300)
ap.add_argument("--submod-trials", type=int, default=2000)
ap.add_argument("--out", default=str(ROOT / "results"))
a = ap.parse_args()
g = get_graph(a.data, a.labels, a.synthetic)

# ---- RQ2: Greedy / OPT trên đồ thị con nhỏ ----
sub = top_degree_subgraph(g, a.sub_size)
print(f"Subgraph: n={sub.n}, m={sub.m}")
rows = []
for model in a.models:
    probs = edge_probs(sub, model)
    snap = Snapshots(sub, probs, a.R, seed=1)
    for k in (1, 2, 3):
        S_g, ig = celf(snap, k)
        S_o, io = brute_force(snap, k)
        gv = snap.spread(S_g)
        rows.append(dict(model=model, k=k, greedy=gv, opt=io["value"], ratio=gv / io["value"],
                         bound=1 - 1 / np.e, greedy_seeds=S_g, opt_seeds=S_o))
        print(f"{model:>13} k={k}: greedy={gv:.3f} opt={io['value']:.3f} ratio={gv/io['value']:.4f}")
pd.DataFrame(rows).to_csv(f"{a.out}/bruteforce.csv", index=False)

# ---- RQ5: kiểm tra submodular & đơn điệu trên đồ thị đầy đủ ----
rng = np.random.default_rng(5)
rows = []
for model in a.models:
    snap = Snapshots(g, edge_probs(g, model), 100, seed=3)
    viol = mono_viol = 0
    for _ in range(a.submod_trials):
        t = int(rng.integers(2, 12))
        T = list(rng.choice(g.n, t, replace=False))
        S = T[: int(rng.integers(1, t))]           # S ⊂ T
        v = int(rng.choice([x for x in range(g.n) if x not in T]))
        sS, sSv = snap.spread(S), snap.spread(S + [v])
        sT, sTv = snap.spread(T), snap.spread(T + [v])
        if (sSv - sS) < (sTv - sT) - 1e-9: viol += 1
        if sSv < sS - 1e-9: mono_viol += 1
    rows.append(dict(model=model, trials=a.submod_trials, submodular_violations=viol, monotone_violations=mono_viol))
    print(f"{model}: vi phạm submodular {viol}/{a.submod_trials}, đơn điệu {mono_viol}")
pd.DataFrame(rows).to_csv(f"{a.out}/submodular_check.csv", index=False)

# ---- Độ nhạy theo R: chọn seed bằng R nhỏ/lớn rồi đánh giá độc lập ----
model, k = a.models[-1], 5
probs = edge_probs(g, model)
rows = []
for R in (10, 30, 100, 300):
    for rep in range(5):
        S, _ = celf(Snapshots(g, probs, R, seed=100 + rep), k)
        m, _ = mean_ci(simulate_ic(g, probs, S, 1000, rng_seed=9))
        rows.append(dict(model=model, k=k, R=R, rep=rep, spread=m))
    print(f"R={R}: spread={np.mean([r['spread'] for r in rows if r['R']==R]):.2f}")
pd.DataFrame(rows).to_csv(f"{a.out}/sensitivity_R.csv", index=False)
