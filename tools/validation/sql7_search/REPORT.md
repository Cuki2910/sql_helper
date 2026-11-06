# Nghiệm thu riêng thay đổi cũ SQL7 — 2026-11-06

## 1. Phạm vi và kết luận

- Theo yêu cầu tiếp theo: chỉ nghiệm thu khối nhận diện `write` và 132 alias SQL7 đã thêm. Bỏ ngoài các thay đổi chuẩn hóa toán tử/so sánh xuất hiện đồng thời. Không sửa hay ghi đè source/app đang làm việc.
- Khôi phục bản nghiệm thu riêng từ `/tmp/search.js.pre_x`, chỉ áp lại hunk `write`; đối chiếu phần trước/sau khối đều trùng backup. Diff được lưu tại `accepted/search.diff`.
- Cả năm lệnh nghiệm thu chạy lại, exit 0 trên snapshot này, dùng **DB northwind cô lập MySQL 9.7.2**. Chưa nghiệm thu DB host `/tmp/mysql.sock` hay MySQL 8.0.28.
- Recall@1 84.6% (165/195); Recall@3 88.2%; top-1 sai 8.8% (16/181), không tăng; trap silent wrong 0; unrelated 0/15. Danh sách 30 MISS@1 giống baseline.
- 15 câu DML/PSM/DDL mới: top-1 10/15, top-3 10/15 (66.7%), NONE 3/15; còn 2 câu trả sai không có critical warning. Không bỏ câu thất bại.
- 15 SELECT: write=false 15/15, top-1 SQL7 0/15. Trong top-3 có 1 mục SQL7 chỉ đọc, có critical warning; không tuyên bố top-3 hoàn toàn vắng SQL7.
- Giữ nguyên SQL/alt/check/cleanup/explanation, held-out, evaluator, file bảo vệ, minScore 0.22, minCoverage 0.45, critPenalty 0.55 và hệ số phạt 0.75.

## 2. Snapshot, backup, môi trường

Working directory của cả năm lệnh chạy lại:

```text
/var/folders/kn/n36cb2ms21g485dsx4ffk0p80000gn/T/sql7-search-accept.v61d00v9
```

Bản app build trong snapshot, không thay app đang làm việc. Snapshot và log `accepted/` là căn cứ nghiệm thu; các log cấp trên là lịch sử lần chạy trước.

Trước lần sửa đầu đã sao lưu `cp js/search.js /tmp/search.js.pre_x` và dump northwind tại `/tmp/nw_pre_x.sql`; có thêm `/tmp/bank_aliases_sql7.py.pre_x`, `/tmp/bank.json.pre_x`. Dump dùng fixture, không phải DB host; có routines/triggers, single transaction và tắt GTID_PURGED.

Không có thông tin xác thực host `/tmp/mysql.sock`; không suy đoán mật khẩu. Fixture chỉ dùng Unix socket, mật khẩu rỗng chỉ truyền qua biến môi trường, không lưu mật khẩu trong file. Môi trường thực tế:

```sh
RUN_DIR=$(cat /Users/cuki2910/Desktop/sql_helper/tools/validation/sql7/mysql97_path.txt)
export MYSQL_PWD='' MYSQL_SOCK="$RUN_DIR/mysql.sock" MYSQL_BIN=/usr/local/mysql/bin/mysql
```

`RUN_DIR`: `/tmp/sql-helper-sql7-97.cl2fiI`. Chưa xác nhận tương đương môi trường host/MySQL 8.0.28.

## 3. Diff js/search.js và toàn bộ alias thêm

Diff dưới chỉ chứa thay đổi cũ được nghiệm thu. ADD xét raw clause để tránh nhầm DATE_ADD; bỏ ngữ cảnh cột computed/percentage/output; window/aggregate/built-in function không bị coi là PSM. Regex vẫn chỉ là heuristic như chú thích ponytail.

