# M3-Part 7 - Insert, Delete, Update

- Nguồn: [M3-Part 7 - Insert, Delete, Update.pdf](M3-Part%207%20-%20Insert%2C%20Delete%2C%20Update.pdf)

- Số trang: 20.

- Chủ đề: INSERT, INSERT có danh sách cột, partial rows, UPDATE, subquery trong UPDATE, DELETE, an toàn khi sửa/xóa dữ liệu.

> Bản trích xuất giữ nguyên ngôn ngữ và nội dung nguồn, không sửa kiến thức hoặc cú pháp SQL. Ví dụ có thể chứa lỗi gốc, dấu nháy cong, cú pháp riêng của DBMS hoặc câu lệnh cố ý dùng để thử lỗi; không mặc định coi mọi đoạn SQL là chạy được. Phần OCR được đánh dấu riêng; đối chiếu ảnh gốc khi cần độ chính xác.

## Mục lục

- [Trang 01: Database Concepts and Skills for Big Data](#page-01)
- [Trang 02: SQL – Part 7](#page-02)
- [Trang 03: Insert Data](#page-03)
- [Trang 04: Inserting Data](#page-04)
- [Trang 05: Inserting Complete Rows](#page-05)
- [Trang 06: Inserting Data](#page-06)
- [Trang 07: Inserting Complete Rows](#page-07)
- [Trang 08: Inserting Data](#page-08)
- [Trang 09: Inserting Data](#page-09)
- [Trang 10: Insert partial rows](#page-10)
- [Trang 11: Update Data](#page-11)
- [Trang 12: Updating Data](#page-12)
- [Trang 13: Updating Data](#page-13)
- [Trang 14: Updating Multiple Columns](#page-14)
- [Trang 15: Using Subqueries in an UPDATE Statement](#page-15)
- [Trang 16: Delete Data](#page-16)
- [Trang 17: Deleting Data](#page-17)
- [Trang 18: Deleting Data](#page-18)
- [Trang 19: Guidelines for Updating and Deleting](#page-19)
- [Trang 20: QnA!](#page-20)

<a id="page-01"></a>

## Trang 01: Database Concepts and Skills for Big Data

Le Duy Dung (Andrew)

<a id="page-02"></a>

## Trang 02: SQL – Part 7

Insert, Delete, Update

<a id="page-03"></a>

## Trang 03: Insert Data

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="page-04"></a>

## Trang 04: Inserting Data

As  its name suggests, INSERT  is used to insert (add) rows to a database table. Insert can be used in several ways:

- Inserting a single complete row

- Inserting a single partial row

- Inserting the results of a query

<a id="page-05"></a>

## Trang 05: Inserting Complete Rows

The simplest way to insert data into a table is to use the basic INSERT syntax, which requires that you specify the table name and the values to be inserted into the new row. &lt;Example&gt;

```sql
INSERT INTO CUSTOMER

VALUES(11, 'Andrew', 'Le', 'VinUniversity', 'Hanoi', 'HN', '99999',
'984780258', 'dung.ld@vinuni.edu.vn');
```

<a id="page-06"></a>

## Trang 06: Inserting Data

&lt;Example&gt;

```sql
INSERT INTO CUSTOMER
VALUES(11, 'Andrew', 'Le', 'VinUniversity', 'Hanoi', 'HN', '99999',
'984780258', 'dung.ld@vinuni.edu.vn’);
```

- The data to be stored  in each table column  is specified  in the VALUES clause, and a value must be provided for every column.

- If a column has no value, the NULL value should be used (assuming the table allows no value to be specified for that column).

- The columns must be populated in the order in which they appear in the table definition.

<a id="page-07"></a>

## Trang 07: Inserting Complete Rows

&lt;Example&gt;

```sql
INSERT INTO CUSTOMER
VALUES(11, 'Andrew', 'Le', 'VinUniversity', 'Hanoi', 'HN', '99999',
'984780258', 'dung.ld@vinuni.edu.vn’);
```

- The above SQL statement  is highly dependent on the order in which the columns are defined in the table.

- It also depends on information about that order being readily  available. Even  if  it is available, there is no guarantee that the columns will be in the exact same order the next time the table is reconstructed.

<a id="page-08"></a>

## Trang 08: Inserting Data

&lt;Example&gt;

```sql
INSERT INTO CUSTOMER (CustomerID, FirstName, LastName, Address, City,
State, ZIP, Phone, EmailAddress)
VALUES(12, 'Andrew', 'Le', 'VinUniversity', 'Hanoi', 'HN', '99999',
'984780258', 'dung.ld@vinuni.edu.vn’);
```

- This example does the exact same thing as the previous INSERT statement, but this time the column names are explicitly stated  in parentheses after the table name.

- When the row is inserted, the DBMS will match each item in the columns list with the appropriate value in the VALUES list.

- The  first entry in VALUES corresponds to the  first specified column name. The second value corresponds to the second column name, and so on.

<a id="page-09"></a>

## Trang 09: Inserting Data

&lt;Example&gt;

```sql
INSERT INTO CUSTOMER (CustomerID, Address, City, State, ZIP, Phone, EmailAddress,
FirstName, LastName)

VALUES(13, 'VinUniversity', 'Hanoi', 'HN', '99999’, '984780258', 'dung.ld@vinuni.edu.vn’,
'Andrew', 'Le');
```

- Try this INSERT statement!!

<a id="page-10"></a>

## Trang 10: Insert partial rows

- The recommended way to use INSERT is to explicitly specify table column names.

- Using  this  syntax, you can  also omit columns. This means you provide values for only some columns, but not for others.

&lt;Example&gt;

```sql
INSERT INTO CUSTOMER (CustomerID, FirstName, LastName, Address, City, ZIP,
```

Phone)

```sql
VALUES(14, 'Andrew', 'Le', 'VinUniversity', 'Hanoi', '99999’, '984780258');
```

<a id="page-11"></a>

## Trang 11: Update Data

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="page-12"></a>

## Trang 12: Updating Data

To update  (modify)  data  in  a  table, you use  the UPDATE

statement. UPDATE can be used in two ways:

- To update specific rows in a table

- To update all rows in a table

<a id="page-13"></a>

## Trang 13: Updating Data

The basic format of an UPDATE statement is made up of three parts:

- The table to be updated

- The column names and their new values

- The filter condition that determines which rows should be updated

&lt;Example&gt;

```sql
UPDATE CUSTOMER

SET State = 'HN'

WHERE CustomerID = 14;
```

<a id="page-14"></a>

## Trang 14: Updating Multiple Columns

The basic format of an UPDATE statement is made up of three parts:

- The table to be updated

- The column names and their new values

- The filter condition that determines which rows should be updated

&lt;Example&gt;

```sql
UPDATE CUSTOMER

SET City = 'Hanoi', EmailAddress='check@gmail.com'

WHERE CustomerID = 14;
```

<a id="page-15"></a>

## Trang 15: Using Subqueries in an UPDATE Statement

Assume that Vendor 1 has bought Vendor 2. Your store needs to

```sql
update the ITEM table, change the VendorID with value of 2 to
```

value 1.

&lt;Example&gt;

```sql
UPDATE ITEM

SET VendorID=1

WHERE ItemID IN (SELECT ItemID FROM ITEM WHERE VendorID=2);
```

<a id="page-16"></a>

## Trang 16: Delete Data

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="page-17"></a>

## Trang 17: Deleting Data

To delete (remove) data from a table, you use the DELETE

statement. DELETE can be used in two ways:

- To delete specific rows from a table

- To delete all rows from a table

<a id="page-18"></a>

## Trang 18: Deleting Data

Assume that Vendor 1 has bought Vendor 2. Your store needs to

```sql
update the ITEM table, change the VendorID with value of 2 to
```

value 1.

&lt;Example&gt;

```sql
DELETE FROM VENDOR

WHERE VendorID=2;
```

<a id="page-19"></a>

## Trang 19: Guidelines for Updating and Deleting

- Never execute an UPDATE or a DELETE without a WHERE clause unless you really do intend to update and delete every row.

- Make sure every table has a primary key (refer to Lesson 12  if you have forgotten what this is), and use  it as the WHERE clause whenever possible. (You may specify individual primary keys, multiple values, or value ranges.)

- Before you use a WHERE clause with an UPDATE or a DELETE, first test  it with a SELECT to make sure it is filtering the right records; it is far too easy to write incorrect WHERE clauses.

- Use database-enforced referential integrity (refer to Lesson 12 for this one too) so that the DBMS will not allow the deletion of rows that have data in other tables related to them.

- Some DBMSs allow database administrators to impose restrictions that prevent the execution of UPDATE or DELETE without a WHERE clause. If your DBMS supports this feature, consider using it.

<a id="page-20"></a>

## Trang 20: QnA!

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*
