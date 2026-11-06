"""Adversarial, connection-local CTE fixtures; leaves the Northwind dump untouched."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bank_sql3 import SQL3

ENTRIES = {entry['id']: entry for entry in SQL3}


def literal(value):
    if value is None:
        return 'NULL'
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return str(value)


def fixture(name, columns, rows):
    members = []
    for values in rows or [[None] * len(columns)]:
        fields = []
        for (column, datatype), value in zip(columns, values):
            fields.append('CAST(%s AS %s) AS `%s`' % (literal(value), datatype, column))
        members.append('SELECT ' + ','.join(fields) + (' WHERE FALSE' if not rows else ''))
    return '`' + name + '` AS (' + ' UNION ALL '.join(members) + ')'


def canonical(value):
    if value == 'NULL':
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return str(value)


def execute(query, definitions=()):
    if definitions:
        prefix = 'WITH ' + ','.join(definitions) + ','
        query = prefix + query[5:] if query.startswith('WITH ') else prefix[:-1] + ' ' + query
    completed = subprocess.run([os.environ.get('MYSQL_BIN','mysql'),'-uroot',
        '-S'+os.environ['MYSQL_SOCK'],'-N','-B','--default-character-set=utf8mb4','northwind'],
        input=query,text=True,capture_output=True)
    if completed.returncode:
        raise AssertionError(completed.stderr)
    return [tuple(canonical(value) for value in row.split('\t')) for row in completed.stdout.splitlines()]


def check(entry_id, label, definitions, expected):
    expected = [tuple(None if value is None else canonical(value) for value in row) for row in expected]
    entry = ENTRIES[entry_id]
    for field in ('sql','alt'):
        actual = execute(entry[field],definitions)
        assert Counter(actual) == Counter(expected), (entry_id,label,field,actual,expected)
    print('PASS',entry_id,label)


def main():
    product_columns = [('ID','SIGNED'),('Category','CHAR(30)'),('Standard Cost','DECIMAL(30,11)'),('List Price','DECIMAL(30,11)')]
    products = fixture('products',product_columns,[(1,'Alpha',None,None),(2,'Alpha',5,10),(3,'Alpha',5,10),(4,'Alpha',6,11),(5,'Alpha',7,11.01),(6,'Beta',3,2)])
    check('SQL3-030','NULL costs do not count; duplicate cheaper products do',[products],[(4,6),(5,7)])
    check('SQL3-031','second distinct cost retains its entire rank',[products],[(4,'Alpha',6)])
    check('SQL3-032','fixed row count drops extra tied prices',[products],[(2,'Alpha',10),(3,'Alpha',10),(6,'Beta',2)])
    check('SQL3-027','inclusive ten-percent threshold; category-local JSON expansion',[products],[(2,3,10,10),(2,4,10,11),(3,4,10,11),(4,5,11,11.01)])
    check('SQL3-011','all tied category maxima',[fixture('products',product_columns,[(1,'Alpha',1,1),(2,'Alpha',1,1),(3,'Beta',1,1),(4,'Beta',1,1),(5,'Gamma',1,1)])],[('Alpha',2),('Beta',2)])
    absent = fixture('products',product_columns,[(1,'Alpha',None,1),(2,'Alpha',5,2)])
    check('SQL3-055','empty ALL includes a NULL left operand',[absent],[(1,None),(2,5)])
    check('SQL3-056','empty ANY is false',[absent],[])
    nonempty = fixture('products',product_columns,[(1,'Seafood',None,1),(2,'Seafood',5,2),(3,'Alpha',6,3)])
    check('SQL3-055','nonempty ALL ignores only explicitly excluded reference NULLs',[nonempty],[(3,6)])
    check('SQL3-056','nonempty ANY needs a true comparison',[nonempty],[(3,6)])
    customers = fixture('customers',[('ID','SIGNED'),('Company','CHAR(30)')],[(1,'One'),(2,'Two'),(3,'Three')])
    orders = fixture('orders',[('Order ID','SIGNED'),('Customer ID','SIGNED')],[(10,1),(20,2)])
    check('SQL3-051','empty reference set qualifies inactive customers',[customers,orders,fixture('order details',[('Order ID','SIGNED'),('Product ID','SIGNED')],[])],[(1,'One'),(2,'Two'),(3,'Three')])
    check('SQL3-051','coverage requires every reference product',[customers,orders,fixture('order details',[('Order ID','SIGNED'),('Product ID','SIGNED')],[(10,1),(10,2),(20,1)])],[(1,'One')])
    check('SQL3-060','nonempty requirement and NULL counterexample',[fixture('orders',[('Order ID','SIGNED')],[(1,),(2,),(3,),(4,)]),fixture('order details',[('Order ID','SIGNED'),('Discount','DECIMAL(10,4)')],[(2,0),(3,0),(3,None),(4,.1)])],[(2,)])
    check('SQL3-078','empty aggregate outputs one row of zeros',[fixture('invoices',[('Due Date','DATETIME')],[])],[(0,0,0)])
    check('SQL3-099','equal-valued lines must not disappear; two-child fanout',[fixture('orders',[('Order ID','SIGNED')],[(1,),(2,)]),fixture('order details',[('Order ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Price','DECIMAL(20,4)')],[(1,1,10),(1,1,10),(1,1,5)]),fixture('invoices',[('Order ID','SIGNED')],[(1,),(1,)])],[(1,3,2,25),(2,0,0,0)])
    check('SQL3-046','domain extraction policy and missing values',[fixture('customers',[('E-mail Address','CHAR(100)')],[('X@EXAMPLE.COM',),(' x@Example.com ',),(None,),('@x',),('x@  ',),('bad@@foo',)])],[('example.com',2),('foo',1)])
    check('SQL3-098','employee with a quarter order but no detail must get zero',[fixture('employees',[('ID','SIGNED')],[(1,),(2,),(3,)]),fixture('orders',[('Order ID','SIGNED'),('Employee ID','SIGNED'),('Order Date','DATETIME')],[(10,2,'2006-03-01'),(20,3,'2006-04-01')]),fixture('order details',[('Order ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Price','DECIMAL(20,4)'),('Discount','DECIMAL(10,4)')],[(20,1,10,0)])],[(1,0,0,0),(2,0,0,0),(3,0,10,10)])
    check('SQL3-016','unknown inventory quantities follow the stated zero-display policy',[fixture('products',[('ID','SIGNED')],[(1,),(2,)]),fixture('inventory transaction types',[('ID','SIGNED'),('Type Name','CHAR(30)')],[(1,'Sold')]),fixture('inventory transactions',[('Product ID','SIGNED'),('Transaction Type','SIGNED'),('Quantity','DECIMAL(20,4)')],[(1,1,None)])],[(1,0,0,0),(2,0,0,0)])
    lines = fixture('order details',[('Order ID','SIGNED'),('Product ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Price','DECIMAL(20,4)'),('Discount','DECIMAL(10,4)')],[(1,1,1,10,.1),(1,1,1,100,None),(2,2,1,10,None)])
    check('SQL3-020','unknown discounts must not dilute a known weighted rate',[fixture('products',[('ID','SIGNED'),('Category','CHAR(30)')],[(1,'Alpha'),(2,'Beta')]),lines],[('Alpha',.1)])
    purchase = fixture('purchase orders',[('Purchase Order ID','SIGNED'),('Supplier ID','SIGNED')],[(1,1)])
    check('SQL3-064','all-unknown received quantities display zero',[fixture('suppliers',[('ID','SIGNED')],[(1,),(2,)]),purchase,fixture('purchase order details',[('Purchase Order ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Date Received','DATETIME')],[(1,None,'2006-03-01')])],[(1,0,0),(2,0,0)])
    check('SQL3-069','unknown costs must not dilute weighted purchase cost',[purchase,fixture('purchase order details',[('Purchase Order ID','SIGNED'),('Product ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Cost','DECIMAL(20,4)')],[(1,3,1,10),(1,3,100,None)])],[(1,3,10)])
    unknown_sales = [fixture('orders',[('Order ID','SIGNED'),('Employee ID','SIGNED'),('Customer ID','SIGNED')],[(1,1,1),(2,1,2),(3,2,3)]),fixture('order details',[('Order ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Price','DECIMAL(20,4)'),('Discount','DECIMAL(10,4)')],[(1,1,None,0),(2,1,10,0),(3,1,None,0)])]
    check('SQL3-092','an all-unknown employee revenue group has no winner',unknown_sales,[(1,2,10)])
    check('SQL3-093','unknown product total sorts last but does not erase prior cumulative value',[fixture('products',[('ID','SIGNED'),('Category','CHAR(30)')],[(1,'Alpha'),(2,'Alpha'),(3,'Alpha')]),fixture('order details',[('Product ID','SIGNED'),('Quantity','DECIMAL(20,4)'),('Unit Price','DECIMAL(20,4)'),('Discount','DECIMAL(10,4)')],[(1,1,10,0),(2,1,None,0),(3,1,5,0)])],[('Alpha',1,10,10),('Alpha',3,5,15),('Alpha',2,None,15)])
    assert execute('SELECT 1 NOT IN (1,NULL),2 NOT IN (1,NULL),NULL>ALL(SELECT ID FROM products WHERE FALSE),NULL>ANY(SELECT ID FROM products WHERE FALSE);') == [(Decimal(0),None,Decimal(1),Decimal(0))]
    assert execute("SELECT YEARWEEK('2021-01-01',3),DATE_FORMAT('2021-01-01','%x-%v');") == [(Decimal(202053),'2020-53')]
    assert execute("SELECT _utf8mb4'x' COLLATE utf8mb4_general_ci = _utf8mb4'x ' COLLATE utf8mb4_general_ci,_utf8mb4'x' COLLATE utf8mb4_0900_ai_ci = _utf8mb4'x ' COLLATE utf8mb4_0900_ai_ci;") == [(Decimal(1),Decimal(0))]
    assert execute("SELECT parsed.value FROM JSON_TABLE('[null]','$[*]' COLUMNS(value INT PATH '$' NULL ON EMPTY NULL ON ERROR)) parsed;") == [(None,)]
    print('PASS theory truth tables, ISO year boundary, collation padding, JSON null')


if __name__ == '__main__':
    main()