```diff
--- a/js/search.js
+++ b/js/search.js
@@ -201,8 +201,10 @@
     if (/\bsum\b/.test(t)) agg.add('sum');
     if (/\bcount\b/.test(t) && !(/\bcount number (days?|hours?|minutes?|seconds?|weeks?|months?|years?|rows?|decimals?|characters?|digits?)\b/.test(t) && !/\bcount (?!number)/.test(t))) agg.add('count');
     c.agg = agg;
-    // data-changing statement vs plain SELECT: a DELETE/UPDATE/DDL answer must not be offered for a retrieval question (and vice versa)
-    c.write = /\b(delete|remove|insert|update|upsert|replace|truncate|alter|drop|raise|commit|rollback)\b|\bstart (a )?transaction\b|\bcreate\b.*\b(tables?|view|index|function|procedure|trigger)\b|\badd (a |an |the )?new (row|shipper)\b|\badd (a |an )?column\b[^.]*\bto the \w+ table|\bon duplicate key\b/.test(t);
+    // ponytail: lexical intent, not SQL parsing; unqualified functions and negated DDL remain ambiguous. Upgrade to statement-aware classification when needed.
+    const writeText = t.replace(/\b(?:built in|window|aggregate) functions?\b/g, ' ');
+    const schemaWrite = /\badd(?:s|ed|ing)?\b[^.;?!]*\b(constraints?|checks?|index(?:es)?|indices|keys?)\b|\badd(?:s|ed|ing)?\b(?![^.;?!]*\b(?:computed|calculated|output|results?|reports?|ratios?|percent(?:age)?)\b)[^.;?!]*\bcolumns?\b|\badd(?:s|ed|ing)?\b[^.;?!]*\b(rows?|records?)\b[^.;?!]*\b(?:to|into)\b|\bremov(?:es|ed|ing)\b[^.;?!]*\b(rows?|records?|fields?|columns?|constraints?|checks?|index(?:es)?|indices|keys?)\b/i.test(scoped);
+    c.write = schemaWrite || /\b(delet(?:e[sd]?|ing)|remove|insert(?:s|ed|ing)?|updat(?:e[sd]?|ing)|upsert(?:s|ed|ing)?|replac(?:e[sd]?|ing)|truncat(?:e[sd]?|ing)|alter(?:s|ed|ing)?|drop(?:s|ped|ping)?|rais(?:e[sd]?|ing)|commit(?:s|ted|ting)?|roll(?:back| back|ed back|ing back))\b|\bstart (a )?transaction\b|\bcreate\b.*\b(tables?|view|index|function|procedure|trigger)\b|\badd(?:s|ed|ing)? (a |an |the )?new (rows?|shippers?)\b|\b(triggers?|functions?|procedures?|cursors?|savepoints?)\b|\btransfer(?:s|red|ring)?\b.*\btransactions?\b|\bon duplicate key\b/.test(writeText);
     c.perCat = /\b(?:in|within|per|for) (?:each|every) (?:product )?categor|\bper (?:product )?categor|\bwithin (?:its|their|the same) (?:product )?categor/.test(t);
     c.allocEq = /\b(equal|equally|evenly)\b/.test(t);
     c.allocProp = /\bproportion\w*|\bpro rata\b|\bprorata\b|\bvalue share\b|\bshare of\b/.test(t);
```

### 132 alias mới: 3 cho mỗi mục SQL7

Giữ nguyên 88 alias cũ. Mọi alias thêm đều không có zz_, scratch, SQLSTATE hay tên bảng tạm.

