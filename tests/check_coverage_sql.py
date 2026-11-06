"""Independent CTE expectations for join/grain/measure/filter gaps; no DB writes."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from bank_sql8 import SQL8
from semantic_checks import canonical, execute, fixture


def check(number, definitions, expected):
    entry = SQL8[number - 1]
    expected = [tuple(canonical(value) if value is not None else None for value in row) for row in expected]
    for field in ('sql', 'alt'):
        actual = execute(entry[field], definitions)
        assert Counter(actual) == Counter(expected), (entry['id'], field, actual, expected)
    print('PASS', entry['id'])


employees = fixture('employees', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'),
                                 ('Last Name', 'CHAR(20)')], [
    (1, 'Same', 'Name'), (2, 'Same', 'Name'), (3, 'No', 'Orders')])
customers = fixture('customers', [('ID', 'SIGNED'), ('Company', 'CHAR(20)'), ('City', 'CHAR(20)')], [
    (1, 'Same', 'A'), (2, 'Same', 'A'), (3, 'Other', 'B'), (4, 'Unknown', None), (5, 'Unused', 'A')])
shippers = fixture('shippers', [('ID', 'SIGNED'), ('Company', 'CHAR(20)')], [(1, 'Same'), (2, 'Same')])
products = fixture('products', [('ID', 'SIGNED'), ('Category', 'CHAR(20)')], [
    (1, 'A'), (2, 'A'), (3, 'B'), (4, None), (5, 'C')])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Employee ID', 'SIGNED'),
                           ('Customer ID', 'SIGNED'), ('Shipper ID', 'SIGNED'),
                           ('Ship City', 'CHAR(20)'), ('Order Date', 'DATETIME')], [
    (1, 1, 1, 1, 'X', '2006-01-01'), (2, 1, 1, 1, 'X', '2006-12-31 23:59:59'),
    (3, 1, 2, 1, 'X', '2006-06-01'), (4, 1, 3, 1, 'Y', '2007-01-01'),
    (5, 2, 1, 2, 'X', '2006-01-01'), (6, 2, 2, 2, 'Z', '2006-01-01'),
    (7, 1, 4, 1, 'X', '2006-01-01'), (8, 1, 2, 1, None, '2006-01-01'),
    (9, 1, 2, 1, 'X', '2005-12-31 23:59:59'), (10, 1, 3, 1, None, None),
    (11, 1, 1, 1, 'X', '2006-01-01'), (12, 1, 404, 1, 'X', '2006-01-01')])
details = fixture('order details', [('ID', 'SIGNED'), ('Order ID', 'SIGNED'), ('Product ID', 'SIGNED'),
                                   ('Quantity', 'SIGNED'), ('Unit Price', 'DECIMAL(10,2)'),
                                   ('Discount', 'DECIMAL(10,2)')], [
    (1, 1, 1, 1, 10, 0), (2, 1, 1, 2, 10, 0), (3, 1, 2, 1, 20, '0.5'),
    (4, 2, 1, 1, 10, None), (5, 3, 1, 2, 10, 0), (6, 3, 2, 1, 20, 0),
    (7, 4, 3, 3, 10, 0), (8, 5, 1, 1, 10, 0), (9, 6, 3, 1, 10, 0),
    (10, 7, 2, 1, 20, 0), (11, 9, 3, 1, 10, 0), (12, 11, 4, 1, 5, 0),
    (13, 3, 404, 1, 7, 0), (14, 12, 1, 1, 10, 0), (15, 6, 1, 1, 10, 0)])
sales = [employees, customers, shippers, products, orders, details]
check(1, sales, [(1, 'Same', 'Name', 'A', 6), (1, 'Same', 'Name', 'B', 2), (2, 'Same', 'Name', 'A', 2)])
check(2, sales, [(1, 'Same', 'Name', 'X', 3)])
shipping_orders = fixture('orders', [('Order ID', 'SIGNED'), ('Employee ID', 'SIGNED'),
    ('Customer ID', 'SIGNED'), ('Ship City', 'CHAR(20)')], [
    (1, 1, 1, 'X'), (2, 1, 2, 'X'), (3, 1, 1, 'X'), (4, 1, 1, 'Y'),
    (5, 1, 1, None), (6, 1, 2, None)])
check(2, [employees, customers, shipping_orders], [(1, 'Same', 'Name', 'X', 2)])
check(3, sales, [(1, 'Same', 'Name', 'A', 3), (2, 'Same', 'Name', 'A', 2)])
check(4, sales, [(1, 'Same', 'A', 2), (2, 'Same', 'A', 2)])
check(5, sales, [(1, 'Same', 'A', 2), (2, 'Same', 'A', 2)])
check(9, sales, [(1, 'Same', 'Name', 1, 'Same', 3, 55),
                 (1, 'Same', 'Name', 2, 'Same', 3, 57),
                 (1, 'Same', 'Name', 3, 'Other', 2, 30),
                 (1, 'Same', 'Name', 4, 'Unknown', 1, 20),
                 (2, 'Same', 'Name', 1, 'Same', 1, 10),
                 (2, 'Same', 'Name', 2, 'Same', 1, 20)])

suppliers = fixture('suppliers', [('ID', 'SIGNED'), ('Company', 'CHAR(20)')], [
    (1, 'Same'), (2, 'Same'), (3, 'Unused')])
purchase_orders = fixture('purchase orders', [('Purchase Order ID', 'SIGNED'), ('Supplier ID', 'SIGNED'),
    ('Created By', 'SIGNED'), ('Approved By', 'SIGNED'), ('Shipping Fee', 'DECIMAL(10,2)')], [
    (1, 1, 1, 2, 5), (2, 1, 1, 2, 5), (3, 1, 2, 1, None),
    (4, 2, 1, 2, 7), (5, 2, 1, 2, 7), (6, 2, 2, 2, 3)])
purchase_details = fixture('purchase order details', [('ID', 'SIGNED'), ('Purchase Order ID', 'SIGNED'),
    ('Product ID', 'SIGNED'), ('Quantity', 'SIGNED'), ('Unit Cost', 'DECIMAL(10,2)')], [
    (1, 1, 1, 2, 3), (2, 1, 1, 1, 3), (3, 1, 2, 1, 4),
    (4, 2, 1, 1, 3), (5, 2, 3, 2, 5), (6, 4, 1, 3, 2), (7, 4, 2, 2, 4),
    (8, 6, 4, 1, 9), (9, 6, 404, 1, 8)])
purchases = [employees, suppliers, products, purchase_orders, purchase_details]
check(6, purchases, [(1, 'Same', 'A', 2), (2, 'Same', 'A', 2)])
check(7, purchases, [(1, 'Same', 'Name', 1, 'Same', 2), (1, 'Same', 'Name', 2, 'Same', 2)])
check(8, purchases, [(1, 'Same', 3, 10, 26), (2, 'Same', 3, 17, 31), (3, 'Unused', 0, 0, 0)])

privileges = fixture('privileges', [('Privilege ID', 'SIGNED')], [(1,), (2,), (3,)])
assignments = fixture('employee privileges', [('Employee ID', 'SIGNED'), ('Privilege ID', 'SIGNED')], [
    (1, 1), (1, 1), (1, 2), (1, 404), (2, None), (2, 404)])
check(10, [employees, privileges, assignments], [
    (1, 'Same', 'Name', 2), (2, 'Same', 'Name', 0), (3, 'No', 'Orders', 0)])

statuses = fixture('order details status', [('Status ID', 'SIGNED'), ('Status Name', 'CHAR(20)')], [
    (1, 'Same'), (2, 'Same'), (3, 'Unused')])
status_details = fixture('order details', [('ID', 'SIGNED'), ('Order ID', 'SIGNED'), ('Status ID', 'SIGNED')], [
    (1, 1, 1), (2, 1, 1), (3, 2, 1), (4, None, 1), (5, 3, 2), (6, 4, 404), (7, 1, None)])
check(11, [statuses, status_details], [(1, 'Same', 4, 2), (2, 'Same', 1, 1), (3, 'Unused', 0, 0)])

types = fixture('inventory transaction types', [('ID', 'SIGNED'), ('Type Name', 'CHAR(20)')], [
    (9, 'Purchased'), (2, 'Sold'), (3, 'On Hold'), (4, 'Waste'), (5, 'Unused')])
movements = fixture('inventory transactions', [('Transaction Type', 'SIGNED'), ('Product ID', 'SIGNED'),
    ('Quantity', 'SIGNED'), ('Transaction Created Date', 'DATETIME'), ('Transaction Modified Date', 'DATETIME')], [
    (9, 1, 2, '2006-01-01', '2007-01-01'), (9, 1, 3, '2006-12-31 23:59:59', '2007-01-01'),
    (9, 2, 4, '2006-06-01', None), (2, 1, 1, '2006-06-01', None),
    (2, 1, 2, '2006-06-01', None), (2, 3, 4, '2006-06-01', None),
    (3, 1, 5, '2006-06-01', None), (4, 2, 6, '2006-06-01', None),
    (9, 3, 100, '2005-12-31 23:59:59', '2006-01-01'), (9, 3, 100, '2007-01-01', None),
    (9, 3, 100, None, '2006-01-01'), (9, 4, 100, '2006-01-01', None),
    (9, 404, 100, '2006-01-01', None), (404, 1, 100, '2006-01-01', None)])
check(12, [types, movements, products], [(9, 'Purchased', 'A', 2, 9),
    (2, 'Sold', 'A', 1, 3), (2, 'Sold', 'B', 1, 4),
    (3, 'On Hold', 'A', 1, 5), (4, 'Waste', 'A', 1, 6)])

empty_products = fixture('products', [('ID', 'SIGNED'), ('Category', 'CHAR(20)')], [])
check(4, [customers, orders, details, empty_products], [])
empty_purchase_orders = fixture('purchase orders', [('Purchase Order ID', 'SIGNED'), ('Supplier ID', 'SIGNED'),
    ('Created By', 'SIGNED'), ('Approved By', 'SIGNED'), ('Shipping Fee', 'DECIMAL(10,2)')], [])
check(8, [suppliers, empty_purchase_orders, purchase_details], [
    (1, 'Same', 0, 0, 0), (2, 'Same', 0, 0, 0), (3, 'Unused', 0, 0, 0)])
