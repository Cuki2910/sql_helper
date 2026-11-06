# Plan: lấp khoảng trống question bank (DML, PSM, DDL, transaction)

Written for: coder (X) sẽ viết mục bank; người audit đọc lại sau.

## Đo hiện trạng (bank 2284 mục, đo ngày 2026-11-06)
| Phần | Hiện có | Thiếu so với slide |
|---|---|---|
| DML | SQL4-048..057 (INSERT 2, UPDATE 3, DELETE 2) | `INSERT..SELECT` 0, `UPDATE ... JOIN` 0, `UPDATE` nhiều cột, `UPDATE` với subquery (M3-P7 slide 15), `REPLACE` 0, `TRUNCATE` 0 |
| PSM | chỉ lý thuyết (TH-69, TH4-006/007/008) | 0 SQL chạy được: function, trigger, procedure `IN`/`OUT`, `CURSOR` 0. M6-PSM có 3 ví dụ trigger + 3 procedure |
| Transaction | 0 mục có `START TRANSACTION`/`ROLLBACK`/`COMMIT` trong đáp án | cả phần SQL |
| DDL | `CREATE TABLE` 1, `ALTER` 1 | constraint, `FOREIGN KEY`, `AUTO_INCREMENT`, drop cột/constraint (M6 no_merge) |
| Bảng | `orders tax status` 0, `sales reports` 0 | nhỏ, ưu tiên thấp |

Không làm: `JSON_*`, `LATERAL`, `NATURAL JOIN` (không có trong slide, YAGNI).

## Quy tắc bắt buộc
1. Mỗi câu gốc kèm 2-4 biến thể khác yêu cầu thật (ngưỡng, hướng, bảng, `WHERE` có/không). Không biến thể chỉ đổi chữ.
2. Mỗi mục có `sql` và `alt` độc lập. `alt` phải khác cấu trúc (build_bank + `check_bank` loại `same-structure-signature`).
3. Mỗi mục thêm alias vào `ALIASES_*` (câu diễn đạt khác, tiếng Anh).
4. Biến thể không được rỗng (xem SQL5-047, SQL6-005 là ví dụ rỗng chỉ chấp nhận khi ghi `EMPTY RESULT` trong explanation).
5. Số liệu trong explanation (số dòng, giá trị) phải đo từ DB, không đoán.
6. Cú pháp MySQL 8.0.28. Không `INTERSECT`/`EXCEPT`.

## Cách verify DML/DDL (đã có sẵn, đọc `tools/build_bank.py:49-65`)
- Dòng entry cần `mode`, `check`, `cleanup`. `S()` trong `bank_sql6.py` KHÔNG có 3 khóa này; dùng format `S()` của `bank_sql4.py`.
- `mode='rollback'`: build bọc `START TRANSACTION; <sql> <check> ROLLBACK;`. Dùng cho `INSERT/UPDATE/DELETE`.
- `mode='ddl'`: `CREATE/ALTER/DROP` tự commit, nên BẮT BUỘC `cleanup` chạy trước và sau, trả DB về nguyên trạng.
- `TRUNCATE` cũng tự commit: không được chạy trên bảng thật. Tạo bảng tạm `zz_*` từ `CREATE TABLE ... AS SELECT`, truncate bảng đó, `cleanup` = `DROP TABLE IF EXISTS zz_*`.
- Mục có `START TRANSACTION`/`ROLLBACK` trong chính đáp án: KHÔNG dùng `mode='rollback'` (transaction lồng sẽ commit ngầm). Dùng `mode='ddl'`, `cleanup` khôi phục dữ liệu bằng câu `UPDATE`/`DELETE` ngược lại, và `check` đọc trạng thái cuối.
- Function: `DELIMITER //` chạy được qua `mysql -e` (đã thử). Bắt buộc có `DETERMINISTIC` hoặc `READS SQL DATA` (`log_bin_trust_function_creators=0`). `cleanup` = `DROP FUNCTION IF EXISTS`.
- Trigger: `mode='ddl'`; `check` = `START TRANSACTION; INSERT...; SELECT ...; ROLLBACK;`; `cleanup` = `DROP TRIGGER IF EXISTS`.
- DB test: `northwind` (socket `/tmp/mysql.sock`, user `root`, mật khẩu qua biến `MYSQL_PWD`, không ghi vào file).

## Wiring (làm một lần, đầu tiên)
Tạo `tools/bank_sql7.py` (ID `SQL7-xxx`, dùng `S()` có `mode/check/cleanup`) và `tools/bank_aliases_sql7.py`. Sửa `tools/build_bank.py`:
- import `SQL7` và `ALIASES_SQL7`, thêm vào dict `ALIASES` (dòng 21).
- vòng `for entry in SQL4 + SQL5:` (dòng ~200) thêm `SQL7`; sửa `sourceRef` cho tiền tố `SQL7`.
- `new_sql_ids` (dòng ~226) thêm `SQL7`.
- `tools/check_bank.py`: thêm `'SQL7-'` vào tuple `startswith` ở dòng 31, và assert đếm `SQL7-` bằng số mục thực.
Lý thuyết mới vào `tools/bank_theory5.py` (`TH5-005` trở đi), cập nhật assert `== 61` ở `check_bank.py:39`.

