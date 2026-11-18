# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11   # đối chứng
```

Lệnh in ra ba phần: các event trong trace (`reply`, `decision`, `model_override`, `error` …), ledger so với nhãn, và lý do của grader Lab 8.

## Replay FM-03 trên C-002@11

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-002@11`, run ID `E-seeded_regression-20261118-45aa`, item E-002. |
| Triệu chứng | Grader Lab 8 báo `status resolved != denied`. Reply và ledger cùng ghi 20.000đ trong khi nhãn yêu cầu từ chối và ledger 0đ. |
| Bước sai đầu tiên | Bước 3, `model_override`, payload `{"delay_days": 5}`. |
| Vì sao là bước đầu tiên | Bước 1 handoff đúng C-002. Bước 2 investigator đọc đúng O-202 và độ trễ 2 ngày từ DB. Bước 3 thay độ trễ bằng con số 5 ngày trong ticket rồi bước 4 mới tính quote sai 20.000đ. |
| Failure mode | FM-03 trong `docs/failure_taxonomy.md`. |
| Đối chứng | `fixed C-002@11` giữ độ trễ 2 ngày. Bước 3 là `quote` với `amount_vnd=0` và `reason=no_entitlement`. Ledger giữ 0đ và grader Lab 8 qua. |
| Regression test | `test_c002_ticket_cannot_override_db_delay` kiểm tra ledger, trạng thái và event override trên cả hai biến thể. |
| Chưa chắc chắn | Trace cho thấy override trong lần replay này. Cần đối chiếu kết quả và ledger để phát hiện biến thể thay dữ kiện mà không ghi event. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`.