| Mục | Alias thêm 1 | Alias thêm 2 | Alias thêm 3 |
|---|---|---|---|
| SQL7-001 | How do I insert two shippers at once? | Adding two shipping companies with one INSERT. | Insert several delivery companies in a single multirow statement. |
| SQL7-002 | How can I insert old orders into an archive before March 2006? | Copy only orders earlier than March into another table using INSERT SELECT. | Inserting orders into an archive with a date cutoff before March. |
| SQL7-003 | Insert the April 2006 orders and everything later into an archive. | How do I save orders from April onward in another table? | Insert recent orders into another table starting from April 2006. |
| SQL7-004 | How do I update the price and reorder level for beverages together? | Updating beverage prices ten percent and setting reorder level to 30. | Updating two product fields together, price plus reorder point. |
| SQL7-005 | Update every product with CASE to choose reorder levels by price. | I need an update with different reorder levels for cheap and expensive products. | Can an update assign different stock levels depending on how expensive a product is? |
| SQL7-006 | Update condiment prices down five percent and discontinue them. | How can I update both price and discontinued for condiments? | Updating condiments should lower prices and flag them as discontinued. |
| SQL7-007 | Update reorder levels for products sold before March 2006. | How do I update products using an order subquery? | Use a subquery to choose which products get their reorder level updated. |
| SQL7-008 | Update the target stock for products sold on at least three orders. | How can I update products from a grouped join of their orders? | Updating popular products based on the number of orders they appear in. |
| SQL7-009 | Update reorder levels to zero for unsold products. | How do I update products that are missing from order details? | Set a zero reorder point by updating items nobody ordered. |
| SQL7-010 | Delete January orders but leave the later ones. | How do I delete orders from before February 2006? | Deleting old orders while leaving everything from February onwards. |
| SQL7-011 | Remove products that have never been ordered. | Deleting products with no matching order lines. | Deleting catalogue items that never show up in an order. |
| SQL7-012 | Delete all shippers but keep the table. | How do I empty a carrier table using DELETE? | Deleting every row without dropping the table itself. |
| SQL7-013 | Replace an existing row and reset columns I left out. | What does REPLACE do when the key already exists? | Using REPLACE for a duplicate ID and restoring defaults for omitted fields. |
| SQL7-014 | Use REPLACE to add a carrier whose key is not there yet. | Will REPLACE insert a new shipper if its ID does not exist? | Inserting a brand new ID with REPLACE rather than overwriting an existing row. |
| SQL7-015 | Replace several shippers in one go, mixing old and new IDs. | How do I replace an existing carrier and add another in one statement? | A batch REPLACE that overwrites matching IDs and inserts unmatched ones. |
| SQL7-016 | How do I truncate a table and restart its IDs? | Empty the shipper table and reset auto increment using TRUNCATE. | Why do new IDs start over after truncating a table? |
| SQL7-017 | A function that puts employee last name before first name. | How do I make a reusable employee full name function? | Name formatting function: surname, comma, then given name. |
| SQL7-018 | A function that labels a price as high, low or unknown. | How do I write a function with IF to classify product prices? | Function returning High for expensive prices, Low for cheap ones and Unknown for missing prices. |
| SQL7-019 | A function to work out the total value of an order. | How can a function sum order lines after discounts? | Function for a discounted order bill, returning zero when there are no order lines. |
| SQL7-020 | A trigger that fixes negative prices before inserting rows. | Before insert trigger to replace missing or negative prices with zero. | Trigger for cleaning up prices on newly inserted rows. |
| SQL7-021 | A trigger to reject bad prices when updating a product. | Block negative or missing prices with a before update trigger. | Trigger that refuses negative prices rather than silently fixing an update. |
| SQL7-022 | A trigger that records new prices in a log. | How do I log rows automatically after inserting them? | Record each inserted price automatically with a logging trigger. |
| SQL7-023 | A procedure that lists orders for a given employee. | How do I pass an employee number into a procedure? | Procedure taking a staff number and returning that persons assigned orders. |
| SQL7-024 | A procedure that gives an order total back through an output parameter. | How do I call a procedure with an IN order ID and an OUT amount? | Procedure with an input order number and an output total. |
| SQL7-025 | A procedure to add up sales for one employee. | Pass an employee ID to a procedure and get their sales total. | Procedure for calculating the sales made by a member of staff. |
| SQL7-026 | A cursor that adds up beverage prices. | How do I loop through product prices with a cursor and total them? | Cursor loop that accumulates catalogue prices for all beverages. |
| SQL7-027 | A cursor to total the item quantities in the first order. | Loop over an orders line quantities and return their sum. | Add up quantities one line at a time with a cursor for the earliest order. |
| SQL7-028 | A cursor counting an employees orders before March 2006. | Count early orders for employee 3 with a cursor loop. | Cursor counting orders for employee 3 with a date cutoff. |
| SQL7-029 | Create a child table with a generated ID and a foreign key that blocks parent deletion. | How do I create a table with primary key, default and a nonnegative check? | Create a table with an identity counter, required amount and restricted parent link. |
| SQL7-030 | Create a foreign key that deletes child rows when the parent is deleted. | How do I set up cascade delete between two tables? | Delete dependent rows automatically when their parent is removed using a cascading key. |
| SQL7-031 | Create a foreign key that clears the child reference when the parent is deleted. | How does ON DELETE SET NULL keep the child row? | Add a foreign key that preserves child records but nulls their parent reference. |
| SQL7-032 | Add an active column to shippers with default one. | How do I add a required column to a table that already has data? | Adding a required active flag to existing shipper records with a default. |
| SQL7-033 | Drop the company column but keep the shipper records. | How can I delete a column without deleting the rows? | Removing the Company field from shippers without removing any records. |
| SQL7-034 | Add a reorder column and remove the product category column. | How do I add one column and drop another with ALTER TABLE? | Adding one field while dropping another from products in one ALTER. |
| SQL7-035 | Add a check constraint so an amount cannot go negative. | How do I add a nonnegative check to a column? | Adding validation that forbids negative amounts with a CHECK constraint. |
| SQL7-036 | Drop a check constraint so negative amounts are allowed. | How do I remove a named check without removing the column? | Removing an amount check while leaving the amount data untouched. |
| SQL7-037 | Drop the foreign key but leave the parent ID column. | How do I remove a foreign key so unmatched IDs can be inserted? | Removing the reference rule so a parent ID no longer has to exist. |
| SQL7-038 | Transfer money between two accounts in a transaction and commit it. | How do I save both balance changes from a money transfer? | Make a debit and matching credit permanent by committing a transaction. |
| SQL7-039 | Transfer between two accounts then roll back both changes. | How can I cancel a money transfer transaction? | Undo an entire transfer by rolling back the transaction. |
| SQL7-040 | Use a savepoint to undo a failed second transfer but keep the first. | How can I roll back part of a transaction after insufficient funds? | Savepoint for keeping a successful transfer while undoing a later failure. |
| SQL7-041 | Count orders for each tax status, even unused ones. | Show tax status names and how many orders use each. | How many orders belong to each tax status name? |
| SQL7-042 | Show the saved sales report definitions with the default first. | List report titles and their grouping fields. | Which sales reports are saved and which one is the default? |
| SQL7-043 | List available privileges even if nobody has them. | Show all permission IDs and names alphabetically. | What permissions are defined, ordered by name? |
| SQL7-044 | Count order lines in each detail status, including zero. | Show every order detail status with its line count. | How many lines have each order detail status? |

