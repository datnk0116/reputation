"""Nạp đồ thị và gán xác suất cạnh.

Đồ thị được lưu dạng mảng cạnh (src, dst) có hướng, nút đánh số lại 0..n-1.
Cạnh u -> v nghĩa là u có thể ảnh hưởng v (email u gửi cho v).
"""
from __future__ import annotations

import gzip
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass
class Graph:
    n: int
    src: np.ndarray  # (m,) int32
    dst: np.ndarray  # (m,) int32
    labels: np.ndarray | None = None  # nhãn phòng ban (nếu có), theo chỉ số mới
    orig_ids: np.ndarray | None = None  # id gốc của từng nút

    @property
    def m(self) -> int:
        return len(self.src)

    def out_degree(self) -> np.ndarray:
        return np.bincount(self.src, minlength=self.n)

    def in_degree(self) -> np.ndarray:
        return np.bincount(self.dst, minlength=self.n)


def _open(path):
    path = str(path)
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def load_edgelist(path, labels_path=None) -> Graph:
    """Đọc file 'u v' mỗi dòng (SNAP). Bỏ self-loop và cạnh trùng."""
    pairs = []
    with _open(path) as f:
        for line in f:
            if not line.strip() or line.startswith("#"):
                continue
            a, b = line.split()[:2]
            pairs.append((int(a), int(b)))
    arr = np.array(pairs, dtype=np.int64)
    arr = arr[arr[:, 0] != arr[:, 1]]
    arr = np.unique(arr, axis=0)
    ids, inv = np.unique(arr.ravel(), return_inverse=True)
    inv = inv.reshape(-1, 2)
    labels = None
    if labels_path is not None and Path(labels_path).exists():
        lab = {}
        with _open(labels_path) as f:
            for line in f:
                a, b = line.split()[:2]
                lab[int(a)] = int(b)
        labels = np.array([lab.get(int(i), -1) for i in ids])
    return Graph(len(ids), inv[:, 0].astype(np.int32), inv[:, 1].astype(np.int32), labels, ids)


def induced_subgraph(g: Graph, nodes: np.ndarray) -> Graph:
    """Đồ thị con cảm sinh trên tập nút `nodes` (đánh số lại)."""
    nodes = np.asarray(nodes)
    remap = -np.ones(g.n, dtype=np.int64)
    remap[nodes] = np.arange(len(nodes))
    keep = (remap[g.src] >= 0) & (remap[g.dst] >= 0)
    return Graph(
        len(nodes),
        remap[g.src[keep]].astype(np.int32),
        remap[g.dst[keep]].astype(np.int32),
        None if g.labels is None else g.labels[nodes],
        None if g.orig_ids is None else g.orig_ids[nodes],
    )


def top_degree_subgraph(g: Graph, size: int) -> Graph:
    """Lấy `size` nút có tổng bậc lớn nhất - dùng cho thí nghiệm brute-force."""
    deg = g.out_degree() + g.in_degree()
    return induced_subgraph(g, np.sort(np.argsort(-deg)[:size]))


def synthetic_graph(n=300, avg_deg=12, seed=0) -> Graph:
    """Đồ thị tổng hợp (preferential-attachment có hướng) để test khi chưa có dữ liệu thật."""
    rng = np.random.default_rng(seed)
    w = rng.pareto(2.0, n) + 1.0
    w /= w.sum()
    m = n * avg_deg
    s = rng.choice(n, m, p=w).astype(np.int32)
    d = rng.choice(n, m, p=w).astype(np.int32)
    keep = s != d
    arr = np.unique(np.stack([s[keep], d[keep]], 1), axis=0)
    return Graph(n, arr[:, 0].astype(np.int32), arr[:, 1].astype(np.int32))


# ---------- Mô hình xác suất cạnh ----------
def edge_probs(g: Graph, model: str) -> np.ndarray:
    """model: 'uniform:0.05' | 'wc' (weighted cascade, p = 1/in_degree(v))."""
    if model.startswith("uniform:"):
        return np.full(g.m, float(model.split(":")[1]))
    if model == "wc":
        indeg = g.in_degree().astype(float)
        return 1.0 / indeg[g.dst]
    raise ValueError(f"Unknown prob model: {model}")


def to_csr(n, src, dst, probs):
    order = np.argsort(src, kind="stable")
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(np.bincount(src, minlength=n), out=indptr[1:])
    return indptr, dst[order].astype(np.int32), probs[order].astype(np.float64)
