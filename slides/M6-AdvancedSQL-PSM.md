# M6-AdvancedSQL-PSM

- Nguồn: [M6-AdvancedSQL-PSM.pptx](M6-AdvancedSQL-PSM.pptx)

- Số slide: 23.

- Chủ đề: SQL/PSM, user-defined functions, DELIMITER, triggers, CHECK, stored procedures, bài tập và ví dụ MySQL.

> Bản trích xuất giữ nguyên ngôn ngữ và nội dung nguồn, không sửa kiến thức hoặc cú pháp SQL. Ví dụ có thể chứa lỗi gốc, dấu nháy cong, cú pháp riêng của DBMS hoặc câu lệnh cố ý dùng để thử lỗi; không mặc định coi mọi đoạn SQL là chạy được. Phần OCR được đánh dấu riêng; đối chiếu ảnh gốc khi cần độ chính xác.

## Mục lục

- [Slide 01: Databases and Database Systems](#slide-01)
- [Slide 02: LEARNING OBJECTIVES (1)](#slide-02)
- [Slide 03: LEARNING OBJECTIVES (2)](#slide-03)
- [Slide 04: SQL/ Persistent Stored Module (SQL/PSM)](#slide-04)
- [Slide 05: SQL/ Persistent Stored Module (SQL/PSM)](#slide-05)
- [Slide 06: User-defined functions (stored functions)](#slide-06)
- [Slide 07: User-defined functions – Example 1](#slide-07)
- [Slide 08: User-defined functions – Example 1](#slide-08)
- [Slide 09: User-defined functions – Example 1](#slide-09)
- [Slide 10: User-defined functions – A General Formula](#slide-10)
- [Slide 11: User-defined functions – More examples](#slide-11)
- [Slide 12: Triggers](#slide-12)
- [Slide 13: Triggers](#slide-13)
- [Slide 14: Triggers - Example](#slide-14)
- [Slide 15: Triggers - Example](#slide-15)
- [Slide 16: Triggers - Example](#slide-16)
- [Slide 17: Triggers - Example](#slide-17)
- [Slide 18: Stored Procedures](#slide-18)
- [Slide 19: Stored Procedures](#slide-19)
- [Slide 20: Stored Procedures – Example](#slide-20)
- [Slide 21: Stored Procedures – Example](#slide-21)
- [Slide 22: Stored Procedures – Example](#slide-22)
- [Slide 23: QnA!](#slide-23)

<a id="slide-01"></a>

## Slide 01: Databases and Database Systems

Le Duy Dung (Andrew)

![Ảnh gốc, slide 01](<assets/m6-psm/slide-01-image-01.png>)

<a id="slide-02"></a>

## Slide 02: LEARNING OBJECTIVES (1)

To understand reasons for using the SQL ALTER  statement

To use the SQL ALTER statement

To understand the need for the SQL MERGE statement

To use the SQL MERGE statement

To understand the need for additional types of SQL queries

To use SQL outer join queries

To use SQL correlated subqueries

To use SQL queries on recursive relationships

<a id="slide-03"></a>

## Slide 03: LEARNING OBJECTIVES (2)

To understand the reasons for using SQL set operators

To use SQL set operators

To understand the reasons for using SQL views

To use SQL statements to create and use SQL views

To understand SQL/Persistent Stored Modules (SQL/PSM)

To use SQL statements to create and use SQL user-defined functions

<a id="slide-04"></a>

## Slide 04: SQL/ Persistent Stored Module (SQL/PSM)

The SQL/ Persistent Stored Module is a feature which provides users the ability to add their own extensions to the standard SQL.

With SQL/PSM, users can write procedural code and functions

It allows control-of-flow language such as BEGIN .. END blocks, IF…THEN…ELSE logic structures and LOOPs, as well as the ability to provide usable output to users.

### Ghi chú của slide

which provides users the ability to add their own extensions to the standard SQL

<a id="slide-05"></a>

## Slide 05: SQL/ Persistent Stored Module (SQL/PSM)

But most importantly, SQL/PSM allows the code that implements these features in a database to be contained in that databases

Persistent = Remain available overtime

Stored = Stored for reuse in the database

Module = Written as a self-contained block of code, and there are three main module types:

User-defined function (1)

Triggers (2)

Stored procedures (3)

<a id="slide-06"></a>

## Slide 06: User-defined functions (stored functions)

The User-defined function is a stored-set of SQL statements that:

Is called by name from another SQL statement

May have input parameters passed to it by the calling SQL statement

Returns an output value to the SQL statement that called the function.

Basically, they are similar to built-in functions like MIN(), MAX(), COUNT(), etc… except that, we can create them ourselves to perform specific task we need to do.

![Ảnh gốc, slide 06](<assets/m6-psm/slide-06-image-01.png>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

User-Defined Functions Logical Process Flow

| Step | Description |
| --- | --- |
| INPUT | Parameter values from calling SQL statement |
| PROCESS | Parameter values to create result value |
| OUTPUT | Result value to calling SQL statement |

<a id="slide-07"></a>

## Slide 07: User-defined functions – Example 1

Example: One of the common task you have to do is concatenate FirstName and LastName of demographics data.

```sql
SELECT
CONCAT(RTRIM(LastName),', ',RTRIM(FirstName))
   AS EmployeeName,
EmailAddress, Phone
FROM qacs.EMPLOYEE
ORDER BY EmployeeName;
```

<a id="slide-08"></a>

## Slide 08: User-defined functions – Example 1

Example: Instead of writing that chunk of code every time you need to concatenate First and Last Name, you can define a simpler and reusable function.

```sql
DELIMITER //

CREATE FUNCTION NameConcatenation
(
	FirstName CHAR(25),
	LastName CHAR(25)
)
RETURNS VARCHAR(60) DETERMINISTIC

BEGIN
	DECLARE FullName VARCHAR(60);
	SET FullName = CONCAT(LastName,',', FirstName);
    	RETURN FullName;
END
//
DELIMITER ;
```

- The default delimiter is ;

- By running DELIMITER // , we signify that in this chunk of code, our delimiter is // not ;

- As such, MySQL will know that we passing this whole chunk of code as a module.

- If we didn’t re-define our delimiter, MySQL will interpret the 3 statement within BEGIN…END individually, thus raising an error since standing alone, each of these statement is not a complete instruction to MySQL

- After defining the procedure, we use the delimiter // to signify that this is the end of our module, and reset the DELIMITER to ;

** Note: You can use other symbols for delimiter as well, $$, %% are examples of valid options

<a id="slide-09"></a>

## Slide 09: User-defined functions – Example 1

If set up correctly, you can see your function in the qacs database, under the Functions tab.

Now you can use this whenever you need without recreating the code

You can also test your defined function:

```sql
SELECT
NameConcatenation(FirstName, LastName)
  AS EmployeeName,
EmailAddress, Phone
FROM qacs.EMPLOYEE
ORDER BY EmployeeName;
```

![Ảnh gốc, slide 09](<assets/m6-psm/slide-09-image-01.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
SCHEMAS
Q Filter objects
Northwind
qacs
Tables
› • CUSTOMER
ITEM
SALE
SALE_ITEM
VENDOR
> E Views
T Stored Procedures
v Ea Functions
f() NameConcatenation
sys
world
```

<a id="slide-10"></a>

## Slide 10: User-defined functions – A General Formula

Generally, a user– defined function has this form

```sql
DELIMITER $$ --Set the delimiter to other values so that ; can be used within the function
CREATE FUNCTION() -- Define the function name and its input
RETURNS -- Define the data type of output
BEGIN -- Begin the definition of your procedures
RETURN -- Define the output of your function
END $$ -- Signify that the function ends here
DELIMITER ; -- Reset the delimiter so that ; can be used as per usual
```

<a id="slide-11"></a>

## Slide 11: User-defined functions – More examples

Practice questions: Write a function that

Capitalizes all the vowels in a column

Convert the date from ‘yyyy-mm-dd’ to ‘dd/mm/yyyy’ format

<a id="slide-12"></a>

## Slide 12: Triggers

Triggers is a stored program that is executed by the DBMS whenever a specified event occurs.

A trigger is attached to a table or a view. A table or a view may have many triggers, but a trigger is associated with just one table or view. A trigger is invoked by an SQL DML INSERT, UPDATE, or DELETE request on the table or view to which it is attached

BEFORE triggers are executed before the DBMS processes the insert, update, or delete request.

AFTER triggers are executed after the insert, update, or delete request has been processed.

![Ảnh gốc, slide 12](<assets/m6-psm/slide-12-image-01.png>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

Summary of SQL Triggers by DBMS Product

| DML Action | BEFORE | INSTEAD OF | AFTER |
| --- | --- | --- | --- |
| INSERT | Oracle Database; MySQL | Oracle Database; SQL Server | Oracle Database; SQL Server; MySQL |
| UPDATE | Oracle Database; MySQL | Oracle Database; SQL Server | Oracle Database; SQL Server; MySQL |
| DELETE | Oracle Database; MySQL | Oracle Database; SQL Server | Oracle Database; SQL Server; MySQL |

<a id="slide-13"></a>

## Slide 13: Triggers

Common use case of triggers included

Providing default values.

Enforcing data constraints.

Updating SQL views.

Performing referential integrity actions.

<a id="slide-14"></a>

## Slide 14: Triggers - Example

Example: Add a column to the EMPLOYEE table named Apprenticeship, which will contain data showing the apprenticeship status for each employee. Refer to the details below to create Apprenticeship column. Then create a trigger to ensure that only the values of Completed, In process, or Not started are allowed as data in the Apprenticeship column

![Ảnh gốc, slide 14](<assets/m6-psm/slide-14-image-01.png>)

**Nội dung trong ảnh (đã đối chiếu ảnh gốc):**

| EmployeeID | Supervisor | Apprenticeship |
| --- | --- | --- |
| 1 | NULL | Completed |
| 2 | 5 | In process |
| 3 | 1 | Not started |
| 4 | 1 | Completed |
| 5 | NULL | In process |

| Column Name | Type | Key | Required | Remarks |
| --- | --- | --- | --- | --- |
| Supervisor | Integer | Foreign Key | No | REF: EmployeeID in EMPLOYEE |
| Apprenticeship | Varchar (20) | No | Yes | CHECK Values: "Completed", "In process", "Not started" |

<a id="slide-15"></a>

## Slide 15: Triggers - Example

Add column apprenticeship into our employee table

```sql
alter table EMPLOYEE
add Apprenticeship varchar(20);
```

Create a trigger which is equivalent to SQL CHECK constraint, ensure that this column contains only these values “Not started”, “Completed”, “In Progress”

With a SQL CHECK we can do this. How about triggers?

```sql
alter table EMPLOYEE
add constraint Required check
(Apprenticeship in ("Completed", "In process", "Not started"));
```

<a id="slide-16"></a>

## Slide 16: Triggers - Example

2. Our trigger can look like this. If set up correctly, you can see the triggers from the table

```sql
delimiter //
CREATE TRIGGER upd_check BEFORE UPDATE ON EMPLOYEE
	FOR EACH ROW
	BEGIN
		IF NEW.Apprenticeship like '%Completed%' THEN
			SET NEW.Apprenticeship = 'Completed';
		ELSEIF NEW.Apprenticeship like '%In process%' THEN
			SET NEW.Apprenticeship = 'In process';
		ELSEIF NEW.Apprenticeship like '%Not started%' THEN
			SET NEW.Apprenticeship = 'Not started';
		END IF;
	END;//
delimiter ;
```

![Ảnh gốc, slide 16](<assets/m6-psm/slide-16-image-01.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
V E
qacs
v [ Tables
› • CUSTOMER
V EMPLOYEE
Columns
1 Indexes
Foreign Keys
Triggers
upd_check
- ITr
```

<a id="slide-17"></a>

## Slide 17: Triggers - Example

3. Run this script to test our trigger, you can see the values are auto-corrected to abide with rules defined in our trigger

```sql
update EMPLOYEE
set Apprenticeship = case EmployeeID
when 1 then "Completed.  "
when 2 then ”4In processasd"
when 3 then "3Not started"
when 4 then "asdCompleted"
when 5 then "In processedd"
end;
```

<a id="slide-18"></a>

## Slide 18: Stored Procedures

Stored Procedures is a program that is stored within the database and compiled when used.

Stored procedures can receive input parameters and return results. Unlike triggers, which are attached to a given table or view, stored procedures are attached to the database. They can be executed by any process using the database that has permission to use the procedure

Stored procedures are used for many purposes. Although database administrators use them to perform common administration tasks, their primary use is within database applications.

![Ảnh gốc, slide 18](<assets/m6-psm/slide-18-image-01.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Trigger
Module of code that is called by the DBMS when INSERT, UPDATE,
or DELETE commands are issued.
Assigned to a table or view.
Depending on the DBMS, may have more than one trigger per table or view.
Triggers may issue INSERT, UPDATE, and DELETE commands and
thereby may cause the invocation of other triggers.
```

![Ảnh gốc, slide 18](<assets/m6-psm/slide-18-image-02.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Stored Procedure
Module of code that is called by a user or database administrator.
Assigned to a database, but not to a table or a view.
Can issue INSERT, UPDATE, DELETE, and MERGE commands.
Used for repetitive administration tasks or as part of an application.
```

<a id="slide-19"></a>

## Slide 19: Stored Procedures

Advantages of stored procedures included:

![Ảnh gốc, slide 19](<assets/m6-psm/slide-19-image-01.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
Advantages of Stored Procedures
Greater security.
Decreased network traffic.
SQL can be optimized.
Code sharing.
Less work.
Standardized processing.
Specialization among developers.
```

<a id="slide-20"></a>

## Slide 20: Stored Procedures – Example

Example: Refer to table SALE, write a stored procedure that outputs the total value of all the sales made by each employee. The stored procedure will take an employee ID as input and return the total value of sales* made by him.

Note: Total value of sales can be interpreted as sum(Total) as in the SALE table

<a id="slide-21"></a>

## Slide 21: Stored Procedures – Example

Start with CREATE PROCEDURE to determine named of the procedure, and its input datatype

```sql
CREATE PROCEDURE SaleReport(IN eid INT)
```

Then define the task you want the procedure to carry out. This definition is contained within the BEGIN…END statement. This usually looks like a normal query. Remember to end the query with ;, before using END to signify the end of the procedure definition

```sql
BEGIN
	select sum(Total) as 'Total Sales made'
	from qacs.SALE
    	where EmployeeID in (eid);
END
```

<a id="slide-22"></a>

## Slide 22: Stored Procedures – Example

If you set up correctly, the stored procedure will appear under qacs database schema like this.

To use the stored procedure, you have to explicit call it. Try the following call to understand its mechanism

```sql
call SaleReport(1);
call SaleReport(0);
call SaleReport(‘1’);
call SaleReport(1,2);
```

5.   Can you adjust the procedure so that it can take a list of EmployeeID as input and return the total value of sales made by all of those employees?

![Ảnh gốc, slide 22](<assets/m6-psm/slide-22-image-01.png>)

**Nội dung trong ảnh (OCR, có thể sai ký tự hoặc thứ tự cột):**

```text
SCHEMAS
Q Filter objects.
Northwind
qacs
> E Tables
> E7 Views
v E Stored Procedures
SaleReport
• A Functions
```

<a id="slide-23"></a>

## Slide 23: QnA!

![Ảnh gốc, slide 23](<assets/m6-psm/slide-23-image-01.png>)
