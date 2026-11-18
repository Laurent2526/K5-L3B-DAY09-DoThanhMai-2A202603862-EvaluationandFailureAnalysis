# Judge audit

Chạy từ `src/` với hai CSV replay công khai. `FAIL` là lớp dương. Ngưỡng hiệu chuẩn là κ ≥ 0.60, precision ≥ 0.80 và recall ≥ 0.70.

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Tỉ lệ FAIL quan sát → hiệu chỉnh | Quyết định |
|---|---:|---|---:|---:|---:|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | 28% → 30% | Đạt cả ba ngưỡng. Dùng cho tiêu chí giọng điệu. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | 9% → 30% | Trượt κ và recall. Loại khỏi gate. |

## Audit bất đồng

| Case | Judge | Nhãn người | Phán quyết audit và chỉnh rubric |
|---|---|---|---|
| H-008 | PASS | FAIL | Nhãn người đúng. Cách xưng “em” kết hợp “nha” và “check giúp em” quá suồng sã trong ngữ cảnh CSKH. Thêm ví dụ ranh giới giữa thân thiện và suồng sã. |
| H-017 | PASS | FAIL | Nhãn người đúng theo ngữ cảnh khách lớn tuổi trong CSV. Ưu tiên “anh/chị” khi ngữ cảnh cần cách xưng hô trang trọng. |
| H-029 | PASS | FAIL | Nhãn người đúng. “Không cần nhắn thêm” mang giọng ra lệnh. Đánh giá toàn bộ câu và đánh trượt cách nói gạt khách đi dù lời mở đầu lịch sự. |
| H-042 | FAIL | PASS | Nhãn người đúng. Câu xác nhận kết quả và thời gian tiền về vẫn lịch sự. Bỏ yêu cầu xin lỗi bắt buộc đối với thông báo hoàn tiền đã đủ ý. |
| H-051 | FAIL | PASS | Nhãn người đúng. Rubric của LogiX cho phép từ “refund” trong câu tiếng Việt dễ hiểu. Ghi ngoại lệ này kèm ví dụ. |
| H-070 | PASS | FAIL | Nhãn người đúng. Emoji cười thiếu phù hợp với tình huống khiếu nại. Thêm ví dụ về emoji đùa cợt trong phản hồi khiếu nại. |
| H-081 | FAIL | PASS | Ghi chú audit trong CSV cho biết người gắn nhãn đọc nhầm ticket và judge đúng. Cần đối chiếu ticket gốc với người gắn nhãn thứ hai trước khi cập nhật nhãn. Số liệu bảng trên dùng nhãn công khai hiện tại. |
| HL-015 | PASS | FAIL | Nhãn người đúng. Reply báo 55.000đ, ledger ghi 40.000đ. Đưa kiểm tra số tiền đã hoàn vào grader code đối chiếu reply với ledger. |
| HL-016 | PASS | FAIL | Nhãn người đúng. Reply lịch sự báo 55.000đ, ledger ghi 35.000đ. Thêm cặp ví dụ cùng giọng điệu nhưng một bên báo sai tiền, và chấm số tiền qua grader code. |
| HL-020 | PASS | FAIL | Nhãn người đúng. Reply báo 90.000đ, ledger ghi 120.000đ. Kiểm tra chênh lệch cả hai chiều để bắt cả trường hợp báo thiếu. |

## Kết luận

- `helpful` chỉ phát hiện 9 trong 30 lỗi theo nhãn người và bỏ sót 21 lỗi. Precision 1.000 đến từ 9 lần dự đoán FAIL đều đúng. Recall 0.300 khiến judge bỏ sót quá nhiều lỗi để dùng làm gate.
- Rogan–Gladen hiệu chỉnh tỉ lệ FAIL ở cấp tập dữ liệu. Verdict của từng case giữ nguyên, kể cả 21 false negative của `helpful`. Tiền và phê duyệt được kiểm bằng code.
- Hai CSV là dữ liệu replay công khai. Sau khi sửa rubric, cần tập held-out mới có nhãn người để đo lại trước khi dùng kết quả cho release.
