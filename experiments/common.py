import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from im import load_edgelist, synthetic_graph  # noqa: E402


def get_graph(data=None, labels=None, synthetic_n=0):
    """--data tới file edge list SNAP; nếu không có thì dùng đồ thị tổng hợp (chỉ để test code)."""
    if synthetic_n:
        print(f"[!] DÙNG ĐỒ THỊ TỔNG HỢP n={synthetic_n} - KHÔNG phải dữ liệu thật")
        return synthetic_graph(synthetic_n, 12, 0)
    data = data or ROOT / "data" / "email-Eu-core.txt.gz"
    labels = labels or ROOT / "data" / "email-Eu-core-department-labels.txt.gz"
    return load_edgelist(data, labels)
