"""Connection-local CTE fixtures for practice and paraphrased questions."""
from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from bank_sql6 import SQL6
from bank_theory6 import THEORY6
from semantic_checks import canonical, execute, fixture


def check(index, definitions, expected):
    entry = SQL6[index]
    expected = [tuple(canonical(value) if value is not None else None for value in row) for row in expected]
    for field in ('sql', 'alt'):
        actual = execute(entry[field], definitions)
        assert Counter(actual) == Counter(expected), (entry['id'], field, actual, expected)
        if entry['cmp'] == 'ordered':
            assert actual == expected, (entry['id'], field, actual, expected)
    print('PASS', entry['id'])


customers = fixture('customers', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'), ('Last Name', 'CHAR(20)')],
                    [(1, 'Alice', 'A'), (2, 'Bob', 'B'), (3, 'Carol', 'C'), (4, 'Dan', 'D'), (5, 'Eve', 'E')])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Customer ID', 'SIGNED'),
                           ('Order Date', 'DATETIME'), ('Shipping Fee', 'DECIMAL(30,11)')], [
    (1, 1, '2006-01-01', 30), (2, 1, '2006-12-31 23:59:59', 30), (3, 1, '2006-06-01', 5),
    (4, 1, '2005-12-31 23:59:59', 999), (5, 2, '2006-01-02', 15), (6, 2, '2006-02-02', 15),
    (7, 2, '2006-03-02', 15), (8, 3, '2006-03-02', 0), (9, 3, '2006-03-02', 0),
    (10, 4, '2006-04-01', 100), (11, 5, '2006-05-01', '15000.01'), (12, 1, '2007-01-01', 999)])
details = fixture('order details', [('Order ID', 'SIGNED'), ('Product ID', 'SIGNED'),
                                   ('Unit Price', 'DECIMAL(30,11)'), ('Quantity', 'DECIMAL(18,4)')], [
    (1, 1, 25, 1), (1, 1, 25, 1), (1, 2, 50, 1), (1, 5, 0, 1),
    (2, 3, 50, 1), (2, 4, 50, 1), (4, 1, 10000, 1), (5, 1, 100, 1),
    (6, 2, 100, 1), (7, 3, 100, 1), (8, 1, 50, 1), (8, 2, 50, 1),
    (9, 3, 50, 1), (9, 4, 50, 1), (10, 1, 0, 1), (11, 1, 100000, 1), (12, 4, 10000, 1)])
products = fixture('products', [('ID', 'SIGNED'), ('Category', 'CHAR(20)')],
                   [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'), (5, None)])
check(0, [customers, orders, details], [(1, 'Alice', 'A', 200, 65, '0.3250'),
                                       (5, 'Eve', 'E', 100000, '15000.01', '0.1500')])
check(3, [customers, orders, details, products], [(1, 'Alice', 'A', 3, 4)])

transactions = fixture('inventory transactions', [('Transaction Type', 'SIGNED'),
                        ('Transaction Created Date', 'DATETIME'), ('Product ID', 'SIGNED'), ('Quantity', 'SIGNED')], [
    (9, '2006-01-01', 10, 60), (9, '2006-01-31 23:59:59', 10, 41),
    (9, '2006-02-01', 10, 100), (9, '2006-03-01', 10, 70), (9, '2006-04-01', 10, 70),
    (9, '2006-01-02', 20, 150), (9, '2005-12-31 23:59:59', 10, 1000),
    (9, '2007-01-01', 10, 1000), (2, '2006-01-01', 10, 1000),
    (9, '2006-12-31 23:59:59', 10, 101), (9, '2006-01-01', 404, 1000)])
types = fixture('inventory transaction types', [('ID', 'SIGNED'), ('Type Name', 'CHAR(20)')],
                [(9, 'Sold'), (2, 'Purchased')])
products = fixture('products', [('ID', 'SIGNED'), ('Product Name', 'CHAR(20)')], [(10, 'Apple'), (20, 'Bread')])
check(1, [transactions, types, products], [('2006-01', 20, 'Bread', 150),
                                          ('2006-01', 10, 'Apple', 101), ('2006-12', 10, 'Apple', 101)])

employees = fixture('employees', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'),
                                  ('Last Name', 'CHAR(20)'), ('City', 'CHAR(20)')],
                    [(1, 'One', 'A', 'X'), (2, 'Two', 'B', 'X'), (3, 'Three', 'C', 'X'),
                     (4, 'Four', 'D', None), (5, 'Five', 'E', 'X'), (6, 'Six', 'F', 'X')])
customers = fixture('customers', [('ID', 'SIGNED'), ('City', 'CHAR(20)')], [(1, 'X'), (2, 'Y'), (3, None)])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Employee ID', 'SIGNED'),
                           ('Customer ID', 'SIGNED'), ('Order Date', 'DATETIME')], [
    (1, 1, 2, '2006-01-01'), (2, 1, 1, '2005-12-31 23:59:59'),
    (3, 2, 1, '2006-12-31 23:59:59'), (4, 2, 2, '2006-06-01'),
    (5, 3, 2, '2005-06-01'), (6, 4, 3, '2006-06-01'), (7, 5, 2, '2007-01-01')])