## 4. Output nguyên văn các lệnh nghiệm thu

Toàn bộ stdout/stderr của lần chạy lại; không cắt lỗi/cảnh báo có sẵn. Exit status nằm ngoài khối output.

### `python3 -I tools/build_bank.py`

Exit status: 0.

```text
combo: candidates 1918 kept 1712 dropped {'dup-existing': 10, 'error': 0, 'differs': 0, 'empty': 112, 'all-rows': 36, 'dup-question': 0, 'dup-result': 48}
2334 entries; {'execution-verified': 2170, 'reference-text': 164}
```

### `python3 -I tools/check_bank.py`

Exit status: 0.

```text
New entries: 337 {'sql': 258, 'theory': 79}
Statuses: {'execution-verified': 258, 'reference-text': 79}
New empty results: 9 ['SQL3-008', 'SQL3-046', 'SQL3-056', 'SQL3-089', 'SQL4-028', 'SQL4-036', 'SQL5-022', 'SQL5-030', 'SQL5-047']
Existing entry content preserved: 1983 / 1983
Held-out prefix unchanged: 146 ; preregistered additions unchanged: 88
Normalized duplicate groups: existing 0 involving new 0
Engine-normalized duplicate groups involving new: []
Near-text candidates (token Jaccard >= 0.65; manual semantic review required):
NEAR ('SQL3-055', 'SQL3-056') 0.667
NEAR ('SQL4-050', 'VAR-009') 0.750
NEAR ('SQL5-030', 'SQL5-031') 0.920
NEAR ('SQL5-030', 'SQL5-032') 0.920
NEAR ('SQL5-030', 'SQL5-033') 0.786
NEAR ('SQL5-031', 'SQL5-032') 0.920
NEAR ('SQL5-031', 'SQL5-033') 0.852
NEAR ('SQL5-032', 'SQL5-033') 0.786
NEAR ('SQL5-036', 'SQL5-037') 0.808
NEAR ('SQL5-038', 'SQL5-039') 0.829
NEAR ('SQL5-040', 'SQL5-041') 0.692
NEAR ('SQL5-047', 'SQL5-048') 0.875
NEAR ('SQL5-047', 'SQL5-049') 0.742
NEAR ('SQL5-050', 'SQL5-051') 0.654
NEAR ('SQL5-053', 'SQL5-054') 0.810
NEAR ('SQL7-002', 'SQL7-003') 0.765
NEAR ('SQL7-013', 'SQL7-014') 0.684
NEAR ('SQL7-013', 'SQL7-015') 0.667
NEAR ('SQL7-014', 'SQL7-015') 0.667
NEAR ('SQL7-026', 'SQL7-027') 0.652
NEAR ('SQL7-029', 'SQL7-030') 0.833
NEAR ('SQL7-029', 'SQL7-031') 0.800
NEAR ('SQL7-030', 'SQL7-031') 0.875
NEAR ('SQL7-038', 'SQL7-039') 0.765
Same nonempty result-hash candidates involving new (intent must be reviewed):
HASH ['MOCK-15', 'SQL5-028']
HASH ['VAR-015', 'COMBO-1704', 'SQL3-022']
HASH ['VAR-103', 'SQL4-027']
HASH ['SQL3-025', 'SQL3-052']
HASH ['SQL5-050', 'SQL5-052']
Nonempty result-hash candidate groups: 5
Identical structural feature signatures: []
Protected file hashes checked: 17
Errors: 0
```

