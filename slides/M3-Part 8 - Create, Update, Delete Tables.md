# M3-Part 8 - Create, Update, Delete Tables

- Nguồn: [M3-Part 8 - Create, Update, Delete Tables.pptx](M3-Part%208%20-%20Create%2C%20Update%2C%20Delete%20Tables.pptx)

- Số slide: 11.

- Chủ đề: CREATE TABLE, NOT NULL, ALTER TABLE, ADD/DROP COLUMN, DROP TABLE.

> Bản trích xuất giữ nguyên ngôn ngữ và nội dung nguồn, không sửa kiến thức hoặc cú pháp SQL. Ví dụ có thể chứa lỗi gốc, dấu nháy cong, cú pháp riêng của DBMS hoặc câu lệnh cố ý dùng để thử lỗi; không mặc định coi mọi đoạn SQL là chạy được. Phần OCR được đánh dấu riêng; đối chiếu ảnh gốc khi cần độ chính xác.

## Mục lục

- [Slide 01: Databases and Database Systems](#slide-01)
- [Slide 02: SQL – Part 8](#slide-02)
- [Slide 03: Create Tables](#slide-03)
- [Slide 04: Creating Tables](#slide-04)
- [Slide 05: Basic Table Creation](#slide-05)
- [Slide 06: Update Tables](#slide-06)
- [Slide 07: Updating Tables](#slide-07)
- [Slide 08: Updating Tables](#slide-08)
- [Slide 09: DELETE Tables](#slide-09)
- [Slide 10: Deleting Tables](#slide-10)
- [Slide 11: QnA!](#slide-11)

<a id="slide-01"></a>

## Slide 01: Databases and Database Systems

Le Duy Dung (Andrew)

![Ảnh gốc, slide 01](<assets/m3-part-8/slide-01-image-01.png>)

<a id="slide-02"></a>

## Slide 02: SQL – Part 8

Create, Update, Delete Tables, and Views

<a id="slide-03"></a>

## Slide 03: Create Tables

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="slide-04"></a>

## Slide 04: Creating Tables

SQL is not used just for table data manipulation. Rather, SQL can be used to perform all database and table operations, including the creation and manipulation of tables themselves.

There are generally two ways to create database tables:

Most DBMSs come with an administration tool that you can use to create and manage database tables interactively.

Tables may also be manipulated directly with SQL statements.

<a id="slide-05"></a>

## Slide 05: Basic Table Creation

To create a table using CREATE TABLE, you must specify the following information:

The name of the new table specified after the keywords CREATE TABLE.

The name and definition of the table columns separated by commas.

Example: the store decides to sell bundles, which are collections of items that will be shipped together. A new table called BUNDLE is created.

```sql
CREATE TABLE BUNDLE
    (
         BundleID INTEGER NOT NULL,
         BundlePrice DOUBLE NOT NULL
    );
```

This statement creates the BUNDLE table, containing two columns.

All two columns are required, so each contains keyword NOT NULL, preventing the insertion of columns with no value.

<a id="slide-06"></a>

## Slide 06: Update Tables

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="slide-07"></a>

## Slide 07: Updating Tables

To update table definitions, use the ALTER TABLE statement.

To change a table using ALTER TABLE, you must specify the following information

The name of the table to be altered after the keywords ALTER TABLE

The list of changes to be made

&lt;Example&gt;  To add a column to an existing table

```sql
ALTER TABLE BUNDLE
ADD BundleDescription TEXT(20);
```

<a id="slide-08"></a>

## Slide 08: Updating Tables

To update table definitions, use the ALTER TABLE statement.

To change a table using ALTER TABLE, you must specify the following information

The name of the table to be altered after the keywords ALTER TABLE

The list of changes to be made

&lt;Example&gt;  To remove a column to an existing table

```sql
ALTER TABLE BUNDLE
DROP COLUMN BundleDescription;
```

<a id="slide-09"></a>

## Slide 09: DELETE Tables

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="slide-10"></a>

## Slide 10: Deleting Tables

Deleting tables (actually removing the entire table, not just the contents) is very easy—arguably too easy.

Tables are deleted using the DROP TABLE statement:

&lt;Example&gt;

```sql
DROP TABLE BUNDLE;
```

<a id="slide-11"></a>

## Slide 11: QnA!

![Ảnh gốc, slide 11](<assets/m3-part-8/slide-11-image-01.png>)
