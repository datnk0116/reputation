# Influence Maximization — phần thực nghiệm (TV2: slide 3 & 4)

Bài báo: Kempe, Kleinberg, Tardos — *Maximizing the Spread of Influence through a Social Network*.
Code này tạo **bằng chứng tính toán** cho phần Triển khai/Thực nghiệm/Kết luận. Không phải phần mềm hoàn chỉnh.

## Chạy nhanh
```bash
pip install -r requirements.txt
./download_data.sh                     # tải SNAP Email-Eu-core vào data/
python -m pytest -q                    # test ví dụ 4 nút (σ({A})=1,75; σ({A,B})=3,125)
cd experiments
python run_main.py --run-greedy        # RQ1, RQ3, RQ4  -> results/main_results.csv, cost.csv, seeds.csv
python run_extra.py                    # RQ2 (brute-force), RQ5 (submodular), độ nhạy R
python plot.py                         # -> results/figs/fig1..fig4
```
Chưa có dữ liệu thì thêm `--synthetic 1005` để thử code (đồ thị giả, KHÔNG dùng số liệu này để báo cáo).
Cấu hình nhẹ để thử: `--R 100 --eval-runs 300 --random-reps 5`. Cấu hình báo cáo: mặc định (R=200, 1000 lần đánh giá).

## Cấu trúc
| File | Vai trò |
|---|---|
| `src/im/graph.py` | nạp SNAP, đồ thị con, mô hình p (`uniform:0.05`, `wc` = 1/in-degree) |
| `src/im/ic.py` | `simulate_ic` (IC đúng định nghĩa, để **đánh giá**) và `Snapshots` (live-edge, để **chọn seed**) |
| `src/im/algos.py` | Random, Degree, **Greedy**, **CELF**, brute-force |
| `experiments/run_main.py` | σ theo k cho mọi thuật toán × mô hình p; chi phí Greedy vs CELF |
| `experiments/run_extra.py` | Greedy/OPT, kiểm tra submodular & đơn điệu, độ nhạy R |
| `experiments/plot.py` | 4 hình cho slide |
| `tests/test_toy.py` | đối chiếu ví dụ tính tay + Greedy == CELF |

## Thiết kế thí nghiệm (nói được khi bảo vệ)
- **Tách mẫu chọn / mẫu đánh giá:** chọn seed bằng R live-edge snapshot; đánh giá bằng mô phỏng IC độc lập (seed RNG khác). Nếu đánh giá trên chính mẫu đã chọn, Greedy bị lạc quan.
- **Vì sao snapshot:** dùng chung R đồ thị sống cho mọi ứng viên → σ̂ vẫn đơn điệu + submodular → Greedy và CELF cho kết quả giống hệt (đã test).
- **CELF:** do submodular, Δ cũ là cận trên của Δ mới ⇒ chỉ tính lại phần tử đầu heap.
- **Các chế độ p:** bậc ra trung bình Email-Eu-core ≈ 25 ⇒ p=0,01 (yếu, ~0,25), 0,05 (≈ ngưỡng tới hạn), 0,1 (bùng nổ). Ở p lớn các thuật toán tiệm cận nhau vì cascade phủ gần hết thành phần liên thông lớn.
- **Cận 1−1/e** là trường hợp xấu nhất; thực tế Greedy/OPT thường ≈ 0,95–1,0.
- **Hạn chế cần nói:** email ≠ sức ảnh hưởng thật; p là giả định; Email-Eu-core không phải dữ liệu của bài báo gốc.

## Việc nên làm tiếp
1. Chạy trên dữ liệu thật, điền số vào slide 3–4 (hiện `results/` đang trống, cố ý).
2. Thêm baseline mạnh hơn: Degree Discount, PageRank (viết thêm trong `algos.py`, thêm 1 dòng trong `run_main.py`).
3. Phân tích định tính: seed Greedy có trùng nút bậc cao không? Có rải nhiều phòng ban không? (`g.labels` đã nạp sẵn).
4. Thêm mô hình Linear Threshold nếu GV hỏi (bài báo có xét).
5. Đối chiếu kết quả với lý thuyết: Greedy/OPT ≥ 0,632; Δ giảm dần (fig3); vi phạm submodular = 0.
