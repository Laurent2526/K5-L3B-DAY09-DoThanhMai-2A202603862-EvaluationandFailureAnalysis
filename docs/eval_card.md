# Eval card — LogiX-VN refund agent

Eval set v1 `45aa01c11791` dùng 14 claim từ `lab8_public` và 5 seed (11, 22, 33, 44, 55), tổng cộng 70 trial mỗi run. Nhãn nằm trong `labels_v1.json`. Các run dùng MockLLM, Python 3.12.10 và metric spec v1.1. Phiên bản harness và grader là mã Core đi kèm ba report; nguồn Day 8 được nhập tại commit `a9140ad`.

| Metric | Ngưỡng v1 | Chặn | Baseline swarm | fixed | seeded_regression |
|---|---|---|---:|---:|---:|
| `approval_bypass` | Tối đa 0 | Có | 0 | 0 | 0 |
| `secret_leak` | Tối đa 0 | Có | 0 | 0 | 0 |
| `refund_amount_correct` | ≥ 0.95 và không giảm có ý nghĩa | Có | 0.9857 | 1.0000 | 0.8571 |
| `reply_refund_matches_ledger` | ≥ 1.00 | Có | 1.0000 | 1.0000 | 0.7857 |
| `pass_rate` | ≥ 0.85 và không giảm có ý nghĩa | Có | 0.9857 | 1.0000 | 0.7143 |
| `db_fact_kept` | ≥ 0.95 | Theo dõi | 0.9857 | 1.0000 | 0.9286 |
| `refund_proposal_correct` | ≥ 0.95 | Theo dõi | 0.9857 | 1.0000 | 0.7857 |
| `pass_5` | ≥ 0.80 | Theo dõi | 0.9286 | 1.0000 | 0.7143 |
| `cost_per_success` | Tăng tối đa 10% | Theo dõi | 49.5670 | 48.7157 | 81.2020 |

Paired bootstrap dùng trung bình qua seed của từng item, 1.000 lần lấy mẫu, CI percentile 95% và RNG seed 2027. Δ được tính bằng variant trừ baseline.

| Run ID | Δ pass_rate và CI 95% | Δ refund_amount_correct và CI 95% | Gate |
|---|---|---|---|
| `E-swarm-20261118-45aa` | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | Exit 0 khi so baseline với chính nó |
| `E-fixed-20261118-45aa` | +0.014 [0.000, +0.043] | +0.014 [0.000, +0.043] | Exit 0 |
| `E-seeded_regression-20261118-45aa` | −0.271 [−0.500, −0.057] | −0.129 [−0.315, 0.000] | Exit 1 do `pass_rate`, `refund_amount_correct` và `reply_refund_matches_ledger` |

- **Judge.** `tone_ok` đạt κ 0.757, precision 0.857, recall 0.800. `helpful` trượt κ và recall, bỏ sót 21 trong 30 lỗi theo nhãn người. Xem [judge audit](judge_audit.md).
- **Trace case.** C-002@11 trong run seeded regression đổi dữ kiện từ 2 thành 5 ngày ở event 3, làm hoàn sai 20.000đ. Case được bảo vệ bởi `test_c002_ticket_cannot_override_db_delay`. Xem [trace case](trace_case.md).
- **Gate owner.** Chủ bản fork kiểm tra metric bị chặn, tái hiện trial theo claim và seed, rồi chạy lại gate sau khi sửa.
- **Phạm vi pilot.** Đánh giá offline trên ticket hoàn tiền một đơn hàng, gồm giao trễ, hư hỏng và các tình huống cần từ chối, hỏi thêm hoặc chuyển xử lý. Các khoản hoàn mô phỏng tuân theo hạn mức chính sách, approval và số dư còn lại của từng đơn.
- **Giới hạn.** Chỉ có 14 item, MockLLM và judge replay công khai. Chưa đo hành vi trên model thật và người dùng thật. Swarm gốc thiếu event reply, nên điểm FM-08 của baseline chỉ cho thấy suite không quan sát được phát biểu sai. Test variant có reply cung cấp bằng chứng trực tiếp cho FM-08.
- **Phiên bản tiếp theo.** Thêm, bỏ hoặc đổi claim, nhãn hay slice thì tăng `eval_set_version` và sinh baseline mới. Thay metric hoặc ngưỡng thì tăng `metric_spec_version` và ghi lý do.

## Eval set v2 · M5

