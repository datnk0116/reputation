"""Các thuật toán chọn seed. Tất cả trả về (seeds, info) với seeds theo thứ tự chọn."""
from __future__ import annotations

import heapq
import itertools
import time

import numpy as np

from .graph import Graph
from .ic import Snapshots


def random_seeds(g: Graph, k: int, rng: np.random.Generator):
    return list(rng.choice(g.n, k, replace=False))


def degree_seeds(g: Graph, k: int):
    """High-Degree: k nút có bậc ra lớn nhất (hòa thì lấy chỉ số nhỏ)."""
    deg = g.out_degree()
    return list(np.lexsort((np.arange(g.n), -deg))[:k])


def greedy(snap: Snapshots, k: int):
    """Greedy gốc của Kempe: mỗi vòng duyệt MỌI nút còn lại, chọn Δ lớn nhất.
    info['curve'][i] = sigma_hat sau khi chọn i+1 seed; info['gains'] = Δ từng vòng."""
    snap.reset()
    snap.n_gain_calls = 0
    t0 = time.perf_counter()
    S, gains, curve = [], [], []
    chosen = np.zeros(snap.n, dtype=bool)
    for _ in range(k):
        best_v, best_g = -1, -1.0
        for v in range(snap.n):
            if chosen[v]:
                continue
            gv = snap.gain(v)
            if gv > best_g:
                best_v, best_g = v, gv
        snap.add(best_v)
        chosen[best_v] = True
        S.append(best_v); gains.append(best_g); curve.append(snap.sigma)
    return S, dict(gains=gains, curve=curve, calls=snap.n_gain_calls,
                   time=time.perf_counter() - t0)


def celf(snap: Snapshots, k: int):
    """CELF (lazy greedy, Leskovec 2007). Nhờ submodular, Δ cũ là cận trên của Δ mới,
    nên chỉ cần tính lại phần tử đầu heap. Cho CÙNG kết quả với greedy (cùng snapshots)."""
    snap.reset()
    snap.n_gain_calls = 0
    t0 = time.perf_counter()
    heap = [(-snap.gain(v), v, 0) for v in range(snap.n)]  # (-Δ, v, vòng tính Δ)
    heapq.heapify(heap)
    S, gains, curve = [], [], []
    while len(S) < k:
        negg, v, last = heapq.heappop(heap)
        if last == len(S):          # Δ đã cập nhật ở vòng hiện tại -> chắc chắn lớn nhất
            snap.add(v)
            S.append(v); gains.append(-negg); curve.append(snap.sigma)
        else:
            heapq.heappush(heap, (-snap.gain(v), v, len(S)))
    return S, dict(gains=gains, curve=curve, calls=snap.n_gain_calls,
                   time=time.perf_counter() - t0)


def brute_force(snap: Snapshots, k: int):
    """Tối ưu tuyệt đối theo sigma_hat (chỉ dùng cho đồ thị nhỏ, k nhỏ)."""
    best, best_S = -1.0, None
    for S in itertools.combinations(range(snap.n), k):
        val = snap.spread(S)
        if val > best:
            best, best_S = val, list(S)
    return best_S, dict(value=best)
