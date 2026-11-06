# Rà độ phủ bank — 2026-11-06

## Phạm vi và cách rà

- Đối chiếu 2.376 mục hiện có với 20 bảng trong `data/schema.json`, nguồn `tools/bank_*.py` và truy vấn thực tế trong `data/bank.json`.
- Đơn vị rà: **chuỗi JOIN + cấp nhóm + đại lượng đếm/cộng + điều kiện lọc**. Không coi thay năm/ngưỡng là một dạng mới.
- Giữ các dạng đã có: đếm thành phố theo nhân viên (`SQL6-040`), khách hàng theo nhân viên–thành phố (`SQL6-044`), hóa đơn theo khách hàng (`SQL3-074`), tổng hợp hai bảng con theo đơn (`SQL3-099`), sản phẩm mua từ nhiều nhà cung cấp (`SQL3-065`).
- Bổ sung 12 tổ hợp có khác biệt về ý nghĩa; không sinh toàn bộ tích Descartes. Đây là rà có mục tiêu, không phải chứng minh đã phủ mọi đề có thể xuất hiện.

## Ma trận bổ sung

| ID | Chuỗi nối | Cấp nhóm | Đại lượng | Điều kiện / điểm phân biệt |
|---|---|---|---|---|
| SQL8-001 | employees → orders → customers | nhân viên + `customers.City` | đơn khác nhau | ≥ 2 đơn, loại NULL City; một khách đặt nhiều đơn vẫn tính nhiều đơn |
| SQL8-002 | employees → orders → customers | nhân viên + `orders.Ship City` | khách hàng khác nhau | ≥ 2 khách, loại NULL Ship City; không dùng thành phố cư trú |
| SQL8-003 | employees → orders → customers; orders → order details → products | nhân viên + Category | khách hàng khác nhau | năm 2006, ≥ 2 khách, loại NULL Category, không đếm lặp qua dòng hàng |
| SQL8-004 | customers → orders → order details → products | khách hàng + Category | sản phẩm khác nhau | ≥ 2 sản phẩm, loại NULL Category; không phải số danh mục/khách |
| SQL8-005 | shippers → orders → customers | hãng vận chuyển + `customers.City` | khách hàng khác nhau | ≥ 2 khách, loại NULL City, giữ đơn chưa có dòng hàng |
| SQL8-006 | suppliers → purchase orders → purchase order details → products | nhà cung cấp + Category | sản phẩm khác nhau | ≥ 2 sản phẩm; lấy lịch sử mua thật, không phân tích chuỗi Supplier IDs |
| SQL8-007 | employees → purchase orders → suppliers | người tạo + nhà cung cấp | đơn mua | ≥ 2 đơn; Created By, không phải Approved By; giữ đơn không có chi tiết |
| SQL8-008 | suppliers → purchase orders → tổng hợp purchase order details | nhà cung cấp | số đơn, phí vận chuyển, tiền hàng | giữ nhà cung cấp chưa có đơn, không nhân phí theo số dòng hàng |
| SQL8-009 | employees → orders → customers; orders → tổng hợp order details | nhân viên + khách hàng | số đơn, doanh thu sau giảm giá | giữ đơn không có chi tiết; NULL Discount = 0 |
| SQL8-010 | employees → employee privileges → privileges | nhân viên | quyền hợp lệ khác nhau | giữ nhân viên có 0 quyền; bỏ liên kết trùng và ID quyền không tồn tại |
| SQL8-011 | order details status → order details | trạng thái dòng hàng | số dòng và số đơn khác nhau | giữ trạng thái chưa dùng; Order ID NULL không được tính thành đơn |
| SQL8-012 | inventory transaction types → inventory transactions → products | loại giao dịch + Category | sản phẩm khác nhau, tổng Quantity | năm 2006 theo Transaction Created Date; tách loại giao dịch, loại NULL Category |

Metadata `tables`, `coverage.groupBy`, `coverage.measures`, `coverage.filters` trong bank giúp rà lại đúng bốn trục. Nguồn duy nhất của 12 mẫu: `tools/bank_sql8.py`; bản JSON/JavaScript được sinh bằng builder hiện có.

## Tìm kiếm trước khi bổ sung

Với câu chuẩn ban đầu của 12 mẫu mới, engine cũ + bank cũ trả về:

