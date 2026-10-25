"""Tổng hợp plan_raw.csv thành bảng (markdown + CSV) và hình cho slide."""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from common import ROOT

R = ROOT / "results"; F = R / "figs"; F.mkdir(exist_ok=True)
raw = pd.read_csv(R / "plan_raw.csv")
T = raw.rep.nunique()

# ---- Bảng tổng hợp: trung bình, độ lệch chuẩn giữa các lần lặp, độ biến động cascade, thời gian ----
agg = raw.groupby(["p", "k", "algo"]).agg(
    spread_mean=("spread", "mean"), spread_sd=("spread", "std"),
    cascade_sd=("cascade_sd", "mean"), runtime=("runtime", "mean")).reset_index()
agg.to_csv(R / "plan_summary.csv", index=False)

# ---- Greedy so với từng baseline: chênh lệch theo cặp (cùng lần lặp), khoảng tin cậy 95% ----
diff_rows = []
for (p, k), d in raw.groupby(["p", "k"]):
    pv = d.pivot(index="rep", columns="algo", values="spread")
    for base in ["Degree", "Random"]:
        x = (pv["Greedy"] - pv[base]).values
        half = stats.t.ppf(0.975, T - 1) * x.std(ddof=1) / np.sqrt(T) if T > 1 else np.nan
        diff_rows.append(dict(p=p, k=k, baseline=base, diff_mean=x.mean(), ci95=half,
                              rel_gain_pct=100 * x.mean() / pv[base].mean(),
                              significant=bool(abs(x.mean()) > half) if T > 1 else None))
diff = pd.DataFrame(diff_rows)
diff.to_csv(R / "plan_diff.csv", index=False)

# ---- Markdown ----
md = [f"# Kết quả thực nghiệm ({T} lần lặp)\n"]
for p in sorted(agg.p.unique()):
    md.append(f"\n## p = {p}: σ(S) trung bình ± độ lệch chuẩn giữa các lần lặp\n")
    ks = sorted(agg.k.unique())
    md.append("| Thuật toán | " + " | ".join(f"k={k}" for k in ks) + " |")
    md.append("|---|" + "---|" * len(ks))
    for algo in ["Random", "Degree", "Greedy"]:
        cells = []
        for k in ks:
            r = agg[(agg.p == p) & (agg.k == k) & (agg.algo == algo)].iloc[0]
            cells.append(f"{r.spread_mean:.1f} ± {r.spread_sd:.1f}")
        md.append(f"| {algo} | " + " | ".join(cells) + " |")
    md.append(f"\nGreedy so với Degree (hiệu theo cặp, ± KTC 95%; * = khác biệt có ý nghĩa):\n")
    md.append("| k | Greedy − Degree | tăng tương đối | Greedy − Random |")
    md.append("|---|---|---|---|")
    for k in ks:
        d1 = diff[(diff.p == p) & (diff.k == k) & (diff.baseline == "Degree")].iloc[0]
        d2 = diff[(diff.p == p) & (diff.k == k) & (diff.baseline == "Random")].iloc[0]
        star = "*" if d1.significant else ""
        md.append(f"| {k} | {d1.diff_mean:+.1f} ± {d1.ci95:.1f}{star} | {d1.rel_gain_pct:+.1f}% | {d2.diff_mean:+.1f} ± {d2.ci95:.1f} |")
    md.append(f"\nThời gian chọn seed (giây) và độ biến động giữa các cascade (độ lệch chuẩn của một lần mô phỏng):\n")
    md.append("| Thuật toán | " + " | ".join(f"k={k}" for k in ks) + " |")
    md.append("|---|" + "---|" * len(ks))
    for algo in ["Random", "Degree", "Greedy"]:
        cells = []
        for k in ks:
            r = agg[(agg.p == p) & (agg.k == k) & (agg.algo == algo)].iloc[0]
            cells.append(f"{r.runtime:.3g}s / sd {r.cascade_sd:.1f}")
        md.append(f"| {algo} | " + " | ".join(cells) + " |")
(R / "plan_table.md").write_text("\n".join(md), encoding="utf-8")

# ---- Hình 1: σ theo k (mỗi p một panel) ----
ps = sorted(agg.p.unique())
col = {"Random": ("tab:gray", "^"), "Degree": ("tab:orange", "s"), "Greedy": ("tab:blue", "o")}
fig, ax = plt.subplots(1, len(ps), figsize=(4.3 * len(ps), 3.6), squeeze=False)
for a_, p in zip(ax[0], ps):
    for algo, (c, mk) in col.items():
        d = agg[(agg.p == p) & (agg.algo == algo)]
        a_.errorbar(d.k, d.spread_mean, yerr=d.spread_sd.fillna(0), color=c, marker=mk, label=algo, capsize=3)
    a_.set_title(f"p = {p}"); a_.set_xlabel("k (số seed)"); a_.set_ylabel("σ(S) kỳ vọng"); a_.grid(alpha=.3)
ax[0][0].legend()
plt.tight_layout(); plt.savefig(F / "plan_fig1_spread_vs_k.png", dpi=200); plt.close()

# ---- Hình 2: thời gian chạy Greedy theo k ----
plt.figure(figsize=(4.8, 3.5))
for p in ps:
    d = agg[(agg.p == p) & (agg.algo == "Greedy")]
    plt.plot(d.k, d.runtime, marker="o", label=f"p = {p}")
plt.xlabel("k"); plt.ylabel("thời gian Greedy (s)"); plt.grid(alpha=.3); plt.legend()
plt.tight_layout(); plt.savefig(F / "plan_fig2_runtime.png", dpi=200); plt.close()
print("Đã tạo results/plan_table.md, plan_summary.csv, plan_diff.csv và hình trong results/figs/")
