# Báo cáo Kiểm tra Độ tin cậy Số liệu & Môi trường Thực nghiệm

Tài liệu này ghi lại kết quả kiểm tra chéo độc lập toàn bộ số liệu thực nghiệm chính thức (`results/plan_*`), phân tích độ nhạy của khoảng tin cậy thống kê, ghi nhận môi trường thực thi và kiểm thử tính đúng đắn của mã nguồn.

---

## 1. Kiểm tra chéo số liệu (Cross-check)

### 1.1. Tính hợp lý của dữ liệu thô (`plan_raw.csv`)
- **Kích thước mẫu:** Đúng 180 dòng, khớp chính xác cấu hình thực nghiệm:
  $$\text{3 thuật toán (Random, Degree, Greedy)} \times 3\text{ mức } p \times 4\text{ mức } k \times 5\text{ lần lặp} = 180\text{ dòng}$$
- **Tính toàn vẹn:** 0 giá trị khuyết thiếu (không có NaN ở bất kỳ trường nào).
- **Tính đơn điệu của Greedy:** Trên toàn bộ 5 lần lặp và 3 mức $p$, độ lan truyền $\sigma(S)$ của Greedy luôn tăng đơn điệu theo $k$ ($1 \to 3 \to 5 \to 10$), không có trường hợp nào bị giảm.
- **Độ biến động tại $k=1$ giữa các lần lặp (spread std, ddof=1):**
  - $p=0.01$: Degree đạt $7.49 \pm 0.17$, Greedy đạt $7.49 \pm 0.17$ (rất nhỏ; 2 thuật toán chọn cùng một nút bậc cao nhất).
  - $p=0.05$: Degree đạt $465.20 \pm 0.68$, Greedy đạt $463.38 \pm 0.65$ (rất nhỏ so với quy mô lan truyền $\sim 465$).
  - $p=0.10$: Degree đạt $660.95 \pm 0.30$, Greedy đạt $661.30 \pm 0.72$ (rất nhỏ so với quy mô lan truyền $\sim 661$).

### 1.2. Đối chiếu độc lập với `plan_summary.csv` và `plan_table.md`
- **Spread trung bình (`spread_mean`):** Tính toán độc lập từ `plan_raw.csv` khớp 100% với `plan_summary.csv` và `plan_table.md` (độ lệch lớn nhất là $0.0000$, không có ô nào lệch $> 0.05$).
- **Độ lệch chuẩn giữa các lần lặp (`spread_sd`, ddof=1):** Khớp 100% (độ lệch lớn nhất $0.0000$).
- **Độ biến động cascade (`cascade_sd`):** Khớp 100% (độ lệch lớn nhất $0.0000$).
- **Thời gian chọn seed (`runtime`):**
  - Tại $p=0.01$ và $p=0.05$: Chênh lệch không đáng kể ($< 0.011$s).
  - Tại $p=0.10$: Greedy runtime trung bình trong `plan_raw.csv` là $1.27$s, trong khi `plan_summary.csv` và `plan_table.md` ghi nhận $1.36$s (chênh lệch $\sim 0.085$s).
  - *Ghi chú:* File `plan_raw.csv` được tạo sau `plan_summary.csv` (timestamp 21:00 so với 20:52), nên cột `runtime` trong `plan_summary.csv` và `plan_table.md` là của lần chạy trước đó. Cột `spread` vẫn khớp tuyệt đối 100% vì thí nghiệm hoàn toàn tất định theo seed ngẫu nhiên cố định (`eval_seed = 10_000 + t`). Khuyến nghị: nên chạy lại `python summarize_plan.py` từ thư mục `experiments/` để cập nhật đồng bộ cột `runtime` mới nhất cho các file tổng hợp.

### 1.3. Đối chiếu độc lập với `plan_diff.csv` (so sánh từng cặp)
- Hiệu trung bình $\text{Greedy} - \text{Baseline}$ tính theo từng cặp (`rep`): Khớp 100%.
- Nửa khoảng tin cậy 95% ($t_{0.975, \text{df}=4} \cdot \frac{s_d}{\sqrt{5}}$): Khớp 100%.
- Tỷ lệ tăng tương đối (`rel_gain_pct`): Khớp 100%.
- Quy tắc ý nghĩa thống kê (dấu `*` khi $|\text{diff\_mean}| > \text{ci95}$): Khớp 100%.

Bảng chi tiết đối chiếu giữa Greedy và Degree:

| $p$ | $k$ | Greedy − Degree | KTC 95% | Độ lệch chuẩn cặp ($s_d$) | Có ý nghĩa ($*$) | Tỷ lệ $\frac{\text{KTC}}{\|\text{hiệu}\|}$ | $T$ ước tính |
|---|---|---|---|---|---|---|---|
| 0.01 | 1 | +0.0000 | $\pm$ 0.0000 | 0.0000 | Không | N/A | N/A |
| 0.01 | 3 | -0.4642 | $\pm$ 0.4913 | 0.3957 | Không | 1.06 | ~3 |
| 0.01 | 5 | -0.1344 | $\pm$ 0.3399 | 0.2737 | Không | 2.53 | ~16 |
| 0.01 | 10 | +0.0464 | $\pm$ 0.3665 | 0.2952 | Không | 7.90 | ~156 |
| 0.05 | 1 | -1.8218 | $\pm$ 1.3513 | 1.0883 | Có (*) | 0.74 | ~2 |
| 0.05 | 3 | +4.0342 | $\pm$ 0.9269 | 0.7465 | Có (*) | 0.23 | ~1 |
| 0.05 | 5 | +6.7998 | $\pm$ 0.3556 | 0.2864 | Có (*) | 0.05 | < 1 |
| 0.05 | 10 | +12.3634 | $\pm$ 0.7475 | 0.6020 | Có (*) | 0.06 | < 1 |
| 0.10 | 1 | +0.3476 | $\pm$ 1.0467 | 0.8429 | Không | 3.01 | ~23 |
| 0.10 | 3 | +3.4762 | $\pm$ 0.4481 | 0.3609 | Có (*) | 0.13 | < 1 |
| 0.10 | 5 | +5.7930 | $\pm$ 0.8835 | 0.7115 | Có (*) | 0.15 | < 1 |
| 0.10 | 10 | +11.1400 | $\pm$ 0.7647 | 0.6159 | Có (*) | 0.07 | < 1 |

---

## 2. Phân tích Khoảng tin cậy & Độ mong manh (Fragility Analysis)

### 2.1. Các ô kết luận còn mong manh
1. **Nhóm không có ý nghĩa thống kê (KTC 95% bao quanh 0, $|\text{hiệu}| \le \text{KTC}$):**
   - $p=0.01, k \in \{1, 3, 5, 10\}$: Tất cả các cấu hình ở $p=0.01$ đều không có khác biệt có ý nghĩa thống kê giữa Greedy và Degree.
   - $p=0.10, k=1$: Hiệu nhỏ ($+0.35$) nhưng KTC khá rộng ($\pm 1.05$), chứa giá trị 0.
2. **Nhóm KTC rộng hơn 25% độ lớn hiệu ($\text{KTC} > 0.25 \times |\text{hiệu}|$):**
   - Bao gồm toàn bộ các ô ở nhóm trên.
   - Thêm ô $p=0.05, k=1$: Hiệu mang giá trị âm ($-1.82 \pm 1.35$), dù có dấu `*` do KTC $[-3.17, -0.47]$ chưa phủ qua 0, nhưng nửa KTC chiếm tới $74\%$ độ lớn hiệu.

### 2.2. Ước lượng số lần lặp $T$ cần thiết
Dùng công thức xấp xỉ $T \approx \left(\frac{1.96 \cdot s_d}{|\text{hiệu}|}\right)^2$:
- Để khẳng định khác biệt $+0.35$ ở $p=0.10, k=1$: cần $T \approx 23$ lần lặp.
- Ở $p=0.01, k=10$: do hiệu thực tế quá bé ($+0.05$), cần tới $T \approx 156$ lần lặp.

### 2.3. Khuyến nghị
- **Không cần thiết phải chạy thêm lần lặp cho báo cáo môn học:**
  - Ở $p=0.01$, việc Greedy tương đương Degree phản ánh đúng bản chất lý thuyết: trong vùng lan truyền dưới ngưỡng tới hạn (subcritical), cascade tắt nhanh và chỉ quanh quẩn vài nút lân cận, các nút bậc cao của Degree đã tối ưu tương đương Greedy.
  - Ở $p \ge 0.05$ và $k \ge 3$, kết luận **Greedy vượt trội hơn Degree là cực kỳ vững chắc** (KTC chỉ chiếm $5\% - 23\%$ độ lớn của hiệu, dấu `*` rõ rệt với độ lợi từ $+3.5$ đến $+12.4$ nút).
  - Nếu muốn triệt tiêu hoàn toàn sự mong manh ở $k=1$, có thể chạy $T=25$ hoặc $T=30$ lần lặp.