check(2, [employees, customers, orders], [(1, 'One', 'A'), (4, 'Four', 'D')])

customers = fixture('customers', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'), ('Last Name', 'CHAR(20)')],
                    [(1, 'A', 'One'), (2, 'B', 'Two'), (3, 'C', 'Three'), (4, 'D', 'Four')])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Customer ID', 'SIGNED'), ('Order Date', 'DATETIME')], [
    (1, 1, '2005-12-31 23:59:59'), (2, 1, '2006-01-01'), (3, 1, '2006-12-31 23:59:59'),
    (4, 1, '2007-01-01'), (5, 2, '2006-06-01'), (6, 3, None)])
details = fixture('order details', [('ID', 'SIGNED'), ('Order ID', 'SIGNED'), ('Product ID', 'SIGNED')],
                  [(1, 1, 9), (2, 2, 1), (3, 2, 1), (4, 2, 2), (5, 3, 1), (6, 3, 3), (7, 4, 8)])
check(35, [customers, orders], [
    (1, 'A', 'One', '2005-12-31 23:59:59', '2007-01-01 00:00:00'),
    (2, 'B', 'Two', '2006-06-01 00:00:00', '2006-06-01 00:00:00'),
    (3, 'C', 'Three', None, None), (4, 'D', 'Four', None, None)])
check(36, [customers, orders, details], [(1, 2, 3), (2, 1, 0)])

products = fixture('products', [('ID', 'SIGNED'), ('Product Name', 'CHAR(20)'),
                               ('Category', 'CHAR(20)'), ('List Price', 'DECIMAL(10,2)')], [
    (1, 'Low', 'A', 10), (2, 'High', 'A', 30), (3, 'Mid', 'A', 20), (4, 'Null', 'A', None),
    (5, 'Solo', 'B', 50), (6, 'Low', 'C', 1), (7, 'High', 'C', 9), (8, 'Higher', 'C', 20),
    (9, 'Low', None, 2), (10, 'High', None, 8), (11, 'Never', 'D', None)])
check(37, [products], [(10, 'High', None, 8), (2, 'High', 'A', 30), (8, 'Higher', 'C', 20)])
check(38, [products, orders, details], [(4, 'Null', 'A'), (5, 'Solo', 'B'), (6, 'Low', 'C'),
    (7, 'High', 'C'), (8, 'Higher', 'C'), (9, 'Low', None), (10, 'High', None), (11, 'Never', 'D')])
check(8, [products, details], [(4, 'Null', 'A', None), (5, 'Solo', 'B', 50), (6, 'Low', 'C', 1),
    (7, 'High', 'C', 9), (10, 'High', None, 8), (11, 'Never', 'D', None)])

orders = fixture('orders', [('Order ID', 'SIGNED'), ('Shipping Fee', 'DECIMAL(20,6)')],
                 [(1, 20), (2, '20.0001'), (3, 100), (4, 100), (5, 100), (6, 100)])
details = fixture('order details', [('Order ID', 'SIGNED'), ('Unit Price', 'DECIMAL(20,6)'),
                                   ('Quantity', 'SIGNED'), ('Discount', 'DECIMAL(4,2)')],
                  [(1, 50, 2, '0.5'), (2, 25, 2, '0.9'), (2, 50, 1, 0), (3, 0, 1, 0),
                   (4, -1, 1, 0), (5, None, 1, 0)])
check(10, [orders, details], [(2, 100, '20.0001', '0.2000')])