## Phạm vi, theo ưu tiên
**P1. DML (slide M3-Part 7, đọc `slides/M3-Part 7 - Insert, Delete, Update.md`)** ~16 mục
- `INSERT` nhiều dòng một câu lệnh + biến thể `INSERT ... SELECT` (copy theo điều kiện, ví dụ orders trước 2006-03 sang bảng `zz_*`).
- `UPDATE` nhiều cột (slide 14) và biến thể `UPDATE` có `CASE`.
- `UPDATE` với subquery trong `WHERE` (slide 15) và biến thể `UPDATE ... JOIN`.
- `DELETE` có điều kiện + biến thể `DELETE` với `NOT EXISTS`; `DELETE` không `WHERE` trên bảng `zz_*`.
- `REPLACE INTO` (kèm cảnh báo khác `ON DUPLICATE KEY UPDATE` ở SQL4-052).
- `TRUNCATE` vs `DELETE` (bảng `zz_*`).

**P2. PSM (slide M6-PSM)** ~12 mục
- Function: ghép tên (slide 8), function có `IF`, function tính tổng tiền một đơn.
- Trigger: `BEFORE INSERT` kiểm tra/chuẩn hóa giá, `BEFORE UPDATE` chặn giá trị sai bằng `SIGNAL`, `AFTER INSERT` ghi log vào bảng `zz_*` (slide 14-17).
- Procedure: `IN` (slide 21), `OUT`, `IN` + `CALL` có `SELECT` tổng theo nhân viên (slide 20-22).
- Mỗi loại có 1 mục `alt` viết bằng cách khác (ví dụ function vs câu `SELECT` thẳng).

**P3. DDL + transaction** ~10 mục
- `CREATE TABLE` có `PRIMARY KEY`, `AUTO_INCREMENT`, `FOREIGN KEY`, `CHECK`, `DEFAULT`.
- `ALTER TABLE`: thêm/xóa cột, thêm/xóa constraint (M6 no_merge, "Removing Table Column/Constraint").
- `START TRANSACTION`/`ROLLBACK`/`COMMIT`: chuyển tiền giữa hai dòng, rollback khi sai; `SAVEPOINT`.

**P4. Bảng ít dùng** ~4 mục: `orders tax status` (2 dòng), `sales reports` (5 dòng), `privileges`, `order details status`. Chỉ cần mỗi bảng 1 câu `SELECT`/`JOIN` có nghĩa.

Tổng ~40-45 mục SQL + ~6 lý thuyết (khi nào dùng trigger vs procedure, `TRUNCATE` vs `DELETE` vs `DROP`, `ROLLBACK` có hoàn tác DDL không, `SIGNAL`).

## Cổng nghiệm thu (X chạy hết, dán output vào báo cáo)
```
export MYSQL_PWD=... MYSQL_SOCK=/tmp/mysql.sock MYSQL_BIN=mysql
python3 -I tools/build_bank.py        # 0 dòng PROBLEM, 0 unverified
python3 -I tools/check_bank.py        # Errors: 0
python3 -I tools/audit_bank.py        # Mismatches: 0
node tests/eval.js                    # Recall@1 >= 84.6%, trap silent wrong = 0, unrelated 0/15
./build_app.sh
```
Kiểm tra thêm sau mỗi lượt: bảng `shippers`, `products`, `orders` giữ nguyên số dòng (đếm trước/sau), không còn bảng/function/trigger `zz_*`: `SHOW TABLES LIKE 'zz%'`, `SHOW TRIGGERS`, `SHOW FUNCTION STATUS WHERE Db='northwind'`.

## Việc audit (phía tôi, sau khi X xong)
1. Đọc từng `sql` và `alt`: có thật sự khác cách làm, có đúng yêu cầu câu hỏi (không chỉ cùng kết quả).
2. Số liệu trong explanation khớp DB.
3. Biến thể có khác yêu cầu thật, không rỗng.
4. Chạy lại 5 lệnh nghiệm thu độc lập, so với báo cáo của X.
5. Viết 15 câu hỏi diễn đạt khác (không có trong bank) cho DML/PSM/DDL, chạy `eng.search`, đo top-1 và cảnh báo `write`. Câu `INSERT/UPDATE/DELETE` không được trả về câu `SELECT` mà không có cảnh báo (engine có hệ số 0.75 cho `write` lệch).
6. Kiểm tra DB không bị bẩn: đếm dòng các bảng chính trước/sau.

## Rủi ro đã biết
- DDL tự commit: `cleanup` sai sẽ để lại bảng thật bị đổi. Chạy build trên bản sao DB nếu không chắc: `mysqldump northwind > /tmp/nw.sql` trước khi bắt đầu.
- `ON DUPLICATE KEY UPDATE ... AS new_row` (alias hàng mới) là cú pháp 8.0.19+, dùng được trên 8.0.28.
- Engine hiện bỏ các câu `Return/Sort/Round` khỏi điểm từ vựng. Câu hỏi DML kiểu "Insert ..." không bị ảnh hưởng, nhưng audit mục 5 sẽ xác nhận.