| Câu mới | Kết quả đứng đầu trước bổ sung | Vấn đề |
|---|---|---|
| SQL8-001 | SQL6-044 | đếm khách thay vì đếm đơn |
| SQL8-002 | SQL6-044 | thành phố cư trú thay vì thành phố giao hàng |
| SQL8-003 | không có | thiếu nhóm nhân viên–danh mục đếm khách |
| SQL8-004 | SQL3-019 | nhóm khách–sản phẩm đếm đơn, không phải khách–danh mục đếm sản phẩm |
| SQL8-005 | không có | thiếu nhóm hãng vận chuyển–thành phố cư trú |
| SQL8-006 | không có | thiếu nhóm nhà cung cấp–danh mục |
| SQL8-007 | không có | thiếu nhóm người tạo đơn mua–nhà cung cấp |
| SQL8-008 | không có | thiếu tổng hợp phí đầu đơn và tiền dòng hàng theo nhà cung cấp |
| SQL8-009 | không có | thiếu nhóm nhân viên–khách gồm cả đơn chưa có chi tiết |
| SQL8-010 | SQL5-004 | tìm người không có quyền, không phải thống kê quyền cho mọi người |
| SQL8-011 | TH5-001 | chỉ ra lý thuyết tra trạng thái, không có truy vấn báo cáo cần tìm |
| SQL8-012 | TH3-058 | chỉ ra lý thuyết loại giao dịch, không có truy vấn tổng hợp cần tìm |

Không phải mọi kết quả gần nghĩa đều an toàn để dùng. Trong phạm vi này, engine được bổ sung nhận diện đối tượng đếm là **orders** và phân biệt lời giải thích `count orders, not distinct customers` với phủ định điều kiện dữ liệu.

## Kiểm tra tái lập

```sh
MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tools/build_bank.py
MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tests/check_coverage_sql.py
./build_app.sh
node tests/check_coverage_search.js
node tests/check_paraphrase_search.js
node tests/check_practice_search.js
node tests/check_write_search.js
python3 -I tools/check_bank.py
```

- SQL: cả bản chính và bản viết độc lập chạy trên dump; CTE fixture có kết quả mong đợi riêng, không chỉ so hai câu với nhau.
- Fixture: nhiều dòng/đơn, mua lặp sản phẩm, khách trùng thành phố, tên người/công ty trùng nhưng ID khác, NULL, tham chiếu không tồn tại, nhóm đúng ngưỡng, phí bằng nhau ở hai đơn, năm ngoài phạm vi, thời điểm cuối năm, đơn không chi tiết và bảng rỗng.
- Tìm kiếm: 12 câu chuẩn + 12 câu diễn đạt khác, cả khi bật/tắt lọc SQL đã xác minh; kiểm tra bank được đóng gói trong app.
- Câu diễn đạt khác là kiểm thử hồi quy được viết cùng đợt thay đổi, **không phải held-out độc lập**. Không suy ra tỷ lệ đúng cho đề thi thật.
- Môi trường chạy SQL đợt này: MySQL 9.7.2. Truy vấn dùng cú pháp có trong MySQL 8.0; chưa xác minh trực tiếp đợt này trên 8.0.28.

## Kết quả đợt bổ sung

- Bank từ 2.376 lên 2.388 mục; cả 12 mẫu mới có bản chính và bản độc lập trả kết quả trùng nhau. Giữ nguyên nội dung câu hỏi, SQL và giải thích của 2.376 mục cũ.
- Audit độc lập toàn bank chạy 4.424 bản chính/bản thay thế cho 2.212 mục SQL, cùng 5 truy vấn phụ; 0 sai lệch kết quả/hash. Kiểm tra trùng và toàn vẹn: 0 lỗi.
- `SQL8-002` trả 0 dòng trên dump hiện tại: không có nhóm nhân viên–Ship City đạt 2 khách. Giữ nguyên yêu cầu; không hạ ngưỡng để có dữ liệu. Fixture riêng xác nhận nhóm đủ đúng 2 khách được giữ, nhóm thiếu và City NULL bị loại.
- Kiểm thử tìm kiếm mới: 24/24 câu chuẩn/diễn đạt lại đứng đầu, không có cảnh báo ràng buộc nghiêm trọng; chạy cả hai chế độ lọc xác minh.
- Bộ hồi quy 234 câu hiện có: Recall@1 từ 169/195 lên 170/195, Recall@3 từ 91,8% lên 92,3%; xử lý 24/24 bẫy, không trả kết quả cho 15/15 câu ngoài chủ đề. Vẫn còn 16 kết quả đứng đầu sai mà không có cảnh báo nghiêm trọng; không coi đây là bộ giải SQL tổng quát.
- Bộ SQL7 riêng vẫn đạt 14/15 như trước; một câu REPLACE tiếp tục nhầm biến thể. Không sửa ngoài phạm vi đợt rà.

## Giới hạn còn lại

- Engine vẫn là tìm mẫu xác định, không sinh hay chứng minh SQL cho câu bất kỳ. Không kết luận hết lỗ hổng chỉ vì 12 mẫu mới tìm đúng.
- Không thêm biến thể chỉ đổi năm/ngưỡng, không nhân mẫu tổng hợp đã có, không tạo quan hệ giao dịch giả cho `strings` hay `sales reports`.
- Khi đề yêu cầu thêm cấp nhóm, đổi cột City, vai trò nhân viên, đại lượng hoặc mốc thời gian, cần đối chiếu lại SQL; chưa có mẫu thì bổ sung một tổ hợp mới kèm fixture độc lập.