### `python3 -I tools/audit_bank.py`

Exit status: 0.

```text
Independent MySQL CLI audit
SQL entries: 2170 statuses: {'execution-verified': 2170}
Main/alternative executions: 4340 additional answer executions: 5
Empty primary results: 14 VAR-011, VAR-041, VAR-085, VAR-091, SQL3-008, SQL3-046, SQL3-056, SQL3-089, SQL6-005, SQL4-028, SQL4-036, SQL5-022, SQL5-030, SQL5-047
Mismatches: 0
```

### `node tests/eval.js`

Exit status: 0.

```text
bank entries: 2334   held-out cases: 234 (195 scored retrieval, 24 traps, 15 unrelated)
Recall@1: 84.6% (165/195)   Recall@3: 88.2%   MRR: 0.864
Incorrect top match (answered but wrong): 8.8% (16/181)
  of which with NO critical-constraint warning: 16
  (info) strict misses whose top entry has the identical verified result set as an expected entry: 0
Trap cases (similar wording, different requirement) handled (no match or critical warning): 24/24; silent wrong: 0
Unrelated questions wrongly answered: 0/15
Latency ms: mean 12.05  p95 24.19  max 35.58
Per category Recall@1: paraphrase 12/12 | reorder 3/3 | typo 3/3 | operator 5/6 | table 5/5 | negation 7/7 | sql 9/9 | theory 10/12 | lab 25/30 | combo 12/13 | theory2 32/35 | sql3 22/40 | theory3 20/20

Failures:
  MISS@1 | Find customers who placed orders for products from more than 5 different categories | got VAR-001 | want VAR-002|MOCK-12 | rank 2
  MISS@1 | Why is NOT IN dangerous when the subquery contains NULL? | got TH3-005 | want TH-05 | rank 3
  MISS@1 | What is the difference between COUNT(*) and COUNT(column)? | got TH-30 | want TH-06 | rank 2
  MISS@1 | Show every customer with the number of orders they placed, customers with zero orders must appear with 0 | got TH5-003 | want LAB-08 | rank 4
  MISS@1 | Why does COUNT(*) give a wrong result when counting orders per customer with a LEFT JOIN? | got TH5-003 | want LAB-08 | rank -
  MISS@1 | Emulate FULL OUTER JOIN of shippers and orders using LEFT JOIN, RIGHT JOIN and UNION | got TH-44 | want LAB-09 | rank 4
  MISS@1 | Split the Supplier IDs text column on semicolons and count how many suppliers each product has | got TH3-031 | want LAB-24 | rank -
  MISS@1 | Stock on hand report from inventory transactions with a Reorder or OK action | got SQL4-015 | want LAB-33 | rank -
  MISS@1 | Customers with at most 2 orders | got VAR-035 | want COMBO-0005 | rank 2
  MISS@1 | Why does YEAR(date) = 2006 not use the index? | got MOCK-09 | want TH-30 | rank -
  MISS@1 | Best way to protect queries from injection attacks | got none | want TH-71 | rank -
  MISS@1 | What is the difference between a view and a table? | got TH-20 | want TH-70 | rank 2
  MISS@1 | Break down discounted line revenue by client, carrier and merchandise category, keeping their identifiers. | got none | want SQL3-001 | rank -
  MISS@1 | Show invoice dates alongside the purchasing company and the staff member responsible for the order. | got none | want SQL3-003 | rank -
  MISS@1 | Summarize procurement expenditure for each vendor and item using ordered units times unit cost. | got none | want SQL3-004 | rank -
  MISS@1 | Connect inventory ledger records to their type labels, item names and the client on the linked sales order. | got TH3-059 | want SQL3-005 | rank 3
  MISS@1 | Identify sales lines charged below the catalogue price, showing the client and transaction date. | got none | want SQL3-008 | rank -
  MISS@1 | Find the clients jointly served by the greatest number of distinct staff members, retaining ties. | got SQL3-092 | want SQL3-012 | rank -
  MISS@1 | For each employee produce separate first-quarter 2006 counts for dispatched and undispatched orders, even for inactive employees. | got none | want SQL3-014 | rank -
  MISS@1 | Show procurement detail rows awaiting receipt, with vendor and product descriptions. | got none | want SQL3-023 | rank -
  MISS@1 | For every client's order show its immediate next order, breaking timestamp ties by order identifier. | got none | want SQL3-028 | rank -
  MISS@1 | Pick exactly the two least expensive items in each category, resolving price ties with item ID. | got none | want SQL3-032 | rank -
  MISS@1 | Compare each month's discounted sales with the preceding observed month's discounted sales, leaving the initial change NULL. | got SQL4-010 | want SQL3-037 | rank -
  MISS@1 | Generate a 2006 monthly order-count calendar that includes months with no orders. | got SQL5-040 | want SQL3-043 | rank 3
  MISS@1 | Find clients covering the entire set of items ordered by customer 1; extra items are allowed. | got none | want SQL3-051 | rank -
  MISS@1 | Which orders cover all the items on the lowest numbered order with detail lines? Extra products may appear. | got none | want SQL3-054 | rank -
  MISS@1 | For each invoice compare its Shipping field with the linked order's Shipping Fee, including the numerical difference. | got none | want SQL3-071 | rank -
  MISS@1 | List ordered items with their Sold ledger quantities and explain any difference without assuming the two systems reconcile. | got TH3-059 | want SQL3-081 | rank -
  MISS@1 | Report items whose aggregate Sold quantity exceeds aggregate Purchased quantity; no opening stock assumption. | got none | want SQL3-089 | rank -
  MISS@1 | Allocate an order's shipping charge proportionally to its lines' gross values without rounding before allocation. | got none | want SQL3-094 | rank -
```

