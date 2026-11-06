# SQL7: lấp khoảng trống question bank

Ngày: 2026-11-06. Phạm vi: 44 SQL (`SQL7-001`–`SQL7-044`), 6 lý thuyết (`TH5-005`–`TH5-010`).

## Gia đình câu hỏi

Mỗi hàng có một câu gốc và 2–3 biến thể thay đổi yêu cầu thật; alias chỉ phục vụ tìm kiếm, không được tính là biến thể.

| ID | Yêu cầu thay đổi giữa các biến thể |
| --- | --- |
| 001–003 | INSERT nhiều dòng; INSERT SELECT trước tháng 3; INSERT SELECT từ tháng 4 |
| 004–006 | UPDATE nhiều cột tăng giá; CASE trên mọi dòng; giảm giá và discontinue |
| 007–009 | UPDATE bằng subquery ngày; JOIN số đơn tối thiểu; anti-join hàng chưa bán |
| 010–012, 016 | DELETE theo ngày; NOT EXISTS; không WHERE; TRUNCATE và reset ID |
| 013–015 | REPLACE khóa có sẵn; khóa mới; cả hai trong một statement |
| 017–019 | Function ghép tên; IF phân loại giá; tổng tiền đơn có READS SQL DATA |
| 020–022 | Trigger chuẩn hóa INSERT; SIGNAL khi UPDATE sai; AFTER INSERT ghi log |
| 023–025 | Procedure IN trả danh sách; IN/OUT trả scalar; IN tổng doanh thu nhân viên |
| 026–028 | CURSOR tổng giá; tổng số lượng; đếm đơn nhân viên theo thời gian |
| 029–031 | CREATE với PK, AUTO_INCREMENT, CHECK, DEFAULT; FK RESTRICT/CASCADE/SET NULL |
| 032–034 | ALTER thêm cột; xóa cột; thêm và xóa cột trên bảng khác |
| 035–037 | Thêm CHECK; xóa CHECK; xóa FOREIGN KEY nhưng giữ cột/index |
| 038–040 | COMMIT chuyển tiền; ROLLBACK toàn bộ; SAVEPOINT giữ giao dịch trước lỗi |
| 041–044 | Lookup tax status; sales reports; privileges; order details status |

`sql` và `alt` đều tự chạy được; khác cách làm, không chỉ đổi alias. Ví dụ: VALUES/SELECT, WHERE/JOIN, IF/CASE, routine/SELECT trực tiếp, CREATE/ALTER, trigger INSERT VALUES/SELECT, hai UPDATE/một CASE UPDATE. DDL không dựa vào kết quả SELECT đơn thuần: các bài constraint/cột còn đọc metadata; trigger kiểm tra cả đường hợp lệ và đường bị từ chối.

## DB kiểm thử

- 44 SQL mới: MySQL **8.0.28**, Linux amd64 qua Docker; `log_bin_trust_function_creators=0`.
- Toàn bank: MySQL **9.7.2** native, data directory và socket riêng dưới `/tmp`, cùng thiết lập function creators. Đây cũng là phiên bản runtime của baseline; không dùng DB host đang có mật khẩu.
- Container riêng `sql-helper-bank-8028-20261106`, không publish cổng host, không sửa MySQL đang chạy trên máy.
- Import `Northwind-1-1.sql`; chỉ đổi `CREATE DATABASE Northwind`/`USE Northwind` thành `northwind` trên luồng nhập vì Linux phân biệt hoa/thường. File dump gốc không đổi.
- DML trên bảng thật chạy trong rollback. DDL, TRUNCATE, trigger, procedure và transaction tự quản dùng bảng/routine `zz_*`, cleanup trước/sau.
- Snapshot ban đầu: 20 bảng, 511 dòng; `shippers=3`, `products=45`, `orders=48`. Hash SHA-256 từng bảng nằm trong `before_state.json`.
- Đã đo: archive trước 2006-03-01 có 7 dòng, từ 2006-04-01 có 33; Beverages 5, Condiments 3; sản phẩm chưa bán 21. Toàn bộ 48 đơn có Tax Status NULL, vì vậy hai mã thuế đều có count 0, không phải kết quả rỗng.
- Cursor đếm đơn sớm dùng nhân viên **3** có dữ liệu, không dùng nhân viên 1 có nguồn rỗng.

## Chạy lại

Wrapper `/tmp/sql-helper-mysql-8028` chỉ chuyển tiếp tới mysql CLI trong container; không chứa mật khẩu:

```sh
#!/bin/sh
exec docker exec -i -e MYSQL_PWD sql-helper-bank-8028-20261106 mysql "$@"
```