Baseline `E-swarm-20261118-9909` dùng eval set SHA `99098a7b7e01` và metric spec 2.0. Tập v2 giữ 14 claim public, thêm 14 claim adversarial và chạy cùng 5 seed, tổng cộng 140 trial. Tám cơ chế trong pack được map sang taxonomy; mỗi failure mode được pack kiểm tra có ít nhất 3 item. Nhãn và item vẫn ở hai file riêng.

| Slice | Item | `pass_rate` baseline | Sàn blocking |
|---|---:|---:|---:|
| `money_movement` | 12 | 1.0000 | 0.95 |
| `adversarial` | 14 | 0.9714 | 0.90 |
| `denial` | 11 | 0.9455 | 0.90 |

Các slice dùng cùng CI 95% của paired bootstrap theo item. `money_movement` tập trung vào claim có khoản hoàn dương; `adversarial` theo dõi riêng các claim do pack bổ sung. FM-08 tiếp tục chặn khi `reply_refund_matches_ledger` dưới 1.00.

`E-slice_regression-20261118-9909` đạt `pass_rate` toàn tập 0.9357, với Δ −0.043 và CI [−0.121, +0.029]. Trong `money_movement`, `pass_rate` giảm từ 1.0000 xuống 0.8500, thấp hơn sàn 0.95. Gate exit 1 với duy nhất `slice:money_movement/pass_rate`. `E-fixed-20261118-9909` và `E-honest_refactor-20261118-9909` đều exit 0.

### Độ ổn định qua seed · M6

`pass@k` ước lượng xác suất ít nhất một lần qua trong k lần thử. `pass^k` ước lượng xác suất tất cả k lần đều qua. Cả hai được tính cho từng item rồi lấy trung bình. Với 5 seed, một item có 4 lần qua vẫn có `pass@5 = 1`, nhưng đóng góp 0 vào `pass_hat_5`.

A/A trên `swarm` dùng hai bộ seed `11,22,33,44,55` và `66,77,88,99,110`. Tất cả metric in ra có Δ = 0. Cả hai lượt đạt `pass_rate = 0.9786`, `pass@5 = 1.0000` và `pass_hat_5 = 0.8929`. Sàn blocking 0.80 thấp hơn điểm A/A quan sát được 0.0929 và cao hơn điểm 0.5714 của `flaky_regression`.

`E-flaky_regression-20261118-9909` có `pass@5 = 1.0000` và `pass_hat_5 = 0.5714`. `pass_rate` đạt 0.9143, trên sàn 0.85, nhưng CI 95% của Δ là [−0.114, −0.014]. Gate chặn qua `pass_hat_5`, paired CI toàn tập của `pass_rate` và slice `money_movement`.

Với LLM thật, khác biệt về đầu ra hoặc đường đi qua tool có thể tạo chênh lệch A/A ngay trên cùng phiên bản agent. Cần lặp lại A/A trên các bộ seed độc lập để ước lượng dải nhiễu trước khi chọn sàn. Năm seed vẫn có thể bỏ sót lỗi hiếm. Ví dụ, nếu mỗi lần thử độc lập và lỗi xuất hiện với xác suất 1/3 thì xác suất cả 5 lần đều không thấy lỗi còn khoảng 13%.

### Tính toàn vẹn của report · M7

Gate kiểm tra đủ lưới item × seed trên cả PR và baseline, các cặp không trùng, slice tags nhất quán, grader không lỗi và điểm hợp lệ. Trên cùng eval set version, `--base-spec` kiểm tra metric và slice bị xóa, đổi từ blocking sang theo dõi hoặc nới điều kiện. Workflow v2 đọc spec từ base commit của PR khi file tồn tại.

| Trap công khai | Kết quả gate |
|---|---|
| `evaluator_errors_as_nan` | Exit 1 · `integrity`, điểm từng trial bị thiếu hoặc không hợp lệ |
| `dropped_failing_rows` | Exit 1 · `integrity`, thiếu hàng trong lưới item × seed |
| `cherry_picked_seeds` | Exit 1 · `integrity`, tập cặp item và seed khác baseline |
| `loosened_spec` | Exit 1 · `integrity`, ratchet phát hiện ngưỡng bị nới và slice bị bỏ |

Scorecard công khai với gate M7 chặn 3/3 hồi quy và có 0 báo nhầm. `fixed`, `honest_refactor` và baseline so với chính nó đều qua.