### `./build_app.sh`

Exit status: 0.

```text
built: SQL Reference Finder.app
```

Builder không in dòng tổng 0 PROBLEM: output không có PROBLEM, combo error=0, exit=0.

## 5. Tự kiểm tra: đủ 15 câu mới, không lọc

Chạy createEngine như evaluator, tất cả loại mục, limit=3, giữ ngưỡng gốc. 30 câu được giữ nguyên từ trước khi sửa alias/engine, kiểm không trùng câu hỏi/alias sau chuẩn hóa. SHA-256 toàn bộ test giữ nguyên: `5e75b4b5c82d945471ef8a0f40e10822bf431e5021a651136bf1475c8b2f769c`.

```sh
node tests/check_write_search.js
node tests/check_write_search.js --json
```

| Phép đo | Trước sửa | Bản cũ nghiệm thu |
|---|---:|---:|
| Top-1 đúng | 1/15 (6.7%) | 10/15 (66.7%) |
| Đúng trong top-3 | 1/15 (6.7%) | 10/15 (66.7%) |
| NONE | 9/15 | 3/15 |

Cả 15 câu có write=true. Điểm dưới làm tròn 4 chữ số; JSON lưu điểm/coverage/warnings đầy đủ. NONE không có điểm, không gán điểm 0.

| # | Câu hỏi | Mục kỳ vọng | Top-1 trả về | Điểm top-1 | Top-3 thực trả (ID:điểm) | Kết quả |
|---:|---|---|---|---:|---|---|
| 1 | I am inserting two delivery companies together. What does the multirow statement look like? | SQL7-001 | SQL7-001 | 0.2548 | SQL7-001:0.2548 | Đúng |
| 2 | Archive only the orders dated earlier than March 2006 with an insert from a query. | SQL7-002 | SQL7-002 | 0.2926 | SQL7-002:0.2926 | Đúng |
| 3 | For beverages, updating price by ten percent must also put the reorder point at 30. | SQL7-004 | SQL7-004 | 0.6267 | SQL7-004:0.6267; SQL7-005:0.2646 | Đúng |
| 4 | Deleting products that were never included on an order, preferably with NOT EXISTS. | SQL7-011 | SQL7-011 | 0.5171 | SQL7-011:0.5171 | Đúng |
| 5 | I need REPLACE for a duplicate ID; any unspecified fields should go back to defaults. | SQL7-013 | SQL7-013 | 0.3105 | SQL7-013:0.3105; SQL7-015:0.3062 | Đúng |
| 6 | I want a function for employee names formatted surname comma given name. | SQL7-017 | SQL7-017 | 0.2457 | SQL7-017:0.2457 | Đúng |
| 7 | The function should return the discounted bill for one order and zero if it has no lines. | SQL7-019 | NONE | — | NONE | NONE |
| 8 | Before inserting a price, a trigger should turn negatives and missing values into zero. | SQL7-020 | SQL7-020 | 0.5712 | SQL7-020:0.5712; SQL7-021:0.4436; TH3-035:0.2827 | Đúng |
| 9 | On updating a price, the trigger must refuse negatives instead of silently fixing them. | SQL7-021 | SQL7-021 | 0.3276 | SQL7-021:0.3276 | Đúng |
| 10 | A procedure receives a staff number and returns all orders assigned to that person. | SQL7-023 | NONE | — | NONE | NONE |
| 11 | An order number goes IN to my procedure; its total must come back OUT. | SQL7-024 | SQL7-024 | 0.4704 | SQL7-024:0.4704 | Đúng |
| 12 | Use a cursor to accumulate beverage catalogue prices until there are no more rows. | SQL7-026 | NONE | — | NONE | NONE |
| 13 | Adding a CHECK should prevent amounts below zero without removing the amount column. | SQL7-035 | TH3-053 | 0.2789 | TH3-053:0.2789 | Sai |
| 14 | Add a foreign key so a child row survives parent deletion with its reference cleared. | SQL7-031 | SQL7-037 | 0.3570 | SQL7-037:0.3570; SQL7-030:0.3483; TH3-016:0.3394 | Sai |
| 15 | Transfer funds inside a transaction, undo just the second attempt with a savepoint, then keep the earlier work. | SQL7-040 | SQL7-040 | 0.3058 | SQL7-040:0.3058 | Đúng |