- **Thời gian chạy ước tính:**
  - Cột `runtime` trong `plan_raw.csv` là thời gian tích lũy theo $k$ (do Greedy chạy một lần tới $k_{\max}=10$ và ghi nhận thời gian tích lũy cho từng mốc $k$), do đó không được cộng các $k$ lại với nhau. Thời gian chọn seed Greedy tính theo $k=10$ là khoảng 0,02 s ($p=0,01$), 0,57 s ($p=0,05$), 1,36 s ($p=0,1$) cho mỗi lần lặp.
  - Phần lớn thời gian thực tế nằm ở **đánh giá IC độc lập** ($1000$ lần mô phỏng $\times$ 10 tập Random = $144.000$ lượt mô phỏng IC mỗi lần lặp). Thời gian chạy thực tế của toàn bộ `run_plan.py` trong repo **chưa được đo và lưu lại** (có thể tự đo bằng `time python run_plan.py ...`).

---

## 3. Kết luận dựa trên số liệu

### 3.1. Kết luận CÓ THỂ nói chắc
1. **Greedy vượt trội Degree có ý nghĩa thống kê khi mạng có lan truyền rõ rệt ($p \ge 0.05$) và số seed $k \ge 3$:** Khoảng tin cậy 95% hoàn toàn dương, độ chênh lệch tăng dần theo $k$ (từ $+3.5$ lên $+12.4$ nút ở $k=10$).
2. Greedy hơn Random ở mọi cấu hình (+5,9 đến +246,5). Degree hơn Random khi k nhỏ hoặc p=0,01, nhưng ở p=0,05 và p=0,1 với k=10 Random cao hơn Degree (469,4 so với 465,6; 664,6 so với 661,0).
3. **Mạng lưới xảy ra hiện tượng bão hòa mạnh ở $p \ge 0.05$:** Chỉ cần 1 seed ($k=1$), cascade đã lan tới $47\%$ mạng ($p=0.05$) và $67\%$ mạng ($p=0.10$). Vì vậy, khoảng cách tương đối giữa các thuật toán bị thu hẹp chỉ còn vài phần trăm.
4. **Hàm ảnh hưởng thỏa mãn tính đơn điệu thực nghiệm:** $\sigma(S)$ luôn tăng chặt khi $k$ tăng trong mọi lần lặp.
5. CELF cho cùng kết quả với Greedy trong các thí nghiệm thăm dò (results/exploratory) và giảm khoảng 5 lần số lần tính lợi ích biên (khoảng 1.800 so với 9.815); thời gian chạy gần như bằng nhau vì vòng đầu chiếm phần lớn.

### 3.2. Kết luận KHÔNG ĐƯỢC nói
1. **KHÔNG ĐƯỢC nói "Greedy luôn thắng Degree ở mọi cấu hình":** Tại $p=0.01$, không có bằng chứng thống kê nào cho thấy Greedy hơn Degree. Thậm chí tại $p=0.05, k=1$, Degree còn nhỉnh hơn Greedy $-1.8$ nút do nhiễu mẫu ngẫu nhiên của tập snapshot.
2. **KHÔNG ĐƯỢC nói "Đã kiểm chứng cận lý thuyết $1 - 1/e$ trên toàn mạng Email-Eu-core":** Nghiệm tối ưu toàn cục (OPT) là bài toán NP-hard và không thể tính trên mạng 986 nút. Thử nghiệm brute-force chỉ mới thực hiện trên đồ thị con $35$ nút với $k \le 3$.
3. **KHÔNG ĐƯỢC khẳng định mô hình phản ánh ảnh hưởng xã hội thực tế:** Dữ liệu SNAP Email-Eu-core chỉ là nhật ký gửi nhận email, không có nhãn xác suất ảnh hưởng thực tế; các tham số $p$ hoàn toàn là giả định mô phỏng.

---

## 4. Môi trường thực nghiệm
- **Hệ điều hành:** macOS 15.7.4 (Darwin Kernel Version 24.6.0, Mach-O 64-bit)
- **Kiến trúc CPU:** Apple Silicon ARM64 (Apple M4)
- **Trình thông dịch Python:** Python 3.14.7 (Clang 17.0.0)
- **Các thư viện chính:**
  - `numpy`: 2.5.4
  - `scipy`: 1.18.1
  - `numba`: 0.68.0
  - `pandas`: 3.1.0
  - `matplotlib`: 3.11.2
- **Thời gian chạy toàn bộ `run_plan.py`:** Chưa đo trong repo (gợi ý đo thực tế bằng lệnh `time python run_plan.py --repeats 5 --R 200 --eval-runs 1000 --random-sets 10`).

---

## 5. Kết quả kiểm thử tự động (Unit Tests)
- Lệnh thực thi: `python -m pytest -q`
- Kết quả: **5 passed in 0.25s** (100% passed, 0 failed).

