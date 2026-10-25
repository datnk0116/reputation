"""RQ1, RQ3, RQ4: so sánh Random / Degree / Greedy / CELF theo k và mô hình xác suất.

Quy trình (tách mẫu chọn và mẫu đánh giá):
  - chọn seed bằng R snapshot (seed RNG A)
  - đánh giá sigma bằng N_EVAL lần mô phỏng IC độc lập (seed RNG B)
"""
import argparse
import numpy as np
import pandas as pd
from common import ROOT, get_graph
from im import (Snapshots, edge_probs, simulate_ic, mean_ci,
                random_seeds, degree_seeds, greedy, celf)

ap = argparse.ArgumentParser()
ap.add_argument("--data"); ap.add_argument("--labels")
ap.add_argument("--synthetic", type=int, default=0, help="n nút tổng hợp (chỉ test)")
ap.add_argument("--models", nargs="+", default=["uniform:0.01", "uniform:0.05", "uniform:0.1", "wc"])
ap.add_argument("--kmax", type=int, default=20)
ap.add_argument("--ks", nargs="+", type=int, default=[1, 2, 3, 5, 10, 20])
ap.add_argument("--R", type=int, default=200, help="số snapshot dùng để CHỌN seed")
ap.add_argument("--eval-runs", type=int, default=1000, help="số lần mô phỏng IC để ĐÁNH GIÁ")
ap.add_argument("--random-reps", type=int, default=20)
ap.add_argument("--run-greedy", action="store_true", help="chạy thêm Greedy gốc (chậm) để so với CELF")
ap.add_argument("--greedy-kmax", type=int, default=10)
ap.add_argument("--out", default=str(ROOT / "results"))
a = ap.parse_args()

g = get_graph(a.data, a.labels, a.synthetic)
print(f"Graph: n={g.n}, m={g.m}, mean out-deg={g.m / g.n:.1f}")
rows, cost_rows, seed_rows = [], [], []

def evaluate(model, algo, probs, S, k, rep=0):
    m, ci = mean_ci(simulate_ic(g, probs, S, a.eval_runs, rng_seed=777 + rep))
    rows.append(dict(model=model, algo=algo, k=k, rep=rep, spread=m, ci95=ci))

for model in a.models:
    probs = edge_probs(g, model)
    print(f"\n== {model} ==")
    snap = Snapshots(g, probs, a.R, seed=1)

    S_celf, info = celf(snap, a.kmax)
    cost_rows.append(dict(model=model, algo="CELF", kmax=a.kmax, calls=info["calls"], time=info["time"]))
    seed_rows.append(dict(model=model, algo="CELF", seeds=S_celf, gains=info["gains"]))
    if a.run_greedy:
        km = min(a.greedy_kmax, a.kmax)
        S_gr, ig = greedy(snap, km)
        cost_rows.append(dict(model=model, algo="Greedy", kmax=km, calls=ig["calls"], time=ig["time"]))
        cost_rows.append(dict(model=model, algo="CELF", kmax=km, calls=celf(snap, km)[1]["calls"],
                              time=celf(snap, km)[1]["time"]))
        print("  Greedy == CELF (prefix)?", S_gr == S_celf[:km])

    S_deg = degree_seeds(g, a.kmax)
    seed_rows.append(dict(model=model, algo="Degree", seeds=S_deg, gains=None))
    rng = np.random.default_rng(2)
    rand_sets = [random_seeds(g, a.kmax, rng) for _ in range(a.random_reps)]

    for k in a.ks:
        if k > a.kmax: continue
        evaluate(model, "CELF(Greedy)", probs, S_celf[:k], k)
        evaluate(model, "Degree", probs, S_deg[:k], k)
        for rep, Sr in enumerate(rand_sets):
            evaluate(model, "Random", probs, Sr[:k], k, rep)
        r = [x for x in rows if x["model"] == model and x["k"] == k]
        print(f"  k={k:>2}: " + ", ".join(
            f"{al}={np.mean([x['spread'] for x in r if x['algo']==al]):.1f}"
            for al in ["CELF(Greedy)", "Degree", "Random"]))
    # đường cong marginal gain (cho hình 3) lưu trong seed_rows

pd.DataFrame(rows).to_csv(f"{a.out}/main_results.csv", index=False)
pd.DataFrame(cost_rows).to_csv(f"{a.out}/cost.csv", index=False)
pd.DataFrame(seed_rows).to_csv(f"{a.out}/seeds.csv", index=False)
print("\nĐã lưu main_results.csv, cost.csv, seeds.csv trong", a.out)
