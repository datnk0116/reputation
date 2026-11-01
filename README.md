# Influence Maximization — phần thực nghiệm (TV2: slide 3 & 4)

Bài báo: Kempe, Kleinberg, Tardos — *Maximizing the Spread of Influence through a Social Network*.
Code này tạo **bằng chứng tính toán** cho phần Triển khai/Thực nghiệm/Kết luận. Không phải phần mềm hoàn chỉnh.

## Chạy nhanh
Các lệnh thực nghiệm chính thức được thực hiện như sau (lưu ý: các lệnh chạy kịch bản chạy từ thư mục `experiments/`):
```bash
pip install -r requirements.txt
./download_data.sh                     # tải SNAP Email-Eu-core vào data/
python -m pytest -q                    # test ví dụ 4 nút (σ({A})=1,75; σ({A,B})=3,125)
cd experiments
python run_plan.py --repeats 5 --R 200 --eval-runs 1000 --random-sets 10
python summarize_plan.py
```
Chưa có dữ liệu thì thêm `--synthetic 1005` vào `run_plan.py` để thử code (đồ thị giả, KHÔNG dùng số liệu này để báo cáo).

*(Tuỳ chọn)* Chạy lại các phân tích thăm dò bổ sung (CELF, brute-force, submodular, mô hình `wc`). Lưu ý: các script này mặc định ghi kết quả ra `results/`, các kết quả thăm dò sẵn có hiện được lưu trữ tách biệt tại `results/exploratory/`:
```bash
python run_main.py --run-greedy        # RQ1, RQ3, RQ4 -> ghi ra results/main_results.csv, cost.csv, seeds.csv
python run_extra.py                    # RQ2 (brute-force), RQ5 (submodular), độ nhạy R
python plot.py                         # vẽ fig1..fig4 -> ghi ra results/figs/
```

## Dữ liệu và tiền xử lý
- **Tập dữ liệu:** SNAP Email-Eu-core (mạng lưới trao đổi email tại một viện nghiên cứu lớn của châu Âu).
- **Tiền xử lý:** Sau khi loại bỏ các vòng lặp bản thân (self-loop) và các nút cô lập (isolated nodes), đồ thị thu được gồm **986 nút**, **24.929 cạnh có hướng**, với bậc ra trung bình là **25.3**.
- **Lưu ý:** Dữ liệu thực tế không chứa xác suất ảnh hưởng giữa các cá nhân, vì vậy xác suất lan truyền $p \in \{0.01, 0.05, 0.1\}$ là giả định thực nghiệm. Đồng thời, đây không phải tập dữ liệu trong bài báo gốc của Kempe et al. (bài báo gốc dùng mạng đồng tác giả arXiv High Energy Physics).

## Giao thức đánh giá
- **Chọn seed:** Dùng tập live-edge snapshots ($R=200$) để tối ưu hóa chọn tập seed $S$ với $k \in \{1, 3, 5, 10\}$ theo mô hình Independent Cascade (IC).
- **Đánh giá độc lập:** Đánh giá mức độ lan truyền $\sigma(S)$ bằng $1000$ lần mô phỏng IC độc lập với seed ngẫu nhiên khác (tách biệt mẫu chọn và mẫu đánh giá để tránh thiên lệch lạc quan).
- **Thử nghiệm lặp lại:** Thực hiện $5$ lần lặp độc lập (repeats); ở mỗi lần lặp, baseline Random được lấy trung bình từ $10$ tập seed ngẫu nhiên.
- **Kiểm định thống kê:** Chênh lệch Greedy − Degree được tính theo từng cặp (paired difference) trong từng lần lặp; khoảng tin cậy 95% tính theo phân phối Student's $t$ ($df=4$); đánh dấu `*` khi khác biệt có ý nghĩa thống kê ($\alpha = 0.05$).

## Ánh xạ file kết quả chính thức
Các file kết quả chính thức phục vụ báo cáo và slide được lưu trực tiếp trong thư mục `results/`:

| File | Ý nghĩa |
|---|---|
| `results/plan_table.md` | Bảng tổng hợp Markdown cho slide & báo cáo: $\sigma(S)$ trung bình $\pm$ độ lệch chuẩn giữa các lần lặp, chênh lệch theo cặp Greedy − Degree (kèm KTC 95%, dấu `*`), thời gian chạy và độ biến động cascade |
| `results/plan_summary.csv` | Tóm tắt thống kê theo từng cấu hình $(p, k, \text{algo})$ (spread trung bình, std giữa các lần lặp, cascade std, runtime) |
| `results/plan_diff.csv` | Chênh lệch theo cặp Greedy − Degree và Greedy − Random qua các lần lặp, khoảng tin cậy 95%, tỷ lệ tăng tương đối và cờ ý nghĩa thống kê |
| `results/plan_raw.csv` | Mỗi dòng là trung bình 1000 lần mô phỏng IC cho một (p, k, thuật toán, lần lặp); riêng với Random là trung bình qua 10 tập seed ngẫu nhiên, mỗi tập chấm bằng 1000 lần mô phỏng |
| `results/figs/plan_fig1_spread_vs_k.png` | Biểu đồ so sánh độ lan truyền $\sigma(S)$ theo $k$ giữa Random, Degree và Greedy trên 3 giá trị $p$ (3 panel) |
| `results/figs/plan_fig2_runtime.png` | Biểu đồ thời gian chạy (runtime) của Greedy theo $k$ ứng với các mức $p$ khác nhau |