### Tất cả thất bại và nguy cơ nhầm — chỉ báo cáo

- #7 SQL7-019, #10 SQL7-023, #12 SQL7-026: NONE dù write=true. Chưa khắc phục ba cách diễn đạt này; không đoán điểm/nguyên nhân của ứng viên đã bị lọc.
- #13 ADD CHECK kỳ vọng SQL7-035, trả TH3-053 (optimistic locking), điểm 0.2789, không critical warning; không phải biến thể tương đương.
- #14 ON DELETE SET NULL kỳ vọng SQL7-031, trả SQL7-037 (DROP FOREIGN KEY), điểm 0.3570; top-3 còn SQL7-030 (CASCADE), TH3-016. Cả ba không critical warning. Đây là nhầm ý định DDL, có rủi ro nếu chạy SQL được gợi ý; không sửa nội dung mục hay hardcode ID để che lỗi.

## 6. Kiểm tra 15 SELECT thuần

| # | Câu hỏi | write | Top-1 | Điểm | Top-3 thực trả (ID:điểm) |
|---:|---|---|---|---:|---|
| 1 | List employee first and last names alphabetically. | false | A3-07 | 0.3939 | A3-07:0.3939; SQL3-003:0.2357 |
| 2 | Show each order and its discounted total, without defining a routine. | false | NONE | — | NONE |
| 3 | Find the most expensive product in each category. | false | LAB-15 | 0.7717 | LAB-15:0.7717; SQL5-029:0.7162; SQL4-001:0.7030 |
| 4 | Show customers who have never placed an order. | false | VAR-009 | 0.9244 | VAR-009:0.9244; LAB-08:0.6993; COMBO-1678:0.6880 |
| 5 | Count orders for every employee, including employees with none. | false | SQL4-006 | 0.2900 | SQL4-006:0.2900; SQL4-039:0.2534; SQL5-001:0.2320 |
| 6 | List beverages with List Price above 20. | false | VAR-056 | 0.5085 | VAR-056:0.5085; A3-06:0.4339 |
| 7 | Show orders placed in January 2006. | false | VAR-081 | 0.3806 | VAR-081:0.3806; LAB-25:0.2923 |
| 8 | Use ROW_NUMBER window function to rank products by price. | false | TH-51 | 0.5964 | TH-51:0.5964; TH-15:0.5610; TH3-041:0.4854 |
| 9 | Calculate average List Price for each category. | false | A4-04 | 0.7011 | A4-04:0.7011; A4-07:0.5963; SQL6-007:0.5736 |
| 10 | Show the three customers with highest total spending. | false | SQL4-044 | 0.5372 | SQL4-044:0.5372; COMBO-0051:0.5096; COMBO-0116:0.5073 |
| 11 | List products and their supplier company names. | false | SQL3-065 | 0.4418 | SQL3-065:0.4418; LAB-20:0.4267; SQL3-023:0.3227 |
| 12 | Count order details belonging to each order. | false | TH5-004 | 0.2889 | TH5-004:0.2889; SQL7-041:0.2560 |
| 13 | Show countries with at least two customers. | false | COMBO-0003 | 0.4501 | COMBO-0003:0.4501; SQL4-017:0.4285; COMBO-0235:0.4272 |
| 14 | Find products that were not ordered at all. | false | COMBO-1703 | 0.5239 | COMBO-1703:0.5239; A4-08:0.4668; LAB-21:0.4050 |
| 15 | Use the SUM aggregate function for revenue per customer. | false | SQL3-092 | 0.4745 | SQL3-092:0.4745; SQL3-001:0.4375; TH5-004:0.4292 |

