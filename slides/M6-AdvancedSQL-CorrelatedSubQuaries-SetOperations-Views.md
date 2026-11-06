# M6-AdvancedSQL-CorrelatedSubQuaries-SetOperations-Views

- Nguồn: [M6-AdvancedSQL-CorrelatedSubQuaries-SetOperations-Views.pptx](M6-AdvancedSQL-CorrelatedSubQuaries-SetOperations-Views.pptx)

- Số slide: 18.

- Chủ đề: Correlated subqueries, EXISTS/NOT EXISTS, recursive relationships, UNION/INTERSECT/EXCEPT, CREATE VIEW và các ví dụ view.

> Bản trích xuất giữ nguyên ngôn ngữ và nội dung nguồn, không sửa kiến thức hoặc cú pháp SQL. Ví dụ có thể chứa lỗi gốc, dấu nháy cong, cú pháp riêng của DBMS hoặc câu lệnh cố ý dùng để thử lỗi; không mặc định coi mọi đoạn SQL là chạy được. Phần OCR được đánh dấu riêng; đối chiếu ảnh gốc khi cần độ chính xác.

## Mục lục

- [Slide 01: Databases and Database Systems](#slide-01)
- [Slide 02: Advanced SQL](#slide-02)
- [Slide 03: LEARNING OBJECTIVES (1)](#slide-03)
- [Slide 04: LEARNING OBJECTIVES (2)](#slide-04)
- [Slide 05: SQL Correlated Subqueries](#slide-05)
- [Slide 06: SQL Subqueries Using the EXISTS and NOT EXISTS Comparison Operators](#slide-06)
- [Slide 07: SQL Subqueries Using the EXISTS and NOT EXISTS Comparison Operators](#slide-07)
- [Slide 08: SQL Queries on Recursive Relationships](#slide-08)
- [Slide 09: SQL Set Operators](#slide-09)
- [Slide 10: SQL Set Operators (bảng và sơ đồ)](#slide-10)
- [Slide 11: Creating and Working with SQL Views](#slide-11)
- [Slide 12: Creating and Working with SQL Views](#slide-12)
- [Slide 13: Minh họa viewCustomerContacts (ảnh)](#slide-13)
- [Slide 14: Creating SQL Views](#slide-14)
- [Slide 15: Some Uses of SQL Views](#slide-15)
- [Slide 16: Some Uses of SQL Views](#slide-16)
- [Slide 17: Some Uses of SQL Views](#slide-17)
- [Slide 18: QnA!](#slide-18)

<a id="slide-01"></a>

## Slide 01: Databases and Database Systems

Le Duy Dung (Andrew)

![Ảnh gốc, slide 01](<assets/m6-subqueries-sets-views/slide-01-image-01.png>)

<a id="slide-02"></a>

## Slide 02: Advanced SQL

*Slide/trang phân đoạn; chỉ có tiêu đề như trên.*

<a id="slide-03"></a>

## Slide 03: LEARNING OBJECTIVES (1)

To understand reasons for using the SQL ALTER  statement

To use the SQL ALTER statement

To understand the need for the SQL MERGE statement

To use the SQL MERGE statement

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

## Slide 05: SQL Correlated Subqueries

A correlated subquery works very differently than a regular subquery.

A regular subquery processes from the bottom up whereas a correlated subquery takes a value from the table in the query and compares it to every row in the subquery and then repeats for the next value in the main query.

A correlated subquery will use the same table in both the main and subquery and only differentiate them by using a version.

Example:

```sql
SELECT      E1.EmployeeNumber, E1.FirstName, E1.LastName
FROM         EMPLOYEE AS E1
WHERE      E1.LastName IN
                 (SELECT	E2.LastName
	      FROM   	EMPLOYEE AS E2
	      WHERE  	E1.LastName = E2.LastName
	        AND    	E1.EmployeeNumber <> E2.EmployeeNumber);
```

What is the result of this SQL statement?

<a id="slide-06"></a>

## Slide 06: SQL Subqueries Using the EXISTS and NOT EXISTS Comparison Operators

The use of EXISTS and NOT EXISTS creates another form of a correlated subquery.

These operators simply test whether there are any values returned by the subquery,  which indicates there are values meeting the conditions of the subquery.

If one or more values are returned, then values from the subquery are used to run the top-level query.

If no values are returned, the top-level query produces an empty set as the result.

Example:

```sql
SELECT      E1.EmployeeNumber, E1.FirstName, E1.LastName
FROM         EMPLOYEE AS E1
WHERE      EXISTS
                 (SELECT	E2.LastName
	      FROM   	EMPLOYEE AS E2
	      WHERE  	E1.LastName = E2.LastName
	       AND    	E1.EmployeeNumber <> E2.EmployeeNumber);
```

What is the result of this SQL statement?

<a id="slide-07"></a>

## Slide 07: SQL Subqueries Using the EXISTS and NOT EXISTS Comparison Operators

![Ảnh gốc, slide 07](<assets/m6-subqueries-sets-views/slide-07-image-01.jpg>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

SQL Comparison Operators

| Operator | Meaning |
| --- | --- |
| EXISTS | Is a non-empty set of values |
| NOT EXISTS | Is an empty set |

Copyright © 2020 by Pearson Education, Inc.

<a id="slide-08"></a>

## Slide 08: SQL Queries on Recursive Relationships

Recursive relationships use the same technique we just used in correlated subqueries.  This gives two virtual tables with the queries using them written just the same as we would any other query.

The following query will show which employees are supervisors (represented by an “s”) and which employees (represented by an “e”) they supervise.

```sql
SELECT	S.FirstName AS SupervisorFirstName,
```

S.LastName AS SupervisorLastName,

E.FirstName AS EmployeeFirstName,

E.LastName AS EmployeeLastName

```sql
FROM     	EMPLOYEE S JOIN EMPLOYEE E
	ON      	      S.EmployeeNumber = E.Supervisor
ORDER BY     S.EmployeeNumber;
```

<a id="slide-09"></a>

## Slide 09: SQL Set Operators

Mathematicians use the term set theory to describe mathematical operations on sets, where a set is defined as a group of distinct items.

Venn diagrams are the standard method of visualizing sets and their relationships. Some definitions of sets are:

A set is represented by a labeled circle.

A subset is a portion of a set that is contained entirely within the set.

The union of two sets represents the two sets together to get a set that contains all values in both sets. This is equivalent to an OR logical operation (A OR B).

The intersection of two sets represents the area common to both sets. This is equivalent to an AND logical operation (A AND B).

The complement of set B in set A represents everything in set A that is not in set B. This is equivalent to a logical operation using A AND (NOT B). It is equivalent to the set difference (A – B).

![Ảnh gốc, slide 09](<assets/m6-subqueries-sets-views/slide-09-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
(a) A Set
(b) A Subset
The Union is the entire
area of both sets
B
(c) The Union of Two Sets
The Intersection is the
middle area common
to both sets
A
B
(d) The Intersection of Two Sets
The Complement is
the area in A that is not
in B
(e) The Complement of Two Sets
Copyright © 2020 by Pearson Education, Inc.
```

<a id="slide-10"></a>

## Slide 10: SQL Set Operators (bảng và sơ đồ)

![Ảnh gốc, slide 10](<assets/m6-subqueries-sets-views/slide-10-image-01.jpg>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

SQL Set Operators

| Operator | Meaning |
| --- | --- |
| UNION | The result is all the row values in one or both tables |
| INTERSECT | The result is all the row values common to both tables |
| EXCEPT | The result is all the row values in the first table but not the second |

Copyright © 2020 by Pearson Education, Inc.

![Ảnh gốc, slide 10](<assets/m6-subqueries-sets-views/slide-09-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
(a) A Set
(b) A Subset
The Union is the entire
area of both sets
B
(c) The Union of Two Sets
The Intersection is the
middle area common
to both sets
A
B
(d) The Intersection of Two Sets
The Complement is
the area in A that is not
in B
(e) The Complement of Two Sets
Copyright © 2020 by Pearson Education, Inc.
```

### Ghi chú của slide

Long Description:
The table has three rows and two columns. The column headings are Operator and Meaning. The table data are as follows:
Operator, UNION. Meaning, The result is all the row values in one or both tables.
Operator, INTERSECT. Meaning, The result is all the row values common to both tables.
Operator, EXCEPT. Meaning, The result is all the row values in the first table but not the second.

<a id="slide-11"></a>

## Slide 11: Creating and Working with SQL Views

An SQL view is a virtual table that is constructed from other tables or views.

A view has no data of its own but uses data stored in tables or other views.

Views are created using SQL SELECT statements and then used in other SELECT statements as just another table.

The only limitation on the SQL statements that create the views is that they cannot contain ORDER BY clauses.

If the results of a query using a view need to be sorted, the sort order must be provided by the SELECT statement that processes the view.

<a id="slide-12"></a>

## Slide 12: Creating and Working with SQL Views

![Ảnh gốc, slide 12](<assets/m6-subqueries-sets-views/slide-12-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Application
Web Application
SQL View
SQL View
SQL View
SQL View
Database Table
Database Table
Database Table
Database Table
Copyright © 2020 by Pearson Education, Inc.
Database Table
```

<a id="slide-13"></a>

## Slide 13: Minh họa viewCustomerContacts (ảnh)

![Ảnh gốc, slide 13](<assets/m6-subqueries-sets-views/slide-13-image-01.png>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

The Wallingford Motors CRM Customer Contacts List

**viewCustomerContacts**

| ContactID | LastName | FirstName | ContactDate | ContactType | Remarks |
| --- | --- | --- | --- | --- | --- |
| 1 | Griffey | Ben | 7/7/2018 | Phone | General interest in a Gaia. |
| 2 | Griffey | Ben | 7/7/2018 | Email | Sent general information. |
| 3 | Griffey | Ben | 7/12/2018 | Phone | Set up an appointment. |
| 4 | Griffey | Ben | 7/14/2018 | Meeting | Bought a HiStandard. |
| 5 | Christman | Jessica | 7/19/2018 | Phone | Interested in a SUHi, set up an appointment. |
| 6 | Griffey | Ben | 7/21/2018 | Email | Sent a standard follow-up message. |
| 7 | Christman | Rob | 7/27/2018 | Phone | Interested in a HiStandard, set up an appointment. |
| 8 | Christman | Jessica | 7/27/2018 | Meeting | Bought a SUHi. |
| 9 | Christman | Rob | 8/2/2018 | Meeting | Talked up to a HiLuxury. Customer bought one. |
| 10 | Christman | Jessica | 8/3/2018 | Email | Sent a standard follow-up message. |
| 11 | Christman | Rob | 8/10/2018 | Email | Sent a standard follow-up message. |
| 12 | Hayes | Judy | 8/15/2018 | Phone | General interest in a Gaia. |

**Thiết kế view trong Access (đọc từ ảnh):**

- Bảng `CONTACT`: `ContactID`, `CustomerID`, `ContactDate`, `ContactType`, `Remarks`.
- Bảng `CUSTOMER`: `CustomerID`, `LastName`, `FirstName`, `Address`, `City`, `State`, `ZIP`, `EmailAddress`, `NickName`, `ReferredBy`.
- Quan hệ nhiều-một giữa `CONTACT.CustomerID` và `CUSTOMER.CustomerID`.
- View lấy `ContactID`, `ContactDate`, `ContactType`, `Remarks` từ `CONTACT`; lấy `LastName`, `FirstName` từ `CUSTOMER`; sắp xếp `ContactID` tăng dần.

**CustomerID của các bản ghi CONTACT:**

| ContactID | CustomerID |
| --- | --- |
| 1 | 1 |
| 2 | 1 |
| 3 | 1 |
| 4 | 1 |
| 5 | 3 |
| 6 | 1 |
| 7 | 4 |
| 8 | 3 |
| 9 | 4 |
| 10 | 3 |
| 11 | 4 |
| 12 | 5 |

**CUSTOMER:**

| CustomerID | LastName | FirstName | Address | City | State | ZIP | EmailAddress | NickName | ReferredBy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Griffey | Ben | 5678 25th NE | Seattle | WA | 98178 | Ben.Griffey@somewhere.com | Big Bill | |
| 3 | Christman | Jessica | 3456 36th SW | Seattle | WA | 98189 | Jessica.Christman@somewhere.com | Billy | |
| 4 | Christman | Rob | 4567 47th NW | Seattle | WA | 98167 | Rob.Christman@somewhere.com | Tina | 3 |
| 5 | Hayes | Judy | 234 Highland Place | Edmonds | WA | 98210 | Judy.Hayes@somewhere.com | Tina | 1 |

Ảnh minh họa dùng Edge, Access 2019, Windows 10, Microsoft Corporation.

<a id="slide-14"></a>

## Slide 14: Creating SQL Views

The SQL CREATE VIEW statement is used to create view structures.  The syntax of this statement is:

```sql
CREATE VIEW	  {ViewName} AS
       {SQL SELECT statement};
```

The view below (EmployeePhoneView) is based on the EMPLOYEE table in the WP database.

```sql
CREATE VIEW EmployeePhoneView AS
      SELECT    FirstName, LastName, OfficePhone AS EmployeePhone
      FROM       EMPLOYEE;
```

<a id="slide-15"></a>

## Slide 15: Some Uses of SQL Views

![Ảnh gốc, slide 15](<assets/m6-subqueries-sets-views/slide-15-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Uses of SQL Views
Hide columns or rows.
Display results of computations.
Hide complicated SQL syntax.
Layer built-in functions.
Copyright © 2020 by Pearson Education, Inc.
```

```sql
CREATE VIEW BasicDepartmentDataView AS
	SELECT DepartmentName, DepartmentPhone
	FROM DEPARTMENT;
```

![Ảnh gốc, slide 15](<assets/m6-subqueries-sets-views/slide-15-image-02.png>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

DDL for wp.DEPARTMENT

```sql
CREATE TABLE `DEPARTMENT` (
  `DepartmentName` char(35) NOT NULL,
  `BudgetCode` char(30) NOT NULL,
  `OfficeNumber` char(15) NOT NULL,
  `DepartmentPhone` char(12) NOT NULL,
  PRIMARY KEY (`DepartmentName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

<a id="slide-16"></a>

## Slide 16: Some Uses of SQL Views

![Ảnh gốc, slide 16](<assets/m6-subqueries-sets-views/slide-15-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Uses of SQL Views
Hide columns or rows.
Display results of computations.
Hide complicated SQL syntax.
Layer built-in functions.
Copyright © 2020 by Pearson Education, Inc.
```

```sql
CREATE VIEW ProjectHoursToDateView AS
	SELECT PROJECT.ProjectID, ProjectName, MaxHours AS ProjectMaxHours,
	SUM(HoursWorked) AS ProjectHoursWorkedToDate
	FROM PROJECT JOIN ASSIGNMENT
	ON PROJECT.ProjectID = ASSIGNMENT.ProjectID
	GROUP BY PROJECT.ProjectID;
```

```sql
CREATE VIEW EmployeeProjectHoursWorkedView AS
SELECT ProjectName, FirstName, LastName, HoursWorked
FROM EMPLOYEE AS E JOIN ASSIGNMENT AS A
	ON E.EmployeeNumber = A.EmployeeNumber
	JOIN PROJECT AS P
	ON A.ProjectID = P.ProjectID
	ORDER BY P.ProjectID, A.EmployeeNumber;
```

<a id="slide-17"></a>

## Slide 17: Some Uses of SQL Views

![Ảnh gốc, slide 17](<assets/m6-subqueries-sets-views/slide-15-image-01.jpg>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Uses of SQL Views
Hide columns or rows.
Display results of computations.
Hide complicated SQL syntax.
Layer built-in functions.
Copyright © 2020 by Pearson Education, Inc.
```

```sql
/* create the view */
CREATE VIEW ProjectHoursToDateView AS
	SELECT PROJECT.ProjectID, ProjectName, MaxHours AS ProjectMaxHours,
	SUM(HoursWorked) AS ProjectHoursWorkedToDate
	FROM PROJECT JOIN ASSIGNMENT
	ON PROJECT.ProjectID = ASSIGNMENT.ProjectID
	GROUP BY PROJECT.ProjectID;

/* write SQL queries on the created view*/
SELECT ProjectID, ProjectName, ProjectMaxHours, ProjectHoursWorkedToDate
FROM ProjectHoursToDateView
WHERE ProjectHoursWorkedToDate > ProjectMaxHours
ORDER BY ProjectID;

/*layering can be continued*/
CREATE VIEW ProjectsOverAllocatedMaxHoursView AS
	SELECT ProjectID, ProjectName, ProjectMaxHours, ProjectHoursWorkedToDate
	FROM ProjectHoursToDateView
	WHERE ProjectHoursWorkedToDate > ProjectMaxHours;

/* perform further calculation*/
SELECT ProjectID, ProjectName, ProjectMaxHours, ProjectHoursWorkedToDate,
	(ProjectHoursWorkedToDate - ProjectMaxHours) AS HoursOverMaxAllocated
	FROM ProjectsOverAllocatedMaxHoursView
	ORDER BY ProjectID;
```

<a id="slide-18"></a>

## Slide 18: QnA!

![Ảnh gốc, slide 18](<assets/m6-subqueries-sets-views/slide-18-image-01.png>)
