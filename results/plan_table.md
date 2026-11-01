# Kết quả thực nghiệm (5 lần lặp)


## p = 0.01: σ(S) trung bình ± độ lệch chuẩn giữa các lần lặp

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 1.6 ± 0.3 | 4.7 ± 0.5 | 7.7 ± 0.7 | 15.6 ± 0.8 |
| Degree | 7.5 ± 0.2 | 18.1 ± 0.1 | 26.6 ± 0.2 | 43.6 ± 0.3 |
| Greedy | 7.5 ± 0.2 | 17.6 ± 0.5 | 26.5 ± 0.4 | 43.7 ± 0.5 |

Greedy so với Degree (hiệu theo cặp, ± KTC 95%; * = khác biệt có ý nghĩa):

| k | Greedy − Degree | tăng tương đối | Greedy − Random |
|---|---|---|---|
| 1 | +0.0 ± 0.0 | +0.0% | +5.9 ± 0.2 |
| 3 | -0.5 ± 0.5 | -2.6% | +12.9 ± 0.5 |
| 5 | -0.1 ± 0.3 | -0.5% | +18.8 ± 0.8 |
| 10 | +0.0 ± 0.4 | +0.1% | +28.1 ± 1.3 |

Thời gian chọn seed (giây) và độ biến động giữa các cascade (độ lệch chuẩn của một lần mô phỏng):

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 1.2e-05s / sd 1.5 | 1.2e-05s / sd 3.0 | 1.2e-05s / sd 3.8 | 1.2e-05s / sd 5.7 |
| Degree | 0.000115s / sd 5.8 | 0.000115s / sd 8.2 | 0.000115s / sd 9.1 | 0.000115s / sd 10.0 |
| Greedy | 0.00219s / sd 5.8 | 0.00612s / sd 8.1 | 0.00974s / sd 9.2 | 0.0182s / sd 10.0 |

## p = 0.05: σ(S) trung bình ± độ lệch chuẩn giữa các lần lặp

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 216.9 ± 42.8 | 369.2 ± 38.2 | 421.5 ± 24.1 | 469.4 ± 1.5 |
| Degree | 465.2 ± 0.7 | 465.2 ± 0.8 | 465.3 ± 0.6 | 465.6 ± 0.7 |
| Greedy | 463.4 ± 0.7 | 469.2 ± 0.5 | 472.1 ± 0.5 | 478.0 ± 0.5 |

Greedy so với Degree (hiệu theo cặp, ± KTC 95%; * = khác biệt có ý nghĩa):

| k | Greedy − Degree | tăng tương đối | Greedy − Random |
|---|---|---|---|
| 1 | -1.8 ± 1.4* | -0.4% | +246.5 ± 53.3 |
| 3 | +4.0 ± 0.9* | +0.9% | +100.0 ± 47.6 |
| 5 | +6.8 ± 0.4* | +1.5% | +50.7 ± 30.4 |
| 10 | +12.4 ± 0.7* | +2.7% | +8.6 ± 1.9 |

Thời gian chọn seed (giây) và độ biến động giữa các cascade (độ lệch chuẩn của một lần mô phỏng):

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 6.33e-06s / sd 155.9 | 6.33e-06s / sd 137.0 | 6.33e-06s / sd 96.4 | 6.33e-06s / sd 28.9 |
| Degree | 0.000134s / sd 18.0 | 0.000134s / sd 18.0 | 0.000134s / sd 18.1 | 0.000134s / sd 18.0 |
| Greedy | 0.541s / sd 32.1 | 0.545s / sd 17.5 | 0.548s / sd 17.7 | 0.556s / sd 17.9 |

## p = 0.1: σ(S) trung bình ± độ lệch chuẩn giữa các lần lặp

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 434.4 ± 67.4 | 606.8 ± 37.0 | 645.3 ± 11.0 | 664.6 ± 0.6 |
| Degree | 661.0 ± 0.3 | 661.1 ± 0.2 | 661.1 ± 0.2 | 661.0 ± 0.4 |
| Greedy | 661.3 ± 0.7 | 664.6 ± 0.5 | 666.8 ± 0.7 | 672.1 ± 0.6 |

Greedy so với Degree (hiệu theo cặp, ± KTC 95%; * = khác biệt có ý nghĩa):

| k | Greedy − Degree | tăng tương đối | Greedy − Random |
|---|---|---|---|
| 1 | +0.3 ± 1.0 | +0.1% | +226.9 ± 84.4 |
| 3 | +3.5 ± 0.4* | +0.5% | +57.8 ± 45.9 |
| 5 | +5.8 ± 0.9* | +0.9% | +21.6 ± 13.9 |
| 10 | +11.1 ± 0.8* | +1.7% | +7.5 ± 1.2 |

Thời gian chọn seed (giây) và độ biến động giữa các cascade (độ lệch chuẩn của một lần mô phỏng):

| Thuật toán | k=1 | k=3 | k=5 | k=10 |
|---|---|---|---|---|
| Random | 6.13e-06s / sd 155.3 | 6.13e-06s / sd 86.6 | 6.13e-06s / sd 51.3 | 6.13e-06s / sd 12.2 |
| Degree | 0.000136s / sd 12.0 | 0.000136s / sd 12.0 | 0.000136s / sd 11.8 | 0.000136s / sd 12.1 |
| Greedy | 1.26s / sd 21.7 | 1.27s / sd 11.6 | 1.27s / sd 11.9 | 1.27s / sd 11.7 |