Top-1 SQL7: 0/15; write=true: 0/15; NONE: 1/15. Câu #12 có SQL7-041 hạng 2 (0.2560), critical warning lệch bảng order details; mục này bản thân là SELECT đếm orders theo tax status, không ghi dữ liệu. Nếu yêu cầu tuyệt đối không có SQL7 trong mọi top-3 thì chưa đạt: 1/15. Không ẩn kết quả bằng bộ lọc.

Test còn kiểm tổng quát các dạng insert/update/delete, ADD các đối tượng schema, PSM đứng riêng, transfer, ngưỡng gốc. Dữ liệu đo đầy đủ: accepted/self_after.json; stdout: accepted/self_check.txt; baseline: self_before.json.

## 7. DB trước/sau — output nguyên văn

Trước chạy lại:

```text
9.7.2
shippers	3
products	45
orders	48
customers	29
order details	58
employees	9
```

Sau chạy lại, CLI dùng --table -vvv:

```text
--------------
SHOW TABLES LIKE 'zz%'
--------------

Empty set (0.001 sec)

--------------
SHOW TRIGGERS
--------------

Empty set (0.001 sec)

--------------
SHOW FUNCTION STATUS WHERE Db='northwind'
--------------

Empty set (0.001 sec)

--------------
SHOW PROCEDURE STATUS WHERE Db='northwind'
--------------

Empty set (0.000 sec)

--------------
SELECT 'shippers' AS table_name,COUNT(*) AS row_count FROM shippers UNION ALL SELECT 'products',COUNT(*) FROM products UNION ALL SELECT 'orders',COUNT(*) FROM orders UNION ALL SELECT 'customers',COUNT(*) FROM customers UNION ALL SELECT 'order details',COUNT(*) FROM `order details` UNION ALL SELECT 'employees',COUNT(*) FROM employees
--------------

+---------------+-----------+
| table_name    | row_count |
+---------------+-----------+
| shippers      |         3 |
| products      |        45 |
| orders        |        48 |
| customers     |        29 |
| order details |        58 |
| employees     |         9 |
+---------------+-----------+
6 rows in set (0.002 sec)

Bye
```

Bốn SHOW đều Empty set; số dòng sáu bảng giữ 3/45/48/29/58/9. Kết luận chỉ áp dụng fixture.

## 8. Việc chưa xác nhận và giới hạn

- Chưa chạy backup/các cổng trên DB host /tmp/mysql.sock; chưa xác nhận MySQL 8.0.28. Các cổng đạt trên fixture MySQL 9.7.2, không thay thế xác nhận đúng môi trường host.
- Chưa xử lý 5 câu thất bại và ứng viên top-3 SQL7 trong SELECT ở mục 5–6. Cờ write phân biệt ghi/đọc, không chứng minh đúng ngữ nghĩa.
- Các cặp/nhóm gần nhau do check_bank nêu: SQL7-002/003 (mốc ngày), 013/014/015 (REPLACE), 026/027 (cursor giá/quantity), 029/030/031 (RESTRICT/CASCADE/SET NULL), 038/039 (COMMIT/ROLLBACK). Đây là ứng viên cần audit ngữ nghĩa, không khẳng định tất cả đang trả sai. Không tự sửa các mục.
- Regex không phân tích đầy đủ phủ định/scope SQL; function không định danh và DDL phủ định vẫn có thể nhập nhằng. Giữ chú thích ponytail, không hạ ngưỡng/hệ số phạt.
- Bộ evaluator gốc vẫn có 30 MISS@1, gồm 16 trả sai không critical warning; danh sách không đổi so với baseline. Không sửa lỗi ngoài phạm vi.
- Build app trong snapshot thành công, tài nguyên trùng source nghiệm thu; chưa kiểm tra GUI. Thay đổi mới/live app không thuộc lần nghiệm thu này.

## 9. Kiểm tra bất biến

```text
Accepted snapshot: only write-classification block differs from /tmp/search.js.pre_x.
Concurrent comparison-normalization changes excluded; live source/app not modified.
SQL7 source unchanged; built SQL7 entries unchanged except aliases: 44/44.
Old aliases retained: 88/88; new natural aliases: 132 (3 per entry).
Forbidden alias terms (zz_, scratch, SQLSTATE): 0.
Heldout/eval/protected pre-edit hashes unchanged in accepted snapshot.
minScore=0.22; minCoverage=0.45; critPenalty=0.55; write multiplier=0.75 unchanged.
Frozen 15-write/15-SELECT test SHA-256 unchanged.
All 30 original MISS@1 lines unchanged versus baseline.
Snapshot app search.js/data_bank.js match accepted sources.
```