Sau nghiệm thu hai server fixture được tắt. Khởi động lại server 9.7 để chạy cổng toàn bank:

```sh
RUN_DIR=$(cat tools/validation/sql7/mysql97_path.txt)
/usr/local/mysql/bin/mysqld --no-defaults --basedir=/usr/local/mysql \
  --datadir="$RUN_DIR/data" --socket="$RUN_DIR/mysql.sock" \
  --skip-networking --mysqlx=OFF --log-bin-trust-function-creators=0 \
  --pid-file="$RUN_DIR/mysql.pid" --log-error="$RUN_DIR/server.log" --daemonize
export MYSQL_PWD='' MYSQL_SOCK="$RUN_DIR/mysql.sock" MYSQL_BIN=/usr/local/mysql/bin/mysql
python3 -I tools/build_bank.py
python3 -I tools/check_bank.py
python3 -I tools/audit_bank.py
node tests/eval.js
node tests/check_bank_sql7.js
./build_app.sh
```

Audit riêng SQL7 trên 8.0.28 (không import builder):

```sh
docker start sql-helper-bank-8028-20261106
python3 -I -c 'import json; b=json.load(open("data/bank.json")); b["entries"]=[e for e in b["entries"] if e["id"].startswith("SQL7-")]; print(json.dumps(b))' > /tmp/sql7-only.json
MYSQL_PWD='' MYSQL_SOCK=/tmp/mysql.sock MYSQL_BIN=/tmp/sql-helper-mysql-8028 \
  python3 -I tools/audit_bank.py --bank /tmp/sql7-only.json
```

Fixture native nằm trong `/tmp`; nếu hệ thống đã dọn thư mục này thì cần khởi tạo lại server và nhập dump trước khi chạy các lệnh trên.

Với DB riêng đã có quyền truy cập, dùng `MYSQL_BIN=mysql` và truyền mật khẩu qua `MYSQL_PWD`, không ghi mật khẩu vào file. Không chạy DDL kiểm thử trên dữ liệu quan trọng khi chưa có bản sao.

## Kết quả cổng toàn bank (MySQL 9.7.2)

`python3 -I tools/build_bank.py` — exit 0, không dòng PROBLEM, không unverified (`build_bank.txt`):

```text
combo: candidates 1918 kept 1712 dropped {'dup-existing': 10, 'error': 0, 'differs': 0, 'empty': 112, 'all-rows': 36, 'dup-question': 0, 'dup-result': 48}
2334 entries; {'execution-verified': 2170, 'reference-text': 164}
```

`python3 -I tools/check_bank.py` — exit 0, trích output (`check_bank.txt` chứa toàn bộ):

```text
New entries: 337 {'sql': 258, 'theory': 79}
Statuses: {'execution-verified': 258, 'reference-text': 79}
Existing entry content preserved: 1983 / 1983
Identical structural feature signatures: []
Protected file hashes checked: 17
Errors: 0
```

Check bổ sung so với bank ngay trước SQL7: giữ nguyên nội dung câu hỏi/đáp án, alias và metadata nội dung của **2284/2284** mục, không tính related links và thông tin xác minh được build lại. Held-out gốc và phần preregistered không đổi.

`python3 -I tools/audit_bank.py` — exit 0 (`audit_bank.txt`):

```text
Independent MySQL CLI audit
SQL entries: 2170 statuses: {'execution-verified': 2170}
Main/alternative executions: 4340 additional answer executions: 5
Empty primary results: 14 VAR-011, VAR-041, VAR-085, VAR-091, SQL3-008, SQL3-046, SQL3-056, SQL3-089, SQL6-005, SQL4-028, SQL4-036, SQL5-022, SQL5-030, SQL5-047
Mismatches: 0
```

14 kết quả rỗng là mục cũ; **SQL7: 0 rỗng**.

`node tests/eval.js` — exit 0, trích output (`eval.txt` có cả các miss cũ):

```text
bank entries: 2334   held-out cases: 234 (195 scored retrieval, 24 traps, 15 unrelated)
Recall@1: 84.6% (165/195)   Recall@3: 88.2%   MRR: 0.864
Incorrect top match (answered but wrong): 8.8% (16/181)
  of which with NO critical-constraint warning: 16
  (info) strict misses whose top entry has the identical verified result set as an expected entry: 0
Trap cases (similar wording, different requirement) handled (no match or critical warning): 24/24; silent wrong: 0
Unrelated questions wrongly answered: 0/15
Latency ms: mean 12.02  p95 23.91  max 33.79
```

