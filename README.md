# SQL Reference Finder (offline)

Tìm lại câu SQL/lý thuyết đã chuẩn bị cho đề thi Northwind. Thuần xác định: BM25 + fuzzy + luật pattern/schema/ràng buộc. **Không AI, không mạng, không server.**

## Chạy
- App macOS (không có thanh địa chỉ): `./build_app.sh` rồi mở `SQL Reference Finder.app` (cần `swiftc`, có sẵn với Xcode Command Line Tools). Dữ liệu người dùng lưu IndexedDB của app.
- Hoặc mở `index.html` bằng trình duyệt (file://). Không cần cài gì.
- Ctrl/Cmd+Enter = tìm.
- Sidebar: **Thứ tự & tra cứu SQL** gồm khung viết/xử lý logic và 40 mục tra cứu chia 7 nhóm, có tìm theo tên hàm, điều kiện, vị trí sử dụng hoặc tình huống. Bao gồm 20 cặp so sánh trong cheat sheet người dùng cung cấp, OFFSET, DATE_FORMAT, NULL, EXISTS, window functions, CTE và ví dụ Northwind. **Northwind: Bảng & Liên kết** thay mục Schema: ý nghĩa từng dòng, cột thường dùng, số cột/dòng trong dump, khóa chính và cách nối bảng. Các liên kết là suy luận, không phải ràng buộc FOREIGN KEY.
- Cheat sheet phân biệt mệnh đề với hàm/điều kiện. Đính chính bản gửi: OFFSET bỏ qua dòng, không DELETE; DATE_FORMAT trả chuỗi; ví dụ self join so City là cùng thành phố, không phải cùng Company. Mục 17 bị thiếu được bổ sung phần BETWEEN; không đoán phần “Medium”. Mẫu viết theo MySQL 8.0, chỉ rõ INTERSECT/EXCEPT cần 8.0.31+ và có cách thay thế cho 8.0.28.

## Cấu trúc
- `index.html`, `css/`, `js/` : app. `js/search.js` = engine (chạy cả browser và Node).
- `js/data_bank.js`, `js/data_schema.js` : dữ liệu sinh tự động. Không sửa tay.
- `data/` : `mock_questions.json` (15 câu trích nguyên văn từ docx), `schema.json`, `bank.json`.
- `tools/` : nguồn của bank + script build. `tests/` : bộ test.

## Mở rộng bank (cần MySQL có nạp Northwind-1-1.sql)
1. Sửa nguồn trong `tools/bank_*.py`; `tools/bank_sql6.py` bổ sung 4 biến thể còn thiếu trong bộ 12 câu luyện tập (câu 3, 5, 7, 12), cùng cách diễn đạt khác cho các câu đã có.
   `SQL6-044` đếm khách hàng khác nhau theo từng nhân viên–thành phố (`customers.City`), giữ nhóm có ít nhất 2 khách hàng, loại NULL và không đếm lặp khách hàng có nhiều đơn.
   `tools/bank_sql8.py` bổ sung 12 tổ hợp JOIN–cấp nhóm–đại lượng–bộ lọc sau đợt rà độ phủ; ma trận, mẫu tái sử dụng và giới hạn nằm trong `BANK_COVERAGE.md`. Không sinh thêm chỉ để đổi năm/ngưỡng.
2. `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tools/build_bank.py`
   Mỗi câu SQL chạy cả bản chính và bản độc lập (`alt`); chỉ khi hai kết quả giống nhau mới thành `execution-verified`. Lỗi => script thoát mã 1 và in PROBLEM.
3. `./build_app.sh` nếu dùng app.
4. Kiểm tra độc lập: `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tools/audit_bank.py`; kiểm tra trùng và bảo toàn đề cũ: `python3 -I tools/check_bank.py`.
5. Các kiểm tra bổ sung: `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tools/semantic_checks.py`, `node tools/check_search.js`, `node tools/measure_bank.js --scale`. Bằng chứng hai vòng dựng sạch và các lỗi còn lại nằm trong `VALIDATION_REPORT.md`.

Alias được dựng cho toàn bank trong `tools/bank_aliases_auto.py`: giữ alias viết tay, bổ sung cách diễn đạt theo cấu trúc câu tổ hợp, cụm từ tương đương và gợi ý đã rà soát cho câu lý thuyết/bài tập. Không lấy câu từ bộ held-out để sinh alias; không đổi SQL, đáp án hay trạng thái xác minh. Muốn bổ sung cách diễn đạt đặc thù, sửa `CURATED` trong file này hoặc các nguồn `tools/bank_aliases*.py`, rồi dựng lại bank và app. Không sửa tay dữ liệu sinh tự động.

Engine xét cụm từ trong từng alias riêng, không ghép các alias thành một câu giả; từ lặp giữa các alias chỉ được tính một lần. Alias không trở thành khớp chính xác và không bỏ qua cảnh báo ràng buộc. Luật hiện vẫn là tìm kiếm từ vựng, không phải bộ hiểu ngữ nghĩa hay trình sinh SQL.
Schema: `MYSQL_SOCK=... python3 -I tools/extract_schema.py Northwind-1-1.sql`. Docx: `python3 -I tools/extract_docx.py in.docx data/mock_questions.json`.
Trong app: tab "Question bank" cho thêm/sửa/xóa, import JSON/CSV (cột: question, answer, kind, pattern, tags, tables, explanation), export, backup/restore. Mục import/thêm tay luôn là `unverified` hoặc `user-confirmed`; app không chạy SQL nên không bao giờ tự gắn `execution-verified`.

## Test
`node tests/check_coverage_search.js` : kiểm tra 12 mẫu độ phủ mới với câu chuẩn và câu diễn đạt khác, cả hai chế độ lọc xác minh, metadata và bank trong app. `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tests/check_coverage_sql.py` kiểm tra hai bản SQL bằng CTE có kết quả mong đợi độc lập, gồm JOIN nhân dòng, NULL, đơn không chi tiết, bảng rỗng và dữ liệu ngoài năm.

`python3 -I tests/check_aliases_all.py` : kiểm tra toàn bộ câu có ít nhất 2 alias, không trùng, không sửa dữ liệu đầu vào; các biến thể theo luật giữ nguyên mã SQL, chuỗi trích dẫn, số, toán tử và các ràng buộc nhận diện về thời gian, phủ định, đồng hạng, lượng từ, đọc/ghi. Báo cáo trước/sau mở rộng toàn bank nằm trong `tools/validation/aliases_all/REPORT.md`.

`node tests/check_sql_reference.js` : kiểm tra đủ 20 cặp so sánh, 40 ví dụ và các cú pháp chính. Thêm `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=/path/mysql` để chạy mọi ví dụ trong transaction chỉ đọc và kiểm tra OFFSET, định dạng ngày, đồng hạng, NULL.

`python3 -I tests/check_schema.py` : kiểm tra đếm dòng dump, kể cả INSERT nhiều dòng/statement và dấu ngoặc trong chuỗi.

`node tests/check_practice_search.js` : kiểm tra cả 12 câu người dùng cung cấp tìm đúng mẫu ở vị trí đầu, kể cả khi bật chỉ câu SQL đã xác minh. Đây là kiểm tra hồi quy, không phải held-out. `MYSQL_SOCK=/path/mysql.sock MYSQL_BIN=mysql python3 -I tests/check_practice_sql.py` kiểm tra 4 đáp án mới bằng dữ liệu CTE độc lập, không sửa database.

`node tests/check_paraphrase_search.js` : kiểm tra 14 câu, gồm các mẫu SQL theo năm/danh mục/thành phố, nhân viên phục vụ ít nhất 2 khách hàng trong cùng thành phố, cặp sản phẩm cùng xuất hiện trong ít nhất 3 đơn năm 2006 và hai câu lý thuyết về COUNT sau JOIN, LIMIT so với đồng hạng ở dòng thứ mười. SQL được kiểm tra cả khi bật bộ lọc đã xác minh; lý thuyết giữ trạng thái `reference-text`, cần tắt bộ lọc chỉ SQL đã xác minh để tìm. Kiểm tra cả dữ liệu đồng bộ trong app macOS. Các tình huống biên SQL nằm trong `tests/check_practice_sql.py`.

`node tests/eval.js [-v]` : Recall@1/@3, MRR, tỉ lệ top-1 sai, bẫy ràng buộc, câu không liên quan, latency. Held-out `tests/heldout.json` không nằm trong bank (script dừng nếu trùng).

`node tests/check_bank_sql7.js` : kiểm tra 44 SQL mới, alias, kết quả không rỗng, cảnh báo ghi/đọc và 15 diễn đạt hồi quy (không phải held-out). Báo cáo DML/PSM/DDL/transaction và output nghiệm thu: `tools/validation/sql7/REPORT.md`.

## Giới hạn (đọc kỹ)
- Held-out do người viết bank viết => đo hồi quy/độ bền khi diễn đạt lại, KHÔNG phải độ chính xác trên đề thật.
- Điểm % = độ giống chữ, không phải xác suất SQL đúng. Cảnh báo ràng buộc dựa trên luật, có thể sót. Luôn tự đọc lại đề.
- Toàn bank `execution-verified` chạy trên MySQL 9.7.2; riêng 44 SQL7 còn được chạy và audit độc lập trên đúng 8.0.28. Hai kết quả rỗng vẫn "verified" nhưng không có thông tin (có ghi chú EMPTY); SQL7 không có kết quả rỗng.
- Dump không có FOREIGN KEY; quan hệ là suy luận, đã đối chiếu dữ liệu (3 quan hệ chưa xác nhận được vì cột toàn NULL).
- Trong dump mọi đơn đều giao USA, nên vài câu (Q2, Q3) cho kết quả suy biến.
- Bank 2367 mục: 85 mục nguồn đề gốc (15 mock + 33 lab + 17 asg_3 + 20 asg_4), 104 VAR, 1712 COMBO, 100 SQL3, 57 SQL4, 57 SQL5, 35 SQL6, 44 SQL7 và 173 mục lý thuyết tự soạn (gồm 12 TH6 lấy từ cheat sheet so sánh). COMBO không được mở rộng trong đợt này; xem `data/combo_report.txt`. Bản viết lại COMBO là biến đổi cấu trúc, bằng chứng yếu hơn một cách giải độc lập, nên điểm bị trừ nhẹ và ghi chú trong verification.
- Độ trễ phụ thuộc máy và tải nền; xem số đo bank thật và bank nhân ba trong `VALIDATION_REPORT.md`, không dùng các số đo cũ làm cam kết hiệu năng.
- Câu hỏi asg_3/asg_4 là ảnh: chữ do tôi chép tay từ ảnh (ghi rõ ở `sourceRef`); cách hiểu mơ hồ (vd 'deviation', 'latest', 'best seller') được nêu trong phần giải thích. Hình kết quả mẫu trong ảnh không nhất thiết khớp dump này.
- INTERSECT/EXCEPT chỉ có từ MySQL 8.0.31; dump là 8.0.28 nên đáp án chính dùng IN/NOT EXISTS. Hai phương án phụ LAB-20/LAB-21 cũ vẫn dùng set operators mới, khiến build toàn bank trên 8.0.28 báo 2 unverified; không được hiểu nhãn xác minh 9.7 là tương thích toàn bộ với 8.0.28.