*(Các kết quả thăm dò cũ như `main_results.csv`, `cost.csv`, `seeds.csv`, `bruteforce.csv`, `submodular_check.csv`, `sensitivity_R.csv` và `fig1..fig4` đã được chuyển vào `results/exploratory/`).*

## Cấu trúc
| File | Vai trò |
|---|---|
| `src/im/graph.py` | nạp SNAP, đồ thị con, mô hình p (`uniform:0.05`, `wc` = 1/in-degree) |
| `src/im/ic.py` | `simulate_ic` (IC đúng định nghĩa, để **đánh giá**) và `Snapshots` (live-edge, để **chọn seed**) |
| `src/im/algos.py` | Random, Degree, **Greedy**, **CELF**, brute-force |
| `experiments/run_plan.py` | Thực nghiệm chính thức: so sánh Random, Degree, Greedy qua các lần lặp theo kế hoạch -> `results/plan_raw.csv` |
| `experiments/summarize_plan.py` | Tổng hợp `plan_raw.csv` thành bảng markdown, CSV và biểu đồ chính thức -> `results/plan_table.md`, `results/plan_*.csv`, `results/figs/plan_fig*.png` |
| `experiments/run_main.py` | Thực nghiệm thăm dò: σ theo k cho mọi thuật toán × mô hình p; chi phí Greedy vs CELF |
| `experiments/run_extra.py` | Thực nghiệm thăm dò: Greedy/OPT, kiểm tra submodular & đơn điệu, độ nhạy R |
| `experiments/plot.py` | Vẽ 4 hình cho thực nghiệm thăm dò |
| `tests/test_toy.py` | đối chiếu ví dụ tính tay + Greedy == CELF |

## Thiết kế thí nghiệm (nói được khi bảo vệ)
- **Tách mẫu chọn / mẫu đánh giá:** chọn seed bằng R live-edge snapshot; đánh giá bằng mô phỏng IC độc lập (seed RNG khác). Nếu đánh giá trên chính mẫu đã chọn, Greedy bị lạc quan.
- **Vì sao snapshot:** dùng chung R đồ thị sống cho mọi ứng viên → σ̂ vẫn đơn điệu + submodular → Greedy và CELF cho kết quả giống hệt (đã test).
- **CELF:** do submodular, Δ cũ là cận trên của Δ mới ⇒ chỉ tính lại phần tử đầu heap.
- **Các chế độ p:** bậc ra trung bình Email-Eu-core ≈ 25. p=0,01 là lan truyền yếu; p=0,05 và p=0,1 đã bão hòa, một seed đã kích hoạt khoảng 47% (p = 0,05) đến 67% (p = 0,1) đồ thị (kết quả thực nghiệm, xem results/plan_table.md), nên mọi thuật toán gần nhau và Greedy chỉ hơn Degree vài phần trăm.
- **Cận 1−1/e** là trường hợp xấu nhất; trong thí nghiệm brute-force trên đồ thị con 35 nút với k ≤ 3 (chỉ thử k = 1, 2, 3), Greedy trùng nghiệm tối ưu (xem results/exploratory/bruteforce.csv).
- **Hạn chế cần nói:** email ≠ sức ảnh hưởng thật; p là giả định; Email-Eu-core không phải dữ liệu của bài báo gốc.

## Việc nên làm tiếp
1. Điền số từ `results/plan_table.md` và hình `results/figs/plan_fig*.png` vào slide 3–4.
2. Thêm baseline mạnh hơn: Degree Discount, PageRank (viết thêm trong `algos.py`, thêm 1 dòng trong `run_main.py`).
3. Phân tích định tính: seed Greedy có trùng nút bậc cao không? Có rải nhiều phòng ban không? (`g.labels` đã nạp sẵn).
4. Thêm mô hình Linear Threshold nếu GV hỏi (bài báo có xét).
5. Đối chiếu với lý thuyết: Greedy trùng tối ưu trên đồ thị con nhỏ với k ≤ 3 (results/exploratory/bruteforce.csv); không vi phạm submodular (results/exploratory/submodular_check.csv); Δ giảm dần (results/exploratory/figs/fig3_marginal_gain.png).