Recall@1 giữ nguyên 165/195 so với trước SQL7, đạt ngưỡng 84.6%. `./build_app.sh` — exit 0 (`build_app.txt`):

```text
built: SQL Reference Finder.app
```

Đã kiểm tra JSON và JS bank giống nhau; app chứa đúng JS bank và search hiện tại; plist hợp lệ; `codesign --verify --strict` thành công.

## Xác minh riêng MySQL 8.0.28

`audit_mysql8028.txt` — exit 0:

```text
Independent MySQL CLI audit
SQL entries: 44 statuses: {'execution-verified': 44}
Main/alternative executions: 88 additional answer executions: 0
Empty primary results: 0
Mismatches: 0
```

Hash kết quả của 44/44 SQL7 giống nhau trên cả hai phiên bản. Lượt kiểm tra bổ sung `targeted.txt` chạy lại từng main/alt và 12 assertion trạng thái cụ thể, bao gồm:

- Trigger INSERT: âm/NULL thành 0, giá dương giữ nguyên; trigger UPDATE từ chối âm/NULL, giữ giá cũ, vẫn cho phép giá hợp lệ.
- Log AFTER INSERT bị rollback cùng dữ liệu nguồn; TRUNCATE sinh lại ID 1.
- OUT tổng đơn nhỏ nhất: `1505.0000`; tổng doanh thu nhân viên 2: `2997.5000`.
- Cursor: tổng giá Beverages `84.9900`, tổng số lượng đơn nhỏ nhất `130.0000`, số đơn nhân viên 3 trước tháng 3 `2.0000`.
- COMMIT: số dư `75.00/75.00`; ROLLBACK: `100.00/50.00`; SAVEPOINT sau lỗi thiếu tiền: `90.00/60.00`.

`transaction_error.txt` còn chèn lỗi SQLSTATE 45001 sau lần chuyển tiền đầu tiên vào cả hai cách giải SAVEPOINT: handler rollback toàn bộ rồi RESIGNAL; caller bắt lỗi trong **cùng connection** và đọc lại số dư `100.00/50.00`. Không dựa vào việc đóng connection để che transaction bị bỏ dở.

**Giới hạn cũ, không che bằng nhãn verified:** lượt build toàn bank trên 8.0.28 exit 1 (`build_bank_mysql8028.txt`), với 2168 execution-verified, 164 reference-text và 2 unverified. Hai mục **LAB-20/LAB-21** dùng INTERSECT/EXCEPT trong phương án phụ/related SQL, cú pháp chỉ có từ 8.0.31. Không sửa nguồn LAB được bảo vệ hoặc baseline để làm xanh cổng. Nhãn verified toàn bank áp dụng cho 9.7.2; chỉ 44 SQL7 được xác nhận riêng trên đúng 8.0.28.

## Tìm kiếm và tồn dư

`node tests/check_bank_sql7.js` — exit 0; đây là **hồi quy do người triển khai viết, không phải held-out độc lập**:

```text
SQL7 retrieval regression: 13/15; silent write mismatch: 0
PASS write-intent warnings with retrieval-only candidates
```

Hai miss còn lại được giữ nguyên trong test/output, không đổi câu hỏi để làm đẹp số:

- Cách diễn đạt UPDATE CASE chứa `>=` và nhiều hằng số: không trả kết quả.
- Cách diễn đạt REPLACE khóa 1: top-1 là SQL7-014 (khóa mới 2), thay vì SQL7-013 (khóa có sẵn 1), không cảnh báo critical. Đây là lỗi tìm kiếm yêu cầu cụ thể, dù cùng thuộc thao tác ghi.

Mở rộng nhận diện write cho REPLACE/TRUNCATE, tạo function/procedure/trigger và transaction. Test bắt buộc mọi SELECT được trả về cho câu ghi phải có cảnh báo critical; không đồng nghĩa engine đảm bảo đúng mọi ngưỡng/khóa.

Test phụ cũ `node tests/check_practice_search.js` vẫn lỗi **14 !== 4** tại assertion số SQL6 (`practice_search.txt`). Bank trước SQL7 đã có 14 SQL6; không sửa test không thuộc phạm vi này.

`db_invariants.txt`, `final_db.txt`, `after_mysql8028.json`, `after_mysql97.json`: cả hai fixture giữ nguyên **20/20 bảng, 511 dòng, SHA-256 từng bảng**, gồm `shippers=3`, `products=45`, `orders=48`; không còn bảng `zz%`, trigger, function hoặc procedure. Không sửa DB host đang có mật khẩu. Hai server fixture được tắt sau lượt kiểm tra cuối; giữ dữ liệu fixture để có thể audit lại.
