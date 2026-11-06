# Tài liệu SQL trích xuất từ slides

5 tài liệu nguồn, 84 slide/trang. Mỗi tài liệu có một file Markdown cùng tên, giữ thứ tự slide/trang để dễ tra cứu và dẫn lại nguồn.

## Danh sách tài liệu

| Markdown | Số slide/trang | Nội dung |
| --- | --- | --- |
| [M3-Part 7 - Insert, Delete, Update.md](M3-Part%207%20-%20Insert%2C%20Delete%2C%20Update.md) | 20 | INSERT, INSERT có danh sách cột, partial rows, UPDATE, subquery trong UPDATE, DELETE, an toàn khi sửa/xóa dữ liệu. |
| [M3-Part 8 - Create, Update, Delete Tables.md](M3-Part%208%20-%20Create%2C%20Update%2C%20Delete%20Tables.md) | 11 | CREATE TABLE, NOT NULL, ALTER TABLE, ADD/DROP COLUMN, DROP TABLE. |
| [M6-AdvancedSQL-CorrelatedSubQuaries-SetOperations-Views.md](M6-AdvancedSQL-CorrelatedSubQuaries-SetOperations-Views.md) | 18 | Correlated subqueries, EXISTS/NOT EXISTS, recursive relationships, UNION/INTERSECT/EXCEPT, CREATE VIEW và các ví dụ view. |
| [M6-AdvancedSQL-PSM.md](M6-AdvancedSQL-PSM.md) | 23 | SQL/PSM, user-defined functions, DELIMITER, triggers, CHECK, stored procedures, bài tập và ví dụ MySQL. |
| [M6-AdvancedSQL_no_merge.md](M6-AdvancedSQL_no_merge.md) | 12 | ALTER TABLE, AUTO_INCREMENT, thêm cột, NOT NULL, CHECK, FOREIGN KEY, ON UPDATE/DELETE, xóa cột/ràng buộc. |

## Cách sử dụng

- Mỗi mục có số slide/trang, tiêu đề và neo liên kết trong mục lục.
- Nội dung tiếng Anh được giữ nguyên; ví dụ SQL đặt trong khối `sql`.
- Bảng và nội dung chỉ có trong ảnh được trích xuất bằng OCR; một số bảng đã được đối chiếu ảnh gốc và chuyển thành bảng Markdown.
- Ảnh gốc từ PowerPoint nằm trong `assets/` và được nhúng bằng đường dẫn tương đối. Giữ thư mục này cùng các file `.md`.
- Ghi chú người trình bày có nội dung được giữ ở cuối slide tương ứng.
- Slide/trang phân đoạn, trang Q&A và các mục lặp lại vẫn được giữ, không tự thêm bài giảng không có trong nguồn.

## Lưu ý độ chính xác

Đây là bản trích xuất tài liệu, không phải bản hiệu đính kiến thức SQL. Giữ nguyên cả lỗi chính tả, dấu nháy cong, ví dụ thử lỗi và cú pháp đặc thù DBMS trong nguồn. Khối `text` gắn nhãn OCR có thể nhận sai tên cột, dấu nháy hoặc thứ tự cột; dùng ảnh gốc để kiểm tra trước khi chạy SQL. Mục tiêu học tập có thể nhắc đến chủ đề không được trình bày đầy đủ trong tài liệu.

## Kiểm tra kết quả

Chạy tại thư mục gốc dự án:

```sh
python3 tools/check_slide_markdown.py
```
