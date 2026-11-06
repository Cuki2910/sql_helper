# M6-AdvancedSQL_no_merge

- Nguồn: [M6-AdvancedSQL_no_merge.pptx](M6-AdvancedSQL_no_merge.pptx)

- Số slide: 12.

- Chủ đề: ALTER TABLE, AUTO_INCREMENT, thêm cột, NOT NULL, CHECK, FOREIGN KEY, ON UPDATE/DELETE, xóa cột/ràng buộc.

> Bản trích xuất giữ nguyên ngôn ngữ và nội dung nguồn, không sửa kiến thức hoặc cú pháp SQL. Ví dụ có thể chứa lỗi gốc, dấu nháy cong, cú pháp riêng của DBMS hoặc câu lệnh cố ý dùng để thử lỗi; không mặc định coi mọi đoạn SQL là chạy được. Phần OCR được đánh dấu riêng; đối chiếu ảnh gốc khi cần độ chính xác.

## Mục lục

- [Slide 01: Databases and Database Systems](#slide-01)
- [Slide 02: Advanced SQL](#slide-02)
- [Slide 03: LEARNING OBJECTIVES (1)](#slide-03)
- [Slide 04: LEARNING OBJECTIVES (2)](#slide-04)
- [Slide 05: SQL ALTER TABLE Statement](#slide-05)
- [Slide 06: ALTER TABLE – Adding a Column to an Existing Table](#slide-06)
- [Slide 07: ALTER TABLE – Adding a Column to an Existing Table](#slide-07)
- [Slide 08: Adding a Table Constraint to an Existing Table](#slide-08)
- [Slide 09: Adding a Table Constraint to an Existing Table](#slide-09)
- [Slide 10: Adding a Referential Integrity Constraint to an Existing Table](#slide-10)
- [Slide 11: Removing a Table Column/Constraint from an Existing Table](#slide-11)
- [Slide 12: QnA!](#slide-12)

<a id="slide-01"></a>

## Slide 01: Databases and Database Systems

Le Duy Dung (Andrew)

![Ảnh gốc, slide 01](<assets/m6-alter-table/slide-01-image-01.png>)

<a id="slide-02"></a>

## Slide 02: Advanced SQL

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="slide-03"></a>

## Slide 03: LEARNING OBJECTIVES (1)

To understand reasons for using the SQL ALTER  statement

To use the SQL ALTER statement

To understand the need for additional types of SQL queries

To use SQL outer join queries

To use SQL correlated subqueries

To use SQL queries on recursive relationships

<a id="slide-04"></a>

## Slide 04: LEARNING OBJECTIVES (2)

To understand the reasons for using SQL set operators

To use SQL set operators

To understand the reasons for using SQL views

To use SQL statements to create and use SQL views

To understand SQL/Persistent Stored Modules (SQL/PSM)

To use SQL statements to create and use SQL user-defined functions

<a id="slide-05"></a>

## Slide 05: SQL ALTER TABLE Statement

The SQL ALTER TABLE statement is used to modify the structure of a table once it has been created in a database.

Can be used to add, modify, and drop columns and constraints

Very useful to modify the AUTO_INCREMENT starting value in MySQL 8.0

Example:

```sql
/* *** EXAMPLE CODE – THIS STATEMENT HAS ALREADY BEEN RUN *** */
 ALTER TABLE CATALOG_SKU_2017 AUTO_INCREMENT = 20170001;
```

<a id="slide-06"></a>

## Slide 06: ALTER TABLE – Adding a Column to an Existing Table

The SQL ALTER TABLE statement can be used to add a column to an. existing table as seen below.

```sql
ALTER TABLE {TableName}
ADD {ColumnName} {DataType} {OptionalColumnConstraints};
```

Example:

```sql
ALTER TABLE PRODUCTION_ITEM
ADD ApprovalDate DATE NULL;
```

<a id="slide-07"></a>

## Slide 07: ALTER TABLE – Adding a Column to an Existing Table

The SQL ALTER TABLE statement can be used to add a column to an. existing table as seen below.

```sql
ALTER TABLE {TableName}
ADD {ColumnName} {DataType} {OptionalColumnConstraints};
```

Note that the SQL COLUMN keyword is not used in an ADD {COLUMN} clause. MySQL does allow it but is not required!

The above statement is sufficient if adding a column that allows NULL values. If a NOT NULL column constraint exists then the following steps must be used:

Add the column as column that allows NULL values.

Update all table rows with data values in the new column.

Modify the column to see the NOT NULL constraint.

<a id="slide-08"></a>

## Slide 08: Adding a Table Constraint to an Existing Table

To use the SQL ALTER statement

The SQL ALTER TABLE statement can be used to add a table constraint to an existing table. The basic syntax is:

```sql
ALTER TABLE {TableName}
	ADD CONSTRAINT {ConstraintName} {TableConstraint};
```

Note that the SQL CONSTRAINT keyword is used in an ADD CONSTRAINT clause

Note the addition of the CHECK constraint below.

```sql
ALTER TABLE PRODUCTION_ITEM
ADD CONSTRAINT CheckProductionDate CHECK
            (ApprovalDate < ProductionStartDate);
```

<a id="slide-09"></a>

## Slide 09: Adding a Table Constraint to an Existing Table

To use the SQL ALTER statement

The SQL ALTER TABLE statement can be used to add a table constraint to an existing table. The basic syntax is:

```sql
ALTER TABLE {TableName}
	ADD CONSTRAINT {ConstraintName} {TableConstraint};
```

Note that the SQL CONSTRAINT keyword is used in an ADD CONSTRAINT clause

Note the addition of the CHECK constraint below.

```sql
ALTER TABLE PRODUCTION_ITEM
ADD CONSTRAINT CheckProductionDate CHECK
            (ApprovalDate < ProductionStartDate);
```

![Ảnh gốc, slide 09](<assets/m6-alter-table/slide-09-image-01.jpg>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

DDL for wp.production_item

```sql
CREATE TABLE `production_item` (
  `SKU` int(11) NOT NULL,
  `SKU_Description` char(35) NOT NULL,
  `ProductionStartDate` date DEFAULT NULL,
  `ProductionEndDate` date DEFAULT NULL,
  `QuantityOnHand` int(11) DEFAULT NULL,
  `QuantityInProduction` int(11) DEFAULT NULL,
  `ApprovalDate` date NOT NULL,
  PRIMARY KEY (`SKU`),
  CONSTRAINT `CheckProductionDate` CHECK ((`ApprovalDate` < `ProductionStartDate`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

- Right-click the **production_item** table, then click **Table Inspector**, then click the **DDL** tab.
- The DDL tab shows the SQL CREATE TABLE statement needed to create the table as it currently exists—Note that this statement now contains the CHECK constraint.
- The ALTER TABLE statement that created the CHECK constraint is shown in Action Output.

MySQL Community Server 8.0, MySQL Workbench, Oracle Corporation.

<a id="slide-10"></a>

## Slide 10: Adding a Referential Integrity Constraint to an Existing Table

The SQL ALTER TABLE statement can be used to add a referential integrity constraint to an existing table. The basic syntax is:

```sql
ALTER TABLE {TableName}
	ADD CONSTRAINT {ConstraintName} FOREIGN KEY({ColumnName})
	      REFERENCES {TableName}({PrimaryKeyColumn})
		{Optional ON UPDATE clause}
		{Optional ON DELETE clause};

ALTER TABLE CATALOG_SKU_2018
	ADD CONSTRAINT CAT16_PROD_ITEM_FK FOREIGN KEY(SKU)
		REFERENCES PRODUCTION_ITEM(SKU)
			ON UPDATE NO ACTION
			ON DELETE NO ACTION;
```

<a id="slide-11"></a>

## Slide 11: Removing a Table Column/Constraint from an Existing Table

The SQL ALTER TABLE statement can be used to remove a column from a table. Note that the SQL COLUMN keyword is used in the DROP COLUMN clause. The basic syntax is:

```sql
ALTER TABLE {TableName}
	DROP COLUMN {ColumnName};
```

The SQL ALTER TABLE statement can be used to remove a table constraint. Note that the SQL CONSTRAINT keyword is used in the DROP CONSTRAINT clause. The basic syntax is:

```sql
ALTER TABLE {TableName}
DROP CONSTRAINT {ConstraintName};
```

<a id="slide-12"></a>

## Slide 12: QnA!

![Ảnh gốc, slide 12](<assets/m6-alter-table/slide-12-image-01.png>)