employees = fixture('employees', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'),
                                 ('Last Name', 'CHAR(20)'), ('City', 'CHAR(20)')],
                    [(employee_id, 'E%d' % employee_id, 'L%d' % employee_id,
                      None if employee_id == 5 else 'Y' if employee_id == 7 else 'X')
                     for employee_id in range(1, 14)])
customers = fixture('customers', [('ID', 'SIGNED'), ('City', 'CHAR(20)')],
                    [(1, 'A'), (2, 'B'), (3, 'C'), (4, 'D'), (5, 'E'),
                     (6, 'X'), (7, 'Y'), (8, None), (9, 'A')])
annual_pairs = [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 1), (1, 9),
                (2, 1), (2, 2), (2, 3), (2, 6), (5, 1), (5, 2), (5, 3), (5, 4),
                (6, 1), (6, 2), (6, 3), (6, 4), (6, 8), (8, 8), (9, 404),
                (10, None), (11, 6), (12, 1), (12, 2), (12, 3)]
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Employee ID', 'SIGNED'),
                           ('Customer ID', 'SIGNED'), ('Order Date', 'DATETIME')],
                 [(order_id, employee_id, customer_id, '2006-01-01')
                  for order_id, (employee_id, customer_id) in enumerate(annual_pairs, 1)] + [
    (101, 1, 6, '2005-12-31 23:59:59'), (102, 1, 8, '2007-01-01'),
    (103, 4, 1, '2005-12-31 23:59:59'), (104, 7, 1, '2006-12-31 23:59:59'),
    (105, 7, 8, '2007-01-01'), (106, 7, 7, '2005-12-31 23:59:59'), (107, 13, 1, None)])
check(39, [employees, customers, orders], [(1, 'E1', 'L1', 5), (2, 'E2', 'L2', 4),
    (5, 'E5', 'L5', 4), (6, 'E6', 'L6', 4)])
check(41, [employees, customers, orders], [(1, 'E1', 'L1'), (7, 'E7', 'L7'), (12, 'E12', 'L12')])

customers = fixture('customers', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'), ('Last Name', 'CHAR(20)')],
                    [(customer_id, 'C%d' % customer_id, 'L%d' % customer_id) for customer_id in range(1, 9)])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Customer ID', 'SIGNED'), ('Order Date', 'DATETIME')], [
    (1, 1, '2006-01-01'), (2, 1, '2006-12-31 23:59:59'), (3, 1, '2007-01-01'),
    (4, 2, '2006-06-01'), (5, 3, '2006-06-01'), (6, 4, '2006-06-01'),
    (7, 4, '2005-12-31 23:59:59'), (8, 5, '2006-06-01'), (9, 6, '2006-06-01'),
    (10, 7, '2006-06-01'), (11, 8, '2005-12-31 23:59:59')])
products = fixture('products', [('ID', 'SIGNED'), ('Category', 'CHAR(20)')],
                   [(1, 'A'), (2, 'A'), (3, 'B'), (4, 'C'), (5, 'D'), (6, None)])
details = fixture('order details', [('Order ID', 'SIGNED'), ('Product ID', 'SIGNED')], [
    (1, 1), (1, 1), (1, 2), (1, 3), (2, 4), (2, 1), (2, 6), (3, 5),
    (4, 1), (4, 3), (4, 4), (4, 5), (5, 1), (5, 3), (6, 1), (6, 3), (7, 4),
    (9, 6), (10, 1), (10, 3), (10, 4), (10, 404), (11, 1), (11, 3), (11, 4)])
check(40, [customers, orders, products, details], [(1, 'C1', 'L1', 3), (7, 'C7', 'L7', 3)])

orders = fixture('orders', [('Order ID', 'SIGNED'), ('Order Date', 'DATETIME')], [
    (1, '2006-01-01'), (2, '2006-06-01'), (3, '2006-12-31 23:59:59'), (4, '2006-04-01'),
    (5, '2005-12-31 23:59:59'), (6, '2007-01-01'), (7, None), (8, '2006-03-01')])
details = fixture('order details', [('Order ID', 'SIGNED'), ('Product ID', 'SIGNED')], [
    (1, 1), (1, 1), (1, 2), (1, 2), (1, 3), (1, 4), (1, None),
    (2, 1), (2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3), (4, 1), (4, 2),
    (5, 1), (5, 3), (5, 4), (5, 5), (6, 1), (6, 3), (6, 4), (6, 5),
    (7, 4), (7, 5), (8, 9), (8, 9)])
