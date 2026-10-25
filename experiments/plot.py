"""Vẽ các hình cho slide từ CSV trong results/."""
import ast
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from common import ROOT

R = ROOT / "results"; F = R / "figs"; F.mkdir(exist_ok=True)
STYLE = {"CELF(Greedy)": ("tab:blue", "o"), "Degree": ("tab:orange", "s"), "Random": ("tab:gray", "^")}

df = pd.read_csv(R / "main_results.csv")
models = list(dict.fromkeys(df.model))
# Hình 1: sigma theo k, mỗi mô hình một panel
fig, ax = plt.subplots(1, len(models), figsize=(4.2 * len(models), 3.6), squeeze=False)
for a_, model in zip(ax[0], models):
    for algo, (c, mk) in STYLE.items():
        d = df[(df.model == model) & (df.algo == algo)].groupby("k").spread.agg(["mean", "std"]).reset_index()
        a_.errorbar(d.k, d["mean"], yerr=d["std"].fillna(0), color=c, marker=mk, label=algo, capsize=3)
    a_.set_title(model); a_.set_xlabel("k (số seed)"); a_.set_ylabel("σ(S) kỳ vọng"); a_.grid(alpha=.3)
ax[0][0].legend()
plt.tight_layout(); plt.savefig(F / "fig1_spread_vs_k.png", dpi=200); plt.close()

# Hình 2: chi phí Greedy vs CELF
try:
    c = pd.read_csv(R / "cost.csv"); c = c[c.algo.isin(["Greedy", "CELF"])]
    c = c[c.kmax == c.groupby("model").kmax.transform("min")] if c.algo.nunique() > 1 else c
    if (c.algo == "Greedy").any():
        p = c.pivot_table(index="model", columns="algo", values=["calls", "time"])
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
        for a_, key, lab in zip(ax, ["calls", "time"], ["số lần tính Δ", "thời gian (s)"]):
            p[key].plot.bar(ax=a_, logy=True, rot=0); a_.set_ylabel(lab); a_.set_xlabel("")
        plt.tight_layout(); plt.savefig(F / "fig2_greedy_vs_celf.png", dpi=200); plt.close()
except Exception as e:
    print("skip fig2:", e)

# Hình 3: marginal gain giảm dần
sd = pd.read_csv(R / "seeds.csv"); sd = sd[sd.algo == "CELF"]
plt.figure(figsize=(5, 3.6))
for _, r in sd.iterrows():
    gains = ast.literal_eval(r.gains); plt.plot(range(1, len(gains) + 1), gains, marker="o", label=r.model)
plt.xlabel("vòng chọn i"); plt.ylabel("Δ(v_i | S_{i-1})"); plt.yscale("log"); plt.grid(alpha=.3); plt.legend()
plt.tight_layout(); plt.savefig(F / "fig3_marginal_gain.png", dpi=200); plt.close()

# Hình 4: độ nhạy theo R
try:
    s = pd.read_csv(R / "sensitivity_R.csv").groupby("R").spread.agg(["mean", "std"]).reset_index()
    plt.figure(figsize=(4.5, 3.4)); plt.errorbar(s.R, s["mean"], yerr=s["std"], marker="o", capsize=3)
    plt.xscale("log"); plt.xlabel("R (số snapshot khi chọn)"); plt.ylabel("σ đánh giá độc lập"); plt.grid(alpha=.3)
    plt.tight_layout(); plt.savefig(F / "fig4_sensitivity_R.png", dpi=200); plt.close()
except Exception as e:
    print("skip fig4:", e)
print("Hình lưu trong", F)
