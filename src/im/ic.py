"""Independent Cascade: mô phỏng trực tiếp + ước lượng sigma bằng live-edge snapshots.

Hai cách tương đương nhau về kỳ vọng (chứng minh trong bài báo, §live-edge):
  1. simulate_ic: mô phỏng đúng định nghĩa IC (dùng để ĐÁNH GIÁ độc lập).
  2. Snapshots: tung xúc xắc mỗi cạnh một lần, được R "đồ thị sống"; sigma(S) = số nút
     tới được từ S, trung bình trên R đồ thị. Dùng chung R mẫu cho mọi ứng viên nên
     sigma_hat vẫn đơn điệu + submodular -> Greedy/CELF nhất quán (dùng để CHỌN seed).
"""
from __future__ import annotations

import numpy as np
from numba import njit

from .graph import Graph, to_csr


# ---------------- Mô phỏng IC thuần ----------------
@njit(cache=True)
def _ic_once(indptr, indices, probs, seeds, active, queue):
    """Một lần cascade. Trả về số nút kích hoạt. `active` là mảng bool dùng lại."""
    n = len(active)
    active[:] = False
    head = 0
    tail = 0
    for s in seeds:
        if not active[s]:
            active[s] = True
            queue[tail] = s
            tail += 1
    while head < tail:
        u = queue[head]
        head += 1
        for e in range(indptr[u], indptr[u + 1]):
            v = indices[e]
            if not active[v] and np.random.random() < probs[e]:
                active[v] = True
                queue[tail] = v
                tail += 1
    return tail


@njit(cache=True)
def _ic_many(indptr, indices, probs, seeds, runs, rng_seed):
    np.random.seed(rng_seed)
    n = len(indptr) - 1
    active = np.zeros(n, dtype=np.bool_)
    queue = np.empty(n, dtype=np.int64)
    out = np.empty(runs, dtype=np.int64)
    for i in range(runs):
        out[i] = _ic_once(indptr, indices, probs, seeds, active, queue)
    return out


def simulate_ic(g: Graph, probs: np.ndarray, seeds, runs=1000, rng_seed=12345):
    """Chạy IC `runs` lần độc lập. Trả về mảng số nút được kích hoạt mỗi lần."""
    indptr, indices, p = to_csr(g.n, g.src, g.dst, probs)
    return _ic_many(indptr, indices, p, np.asarray(list(seeds), dtype=np.int64), runs, rng_seed)


def mean_ci(samples):
    """Trung bình và nửa độ rộng khoảng tin cậy 95%."""
    s = np.asarray(samples, dtype=float)
    return s.mean(), 1.96 * s.std(ddof=1) / np.sqrt(len(s)) if len(s) > 1 else 0.0


# ---------------- Live-edge snapshots ----------------
@njit(cache=True)
def _gain2(indptr, indices, reached, stamp, cur, v, n, R, commit):
    """Giống _gain nhưng stack lưu chỉ số toàn cục; nếu commit=True thì đánh dấu reached."""
    total = 0
    stack = np.empty(n, dtype=np.int64)
    for r in range(R):
        base = r * n
        s = base + v
        if reached[s]:
            continue
        sp = 0
        stack[0] = s
        sp = 1
        stamp[s] = cur
        total += 1
        while sp > 0:
            sp -= 1
            u = stack[sp]
            if commit:
                reached[u] = True
            for e in range(indptr[u], indptr[u + 1]):
                w = indices[e]
                if not reached[w] and stamp[w] != cur:
                    stamp[w] = cur
                    total += 1
                    stack[sp] = w
                    sp += 1
    return total


class Snapshots:
    """R live-edge snapshots gộp thành một CSR lớn (nút (r,u) -> r*n+u)."""

    def __init__(self, g: Graph, probs: np.ndarray, R: int, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.n, self.R = g.n, R
        srcs, dsts = [], []
        for r in range(R):
            keep = rng.random(g.m) < probs
            srcs.append(g.src[keep].astype(np.int64) + r * g.n)
            dsts.append(g.dst[keep].astype(np.int64) + r * g.n)
        src = np.concatenate(srcs)
        dst = np.concatenate(dsts)
        N = g.n * R
        order = np.argsort(src, kind="stable")
        self.indptr = np.zeros(N + 1, dtype=np.int64)
        np.cumsum(np.bincount(src, minlength=N), out=self.indptr[1:])
        self.indices = dst[order]
        self.reset()
        self.n_gain_calls = 0  # đếm số lần đánh giá lợi ích biên (để so Greedy vs CELF)

    def reset(self):
        N = self.n * self.R
        self.reached = np.zeros(N, dtype=np.bool_)
        self._stamp = np.zeros(N, dtype=np.int64)
        self._cur = 0
        self.value = 0  # tổng nút tới được hiện tại (chia R để ra sigma_hat)

    def gain(self, v: int) -> float:
        """Δ(v | S) ước lượng, với S là tập đã `add`."""
        self._cur += 1
        self.n_gain_calls += 1
        t = _gain2(self.indptr, self.indices, self.reached, self._stamp, self._cur,
                   int(v), self.n, self.R, False)
        return t / self.R

    def add(self, v: int) -> float:
        """Thêm v vào S, trả về Δ."""
        self._cur += 1
        t = _gain2(self.indptr, self.indices, self.reached, self._stamp, self._cur,
                   int(v), self.n, self.R, True)
        self.value += t
        return t / self.R

    @property
    def sigma(self) -> float:
        return self.value / self.R

    def spread(self, seeds) -> float:
        """sigma_hat(S) tính từ đầu (reset rồi thêm từng seed)."""
        self.reset()
        for v in seeds:
            self.add(v)
        return self.sigma