check(42, [orders, details], [(1, 2, 4), (1, 3, 3), (2, 3, 3)])

customers = fixture('customers', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'), ('Last Name', 'CHAR(20)')],
                    [(1, 'A', 'One'), (2, 'B', 'Two'), (3, 'C', 'Three')])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Customer ID', 'SIGNED')], [(1, 1), (2, 1), (3, 2)])
details = fixture('order details', [('Order ID', 'SIGNED'), ('Product ID', 'SIGNED')],
                  [(1, 1), (1, 2), (1, 2), (3, 1)])
count_example = next(entry for entry in THEORY6 if entry['id'] == 'TH6-010')['examples'][0]
assert execute(count_example, [customers, orders, details]) == [
    (1, 'A', 'One', 2), (2, 'B', 'Two', 1), (3, 'C', 'Three', 0)]
print('PASS TH6-010 duplicate details, order without details, customer without orders')

rank_example = next(entry for entry in THEORY6 if entry['id'] == 'TH6-005')['examples'][0]
prices = [100, 100, 90, 80, 70, 60, 50, 40, 30, 20, 20, 10, None]
product_columns = [('ID', 'SIGNED'), ('Product Name', 'CHAR(20)'), ('List Price', 'DECIMAL(10,2)')]
product_rows = [(product_id, 'P%d' % product_id, price) for product_id, price in enumerate(prices, 1)]
products = fixture('products', product_columns, product_rows)
exact_ten = 'SELECT ID, `Product Name`, `List Price` FROM products ORDER BY `List Price` DESC, ID ASC LIMIT 10;'
assert execute(exact_ten, [products]) == product_rows[:10]
assert execute(rank_example, [products]) == product_rows[:11]
assert len(execute(rank_example.replace('RANK() OVER', 'DENSE_RANK() OVER'), [products])) == 12
for available in (0, 4):
    products = fixture('products', product_columns, product_rows[:available])
    assert execute(exact_ten, [products]) == product_rows[:available]
    assert execute(rank_example, [products]) == product_rows[:available]
null_boundary = [(product_id, 'P%d' % product_id, 100 - product_id if product_id < 9 else None)
                 for product_id in range(1, 13)]
assert execute(rank_example, [fixture('products', product_columns, null_boundary)]) == null_boundary
print('PASS TH6-005 exact ten, tenth-row ties versus distinct levels, fewer products, NULL boundary')

employees = fixture('employees', [('ID', 'SIGNED'), ('First Name', 'CHAR(20)'),
                                 ('Last Name', 'CHAR(20)'), ('City', 'CHAR(20)')], [
    (1, 'Same', 'Name', 'Elsewhere'), (2, 'Same', 'Name', None), (3, 'No', 'Orders', 'A')])
customers = fixture('customers', [('ID', 'SIGNED'), ('City', 'CHAR(20)')], [
    (1, 'A'), (2, 'A'), (3, 'A'), (4, 'B'), (5, 'B'), (6, None), (7, None), (8, 'C')])
orders = fixture('orders', [('Order ID', 'SIGNED'), ('Employee ID', 'SIGNED'),
                           ('Customer ID', 'SIGNED'), ('Ship City', 'CHAR(20)'),
                           ('Order Date', 'DATETIME')], [
    (1, 1, 1, 'X', '2005-01-01'), (2, 1, 1, 'Y', '2006-01-01'),
    (3, 1, 2, 'Z', '2007-01-01'), (4, 1, 3, 'X', None),
    (5, 1, 4, 'X', '2006-01-01'), (6, 1, 5, 'Y', '2006-01-01'),
    (7, 1, 6, 'X', '2006-01-01'), (8, 1, 7, 'X', '2006-01-01'),
    (9, 1, 8, 'X', '2006-01-01'), (10, 1, 8, 'X', '2006-01-01'),
    (11, 2, 1, 'X', '2006-01-01'), (12, 2, 4, 'X', '2006-01-01'),
    (13, 2, 4, 'X', '2006-01-01'), (14, 2, 5, 'X', '2006-01-01')])
check(43, [employees, customers, orders], [
    (1, 'Same', 'Name', 'A', 3), (1, 'Same', 'Name', 'B', 2), (2, 'Same', 'Name', 'B', 2)])
