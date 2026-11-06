"""Level 2: deterministic template families. Each variation = (question, sql, alt, ...). build_bank.py executes
sql and alt on the Northwind dump and keeps the result-set comparison. Every param set changes the SQL structure or
semantics (table, join path, operator, aggregate, direction, negation), not just a number.
Constraint comparisons rely on the question text being phrased precisely."""
import itertools

OPS = {  # phrase, sql op
    'more than': '>', 'at least': '>=', 'exactly': '=', 'fewer than': '<', 'at most': '<='}

def family_categories():
    out = []
    for phrase, op in OPS.items():
        for n in (2, 3):
            if op in ('=', '<=', '<') and n == 2 and phrase != 'exactly': continue
            q = f"Find customers who placed orders for products from {phrase} {n} different categories."
            base = ("FROM customers c JOIN orders o ON o.`Customer ID` = c.ID\n"
                    "JOIN `order details` od ON od.`Order ID` = o.`Order ID`\nJOIN products p ON p.ID = od.`Product ID`\n")
            sql = f"SELECT c.ID, c.Company, COUNT(DISTINCT p.Category) AS n_categories\n{base}GROUP BY c.ID, c.Company\nHAVING COUNT(DISTINCT p.Category) {op} {n};"
            alt = (f"SELECT c.ID, c.Company, t.n FROM customers c JOIN (SELECT o.`Customer ID` cid, COUNT(DISTINCT p.Category) n\n"
                   f"FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` JOIN products p ON p.ID = od.`Product ID` GROUP BY o.`Customer ID`) t ON t.cid = c.ID WHERE t.n {op} {n};")
            out.append(dict(q=q, sql=sql, alt=alt, pattern='group_having', diff=4, cmp='set', tags=['count distinct', 'having', 'category', 'join', 'multiple tables'],
                            why=f"Same skeleton as the exam question; operator '{op}' ({phrase}) and N={n} change the HAVING condition and the result."))
    return out

def family_never():
    items = [
     ("Find customers who have never placed an order.", 'customers', 'orders', 'Customer ID', 'ID', 'Company'),
     ("Find employees who have never processed an order.", 'employees', 'orders', 'Employee ID', 'ID', 'Last Name'),
     ("Find shippers that have never shipped an order.", 'shippers', 'orders', 'Shipper ID', 'ID', 'Company'),
     ("Find suppliers with no purchase orders.", 'suppliers', 'purchase orders', 'Supplier ID', 'ID', 'Company'),
    ]
    out = []
    for q, par, ch, fk, pk, col in items:
        sql = f"SELECT p.{'`'+pk+'`' if ' ' in pk else pk}, p.`{col}`\nFROM `{par}` p\nWHERE NOT EXISTS (SELECT 1 FROM `{ch}` x WHERE x.`{fk}` = p.{pk});"
        alt = f"SELECT p.{pk}, p.`{col}`\nFROM `{par}` p LEFT JOIN `{ch}` x ON x.`{fk}` = p.{pk}\nWHERE x.`{fk}` IS NULL;"
        out.append(dict(q=q, sql=sql, alt=alt, pattern='not_exists', diff=2, cmp='set', tags=['not exists', 'never', 'left join', 'anti join'],
                        why="Negative condition (never/no): anti-join, not an inner join with <>."))
    # positive twin
    out.append(dict(q="Find customers who have placed at least one order.", sql="SELECT c.ID, c.Company FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.`Customer ID` = c.ID);",
                    alt="SELECT ID, Company FROM customers WHERE ID IN (SELECT `Customer ID` FROM orders);", pattern='exists', diff=1, cmp='set', tags=['exists', 'in'],
                    why="Positive twin of 'customers who have never placed an order'."))
    out.append(dict(q="Find products that have never been ordered.", sql="SELECT p.ID, p.`Product Name` FROM products p WHERE NOT EXISTS (SELECT 1 FROM `order details` od WHERE od.`Product ID` = p.ID);",
                    alt="SELECT p.ID, p.`Product Name` FROM products p LEFT JOIN `order details` od ON od.`Product ID` = p.ID WHERE od.ID IS NULL;", pattern='not_exists', diff=2, cmp='set', tags=['not exists', 'never', 'left join'],
                    why="Anti-join through order details."))
    out.append(dict(q="Find products that have been ordered at least once.", sql="SELECT p.ID, p.`Product Name` FROM products p WHERE p.ID IN (SELECT `Product ID` FROM `order details`);",
                    alt="SELECT DISTINCT p.ID, p.`Product Name` FROM products p JOIN `order details` od ON od.`Product ID` = p.ID;", pattern='in_notin', diff=1, cmp='set', tags=['in', 'distinct', 'join'],
                    why="Positive twin; DISTINCT needed if joining."))
    return out

def family_topn():
    items = [('products', 'List Price', 'ID', 'products', 'most expensive'), ('products', 'Standard Cost', 'ID', 'products', 'highest standard cost'),
             ('orders', 'Shipping Fee', 'Order ID', 'orders', 'highest shipping fee'), ('orders', 'Taxes', 'Order ID', 'orders', 'highest taxes')]
    out = []
    for tb, col, key, _, label in items:
        for n in (3, 5):
            for d, word in (('DESC', 'highest'), ('ASC', 'lowest')):
                if n == 5 and tb == 'orders' and col == 'Taxes': continue
                q = f"Return the top {n} {tb} with the {word} {col.lower()} (exactly {n} rows, break ties by {key.lower()})."
                sql = f"SELECT * FROM `{tb}` ORDER BY `{col}` {d}, `{key}` LIMIT {n};"
                cols = {'products': "`Supplier IDs`, ID, `Product Code`, `Product Name`, Description, `Standard Cost`, `List Price`, `Reorder Level`, `Target Level`, `Quantity Per Unit`, Discontinued, `Minimum Reorder Quantity`, Category, Attachments"}.get(tb, '*')
                alt = f"SELECT {cols} FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY `{col}` {d}, `{key}`) rn FROM `{tb}`) t WHERE rn <= {n} ORDER BY rn;"
                if tb == 'orders': alt = f"SELECT `Order ID`, `Employee ID`, `Customer ID`, `Order Date`, `Shipped Date`, `Shipper ID`, `Ship Name`, `Ship Address`, `Ship City`, `Ship State/Province`, `Ship ZIP/Postal Code`, `Ship Country/Region`, `Shipping Fee`, `Taxes`, `Payment Type`, `Paid Date`, `Notes`, `Tax Rate`, `Tax Status`, `Status ID` FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY `{col}` {d}, `{key}`) rn FROM `{tb}`) t WHERE rn <= {n} ORDER BY rn;"
                out.append(dict(q=q, sql=sql, alt=alt, pattern='topn_rank', diff=2, cmp='ordered', tags=['top n', 'limit', 'order by', word, 'exactly n'],
                                why=f"Exactly N rows ({word}); direction {d}. Ties at the cut-off are broken by key."))
    # with ties
    out.append(dict(q="Return all products whose list price is among the 3 highest distinct prices (include ties).",
                    sql="SELECT * FROM products WHERE `List Price` >= (SELECT MIN(`List Price`) FROM (SELECT DISTINCT `List Price` FROM products ORDER BY `List Price` DESC LIMIT 3) t) ORDER BY `List Price` DESC, ID;",
                    alt="SELECT `Supplier IDs`, ID, `Product Code`, `Product Name`, Description, `Standard Cost`, `List Price`, `Reorder Level`, `Target Level`, `Quantity Per Unit`, Discontinued, `Minimum Reorder Quantity`, Category, Attachments FROM (SELECT *, DENSE_RANK() OVER (ORDER BY `List Price` DESC) dr FROM products) t WHERE dr <= 3 ORDER BY `List Price` DESC, ID;",
                    pattern='topn_rank', diff=4, cmp='ordered', tags=['top n', 'ties', 'dense_rank', 'distinct values'], why="Top N INCLUDING ties by value (DENSE_RANK), unlike LIMIT N."))
    out.append(dict(q="Return the orders whose shipping fee is the 2nd highest distinct shipping fee value (include ties).",
                    sql="SELECT * FROM orders WHERE `Shipping Fee` = (SELECT DISTINCT `Shipping Fee` FROM orders ORDER BY `Shipping Fee` DESC LIMIT 1 OFFSET 1) ORDER BY `Order ID`;",
                    alt="SELECT `Order ID`, `Employee ID`, `Customer ID`, `Order Date`, `Shipped Date`, `Shipper ID`, `Ship Name`, `Ship Address`, `Ship City`, `Ship State/Province`, `Ship ZIP/Postal Code`, `Ship Country/Region`, `Shipping Fee`, `Taxes`, `Payment Type`, `Paid Date`, `Notes`, `Tax Rate`, `Tax Status`, `Status ID` FROM (SELECT *, DENSE_RANK() OVER (ORDER BY `Shipping Fee` DESC) dr FROM orders) t WHERE dr = 2 ORDER BY `Order ID`;",
                    pattern='topn_rank', diff=4, cmp='ordered', tags=['nth highest', 'ties', 'dense_rank', 'distinct values'], why="Nth highest VALUE (ties included) differs from the Nth row."))
    out.append(dict(q="Retrieve (all columns) 3 orders starting from the 6th lowest shipping fee.",
                    sql="SELECT * FROM orders ORDER BY `Shipping Fee` ASC, `Order ID` LIMIT 3 OFFSET 5;",
                    alt="SELECT `Order ID`, `Employee ID`, `Customer ID`, `Order Date`, `Shipped Date`, `Shipper ID`, `Ship Name`, `Ship Address`, `Ship City`, `Ship State/Province`, `Ship ZIP/Postal Code`, `Ship Country/Region`, `Shipping Fee`, `Taxes`, `Payment Type`, `Paid Date`, `Notes`, `Tax Rate`, `Tax Status`, `Status ID` FROM (SELECT *, ROW_NUMBER() OVER (ORDER BY `Shipping Fee` ASC, `Order ID`) rn FROM orders) t WHERE rn BETWEEN 6 AND 8 ORDER BY rn;",
                    pattern='topn_rank', diff=3, cmp='ordered', tags=['offset', 'lowest', 'nth', 'limit'], why="Mirror of the exam question with LOWEST instead of highest (ASC)."))
    return out

def family_group_count():
    items = [('orders', 'Customer ID', 'customer', 'customers'), ('orders', 'Employee ID', 'employee', 'employees'), ('orders', 'Shipper ID', 'shipper', 'shippers'),
             ('orders', 'Status ID', 'order status', None), ('products', 'Category', 'product category', None)]
    out = []
    for tb, col, label, _ in items:
        key = 'Order ID' if tb == 'orders' else 'ID'
        out.append(dict(q=f"Count the number of {tb} per {label}.",
                        sql=f"SELECT `{col}`, COUNT(*) AS n FROM `{tb}` GROUP BY `{col}`;",
                        alt=f"SELECT DISTINCT `{col}`, COUNT(`{key}`) OVER (PARTITION BY `{col}`) AS n FROM `{tb}`;",
                        pattern='group_having', diff=1, cmp='set', tags=['count', 'group by', label], why="Basic grouping."))
        for op_phrase, op in (('more than', '>'), ('at most', '<=')):
            out.append(dict(q=f"List each {label} that has {op_phrase} 2 {tb}, with the count.",
                            sql=f"SELECT `{col}`, COUNT(*) AS n FROM `{tb}` GROUP BY `{col}` HAVING COUNT(*) {op} 2;",
                            alt=f"SELECT `{col}`, n FROM (SELECT `{col}`, COUNT(*) AS n FROM `{tb}` GROUP BY `{col}`) t WHERE n {op} 2;",
                            pattern='group_having', diff=2, cmp='set', tags=['having', 'count', 'group by', op_phrase], why=f"HAVING with '{op_phrase}' => {op} 2."))
    return out

def family_aggregates():
    out = []
    for fn, word in (('AVG', 'average'), ('SUM', 'total'), ('MAX', 'maximum'), ('MIN', 'minimum')):
        for col, tb in (('List Price', 'products'), ('Shipping Fee', 'orders')):
            out.append(dict(q=f"Return the {word} {col.lower()} of all {tb}.",
                            sql=f"SELECT {fn}(`{col}`) AS {word.replace(' ', '_')} FROM `{tb}`;",
                            alt=f"SELECT {fn}(x) FROM (SELECT `{col}` AS x FROM `{tb}`) t;",
                            pattern='aggregate', diff=1, cmp='set', tags=[fn.lower(), 'aggregate', word], why="Single-aggregate query."))
    out.append(dict(q="Return the average list price per product category, only for categories with an average list price above 20.",
                    sql="SELECT Category, AVG(`List Price`) AS avg_price FROM products GROUP BY Category HAVING AVG(`List Price`) > 20;",
                    alt="SELECT Category, avg_price FROM (SELECT Category, AVG(`List Price`) AS avg_price FROM products GROUP BY Category) t WHERE avg_price > 20;",
                    pattern='group_having', diff=2, cmp='set', tags=['avg', 'having', 'group by'], why="Aggregate filter belongs in HAVING."))
    out.append(dict(q="Return the average shipping fee of orders shipped to USA that have already been shipped (Shipped Date is not NULL).",
                    sql="SELECT AVG(`Shipping Fee`) FROM orders WHERE `Ship Country/Region` = 'USA' AND `Shipped Date` IS NOT NULL;",
                    alt="SELECT SUM(`Shipping Fee`) / COUNT(`Shipping Fee`) FROM orders WHERE `Ship Country/Region` = 'USA' AND `Shipped Date` IS NOT NULL;",
                    pattern='null_handling', diff=2, cmp='set', tags=['avg', 'null', 'is not null', 'shipped'], why="Exclusion of NULL shipped dates."))
    out.append(dict(q="Return the average shipping fee of orders shipped to USA including the orders that are not shipped yet (Shipped Date is NULL).",
                    sql="SELECT AVG(`Shipping Fee`) FROM orders WHERE `Ship Country/Region` = 'USA';",
                    alt="SELECT SUM(`Shipping Fee`) / COUNT(*) FROM orders WHERE `Ship Country/Region` = 'USA';",
                    pattern='null_handling', diff=2, cmp='set', tags=['avg', 'null', 'including null'], why="Inclusion of NULL shipped dates (no filter)."))
    return out

def family_sales():
    out = []
    chains = [
      ('customer', 'c.ID, c.Company', "customers c JOIN orders o ON o.`Customer ID` = c.ID", 'c.ID, c.Company'),
      ('employee', 'e.ID, e.`Last Name`', "employees e JOIN orders o ON o.`Employee ID` = e.ID", 'e.ID, e.`Last Name`'),
      ('product category', 'p.Category', None, 'p.Category'),
      ('product', 'p.ID, p.`Product Name`', None, 'p.ID, p.`Product Name`'),
      ('shipper', 's.ID, s.Company', "shippers s JOIN orders o ON o.`Shipper ID` = s.ID", 's.ID, s.Company'),
    ]
    for label, sel, frm, grp in chains:
        if frm is None:
            frm_sql = "products p JOIN `order details` od ON od.`Product ID` = p.ID"
        else:
            frm_sql = frm + " JOIN `order details` od ON od.`Order ID` = o.`Order ID`"
        for fn, word in (('SUM(od.`Unit Price` * od.Quantity)', 'total sales value'), ('SUM(od.Quantity)', 'total quantity ordered')):
            osel = ', '.join(x.split('.')[-1].strip() for x in sel.split(','))
            sql = f"SELECT {sel}, {fn} AS v FROM {frm_sql} GROUP BY {grp};"
            alt = f"SELECT {osel}, v FROM (SELECT {sel}, {fn} AS v FROM {frm_sql} GROUP BY {grp}) t;"
            out.append(dict(q=f"Calculate the {word} per {label}.", sql=sql, alt=alt, pattern='multi_agg', diff=3, cmp='set',
                            tags=['sum', 'join', 'group by', label, 'multiple tables'], why=f"Join chain to order details, aggregate per {label}."))
        out.append(dict(q=f"Find the {label} with the highest total sales value (include ties).",
                        sql=f"SELECT {sel}, v FROM (SELECT {sel}, SUM(od.`Unit Price` * od.Quantity) AS v FROM {frm_sql} GROUP BY {grp}) t WHERE v = (SELECT MAX(v2) FROM (SELECT SUM(od.`Unit Price` * od.Quantity) AS v2 FROM {frm_sql} GROUP BY {grp}) u);".replace(sel + ', v', ', '.join(x.split('.')[-1].strip() for x in sel.split(',')) + ', v'),
                        alt=f"SELECT {', '.join(x.split('.')[-1].strip() for x in sel.split(','))}, v FROM (SELECT {sel}, SUM(od.`Unit Price` * od.Quantity) AS v, RANK() OVER (ORDER BY SUM(od.`Unit Price` * od.Quantity) DESC) rk FROM {frm_sql} GROUP BY {grp}) t WHERE rk = 1;",
                        pattern='topn_rank', diff=4, cmp='set', tags=['max', 'ties', 'sum', 'highest', 'join', label], why="Highest aggregate, ties kept."))
        out.append(dict(q=f"Find the {label} with the lowest total sales value (include ties).",
                        sql=f"SELECT {', '.join(x.split('.')[-1].strip() for x in sel.split(','))}, v FROM (SELECT {sel}, SUM(od.`Unit Price` * od.Quantity) AS v FROM {frm_sql} GROUP BY {grp}) t WHERE v = (SELECT MIN(v2) FROM (SELECT SUM(od.`Unit Price` * od.Quantity) AS v2 FROM {frm_sql} GROUP BY {grp}) u);",
                        alt=f"SELECT {', '.join(x.split('.')[-1].strip() for x in sel.split(','))}, v FROM (SELECT {sel}, SUM(od.`Unit Price` * od.Quantity) AS v, RANK() OVER (ORDER BY SUM(od.`Unit Price` * od.Quantity) ASC) rk FROM {frm_sql} GROUP BY {grp}) t WHERE rk = 1;",
                        pattern='topn_rank', diff=4, cmp='set', tags=['min', 'ties', 'sum', 'lowest', 'join', label], why="LOWEST instead of highest: MIN / ASC."))
    return out

def family_dates():
    out = []
    for yr_phrase, lo, hi in (('in 2006', '2006-01-01', '2007-01-01'), ('in April 2006', '2006-04-01', '2006-05-01'), ('in the first quarter of 2006 (January to March)', '2006-01-01', '2006-04-01')):
        out.append(dict(q=f"Count the orders placed {yr_phrase}.",
                        sql=f"SELECT COUNT(*) FROM orders WHERE `Order Date` >= '{lo}' AND `Order Date` < '{hi}';",
                        alt=f"SELECT SUM(`Order Date` >= '{lo}' AND `Order Date` < '{hi}') FROM orders;",
                        pattern='date', diff=1, cmp='set', tags=['date', 'count', 'range'], why="Half-open date range."))
    out.append(dict(q="Count the orders per month, formatted as YYYY-MM.", sql="SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS ym, COUNT(*) FROM orders GROUP BY ym;",
                    alt="SELECT CONCAT(YEAR(`Order Date`), '-', LPAD(MONTH(`Order Date`), 2, '0')) AS ym, COUNT(*) FROM orders GROUP BY 1;",
                    pattern='date', diff=2, cmp='set', tags=['month', 'date_format', 'group by'], why="Monthly grouping key."))
    out.append(dict(q="For each employee, count the orders placed per month (YYYY-MM).", sql="SELECT `Employee ID`, DATE_FORMAT(`Order Date`, '%Y-%m') AS ym, COUNT(*) AS n FROM orders GROUP BY `Employee ID`, ym;",
                    alt="SELECT `Employee ID`, CONCAT(YEAR(`Order Date`), '-', LPAD(MONTH(`Order Date`), 2, '0')) ym, COUNT(*) n FROM orders GROUP BY `Employee ID`, 2;",
                    pattern='date', diff=2, cmp='set', tags=['month', 'group by', 'per month', 'employee'], why="Per-month grouping (contrast with 'all months combined')."))
    out.append(dict(q="Return the total quantity of each product purchased per month (YYYY-MM) from inventory transactions, only status 'Purchased'.",
                    sql="SELECT DATE_FORMAT(it.`Transaction Created Date`, '%Y-%m') AS `Month`, it.`Product ID`, SUM(it.Quantity) AS q FROM `inventory transactions` it JOIN `inventory transaction types` tt ON tt.ID = it.`Transaction Type` WHERE tt.`Type Name` = 'Purchased' GROUP BY `Month`, it.`Product ID`;",
                    alt="SELECT DATE_FORMAT(`Transaction Created Date`, '%Y-%m'), `Product ID`, SUM(Quantity) FROM `inventory transactions` WHERE `Transaction Type` = 1 GROUP BY 1, 2;",
                    pattern='date', diff=3, cmp='set', tags=['inventory', 'purchased', 'month', 'sum', 'join'], why="Same as the exam question but type Purchased (1) instead of Sold (2)."))
    out.append(dict(q="Return the total quantity of products wasted (inventory transaction type Waste) per product.",
                    sql="SELECT it.`Product ID`, SUM(it.Quantity) q FROM `inventory transactions` it JOIN `inventory transaction types` tt ON tt.ID = it.`Transaction Type` WHERE tt.`Type Name` = 'Waste' GROUP BY it.`Product ID`;",
                    alt="SELECT `Product ID`, SUM(Quantity) FROM `inventory transactions` WHERE `Transaction Type` = 4 GROUP BY `Product ID`;",
                    pattern='multi_agg', diff=2, cmp='set', tags=['inventory', 'waste', 'sum'], why="Waste = type 4; no rows in this dump (empty result is valid)."))
    return out

def family_misc():
    D = lambda **k: k
    return [
     D(q="Return orders whose shipping fee is greater than 15% of the order total value, showing the ratio rounded to 2 decimals.", sql="SELECT o.`Order ID`, ROUND(o.`Shipping Fee` / t.v, 2) AS ratio FROM orders o JOIN (SELECT `Order ID`, SUM(`Unit Price` * Quantity) v FROM `order details` GROUP BY `Order ID`) t ON t.`Order ID` = o.`Order ID` WHERE o.`Shipping Fee` > 0.15 * t.v;",
       alt="SELECT o.`Order ID`, ROUND(o.`Shipping Fee` / SUM(od.`Unit Price` * od.Quantity), 2) FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` GROUP BY o.`Order ID`, o.`Shipping Fee` HAVING o.`Shipping Fee` > 0.15 * SUM(od.`Unit Price` * od.Quantity);",
       pattern='multi_agg', diff=4, cmp='set', tags=['ratio', 'round', 'sum', 'having', 'percent'], why="Rounding changed to 2 decimals."),
     D(q="Return products with a profit margin below 20% ((List Price - Standard Cost) / Standard Cost).", sql="SELECT `Product Code`, `Product Name`, (`List Price` - `Standard Cost`) / `Standard Cost` AS pm FROM products WHERE (`List Price` - `Standard Cost`) / `Standard Cost` < 0.2;",
       alt="SELECT `Product Code`, `Product Name`, pm FROM (SELECT *, (`List Price` - `Standard Cost`) / `Standard Cost` pm FROM products) t WHERE pm < 0.2;",
       pattern='computed', diff=2, cmp='set', tags=['margin', 'percent', 'less than'], why="Direction reversed (< instead of >=)."),
     D(q="Return products whose list price is above the average list price of their own category.", sql="SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p WHERE p.`List Price` > (SELECT AVG(q.`List Price`) FROM products q WHERE q.Category = p.Category);",
       alt="SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p JOIN (SELECT Category, AVG(`List Price`) a FROM products GROUP BY Category) g ON g.Category = p.Category WHERE p.`List Price` > g.a;",
       pattern='correlated', diff=3, cmp='set', tags=['correlated', 'avg', 'subquery'], why="Correlated subquery vs derived-table join."),
     D(q="Return products whose list price is higher than ALL products of the category Beverages.", sql="SELECT ID, `Product Name`, `List Price` FROM products WHERE `List Price` > ALL (SELECT `List Price` FROM products WHERE Category = 'Beverages');",
       alt="SELECT ID, `Product Name`, `List Price` FROM products WHERE `List Price` > (SELECT MAX(`List Price`) FROM products WHERE Category = 'Beverages');",
       pattern='all_any', diff=3, cmp='set', tags=['all', 'subquery', 'max'], why="> ALL = greater than the maximum."),
     D(q="Return products whose list price is higher than ANY product of the category Beverages.", sql="SELECT ID, `Product Name`, `List Price` FROM products WHERE `List Price` > ANY (SELECT `List Price` FROM products WHERE Category = 'Beverages');",
       alt="SELECT ID, `Product Name`, `List Price` FROM products WHERE `List Price` > (SELECT MIN(`List Price`) FROM products WHERE Category = 'Beverages');",
       pattern='all_any', diff=3, cmp='set', tags=['any', 'subquery', 'min'], why="> ANY = greater than the minimum (contrast with ALL)."),
     D(q="Find customers whose orders include every product of the category Beverages.", sql="SELECT o.`Customer ID` FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` JOIN products p ON p.ID = od.`Product ID` WHERE p.Category = 'Beverages' GROUP BY o.`Customer ID` HAVING COUNT(DISTINCT p.ID) = (SELECT COUNT(*) FROM products WHERE Category = 'Beverages');",
       alt="SELECT c.ID FROM customers c WHERE NOT EXISTS (SELECT 1 FROM products p WHERE p.Category = 'Beverages' AND NOT EXISTS (SELECT 1 FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` WHERE o.`Customer ID` = c.ID AND od.`Product ID` = p.ID));",
       pattern='division', diff=5, cmp='set', tags=['division', 'all', 'every', 'not exists'], why="Relational division: counting vs double NOT EXISTS."),
     D(q="Find the pairs of customers who live in the same city (each pair once).", sql="SELECT a.ID, b.ID, a.City FROM customers a JOIN customers b ON a.City = b.City AND a.ID < b.ID;",
       alt="SELECT a.ID, b.ID, a.City FROM customers a, customers b WHERE a.City = b.City AND a.ID < b.ID;", pattern='self_join', diff=3, cmp='set', tags=['self join', 'pairs', 'same city'], why="Self join on city with a.ID < b.ID."),
     D(q="For each employee show the number of shipped and not shipped orders (two columns).", sql="SELECT `Employee ID`, SUM(`Shipped Date` IS NOT NULL) shipped, SUM(`Shipped Date` IS NULL) not_shipped FROM orders GROUP BY `Employee ID`;",
       alt="SELECT `Employee ID`, COUNT(`Shipped Date`) shipped, COUNT(*) - COUNT(`Shipped Date`) not_shipped FROM orders GROUP BY `Employee ID`;",
       pattern='cond_agg', diff=3, cmp='set', tags=['conditional aggregation', 'null', 'case when', 'shipped'], why="Conditional aggregation on NULL / NOT NULL."),
     D(q="For each customer show total quantity ordered of the category Beverages and of the category Condiments in two separate columns.", sql="SELECT o.`Customer ID`, SUM(CASE WHEN p.Category = 'Beverages' THEN od.Quantity ELSE 0 END) beverages, SUM(CASE WHEN p.Category = 'Condiments' THEN od.Quantity ELSE 0 END) condiments FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` JOIN products p ON p.ID = od.`Product ID` GROUP BY o.`Customer ID`;",
       alt="SELECT o.`Customer ID`, SUM(od.Quantity * (p.Category = 'Beverages')) b, SUM(od.Quantity * (p.Category = 'Condiments')) c FROM orders o JOIN `order details` od ON od.`Order ID` = o.`Order ID` JOIN products p ON p.ID = od.`Product ID` GROUP BY o.`Customer ID`;",
       pattern='cond_agg', diff=4, cmp='set', tags=['conditional aggregation', 'pivot', 'case when', 'category'], why="Pivot with CASE inside SUM."),
     D(q="Return the orders that have no payment type recorded (Payment Type is NULL).", sql="SELECT * FROM orders WHERE `Payment Type` IS NULL ORDER BY `Order ID`;",
       alt="SELECT `Order ID`, `Employee ID`, `Customer ID`, `Order Date`, `Shipped Date`, `Shipper ID`, `Ship Name`, `Ship Address`, `Ship City`, `Ship State/Province`, `Ship ZIP/Postal Code`, `Ship Country/Region`, `Shipping Fee`, `Taxes`, `Payment Type`, `Paid Date`, `Notes`, `Tax Rate`, `Tax Status`, `Status ID` FROM orders WHERE NOT (`Payment Type` IS NOT NULL) ORDER BY `Order ID`;",
       pattern='null_handling', diff=1, cmp='ordered', tags=['null', 'is null', 'missing'], why="IS NULL, not = NULL."),
     D(q="Return the orders whose payment type is not 'Check' (exclude NULL payment types as well).", sql="SELECT `Order ID`, `Payment Type` FROM orders WHERE `Payment Type` <> 'Check' ORDER BY `Order ID`;",
       alt="SELECT `Order ID`, `Payment Type` FROM orders WHERE `Payment Type` IS NOT NULL AND `Payment Type` NOT IN ('Check') ORDER BY `Order ID`;",
       pattern='null_handling', diff=2, cmp='ordered', tags=['null', 'not', 'excluding null'], why="<> silently excludes NULL rows."),
     D(q="Return the orders whose payment type is not 'Check' (include orders with NULL payment type).", sql="SELECT `Order ID`, `Payment Type` FROM orders WHERE `Payment Type` <> 'Check' OR `Payment Type` IS NULL ORDER BY `Order ID`;",
       alt="SELECT `Order ID`, `Payment Type` FROM orders WHERE NOT (`Payment Type` <=> 'Check') ORDER BY `Order ID`;",
       pattern='null_handling', diff=2, cmp='ordered', tags=['null', 'not', 'including null', 'null-safe'], why="Include NULL: OR IS NULL or null-safe <=>."),
     D(q="Return the distinct cities of customers, sorted alphabetically.", sql="SELECT DISTINCT City FROM customers ORDER BY City;", alt="SELECT City FROM customers GROUP BY City ORDER BY City;",
       pattern='distinct', diff=1, cmp='ordered', tags=['distinct', 'order by', 'unique'], why="DISTINCT vs GROUP BY equivalence."),
     D(q="Count the distinct cities of customers.", sql="SELECT COUNT(DISTINCT City) FROM customers;", alt="SELECT COUNT(*) FROM (SELECT City FROM customers GROUP BY City) t;",
       pattern='distinct', diff=1, cmp='set', tags=['count distinct'], why="COUNT(DISTINCT)."),
     D(q="Return all companies of customers and suppliers in one list without duplicates.", sql="SELECT Company FROM customers UNION SELECT Company FROM suppliers;",
       alt="SELECT DISTINCT Company FROM (SELECT Company FROM customers UNION ALL SELECT Company FROM suppliers) t;", pattern='set_ops', diff=2, cmp='set', tags=['union', 'distinct'], why="UNION removes duplicates."),
     D(q="Return all companies of customers and suppliers in one list keeping duplicates.", sql="SELECT Company FROM customers UNION ALL SELECT Company FROM suppliers;",
       alt="SELECT Company FROM customers UNION ALL SELECT Company FROM suppliers;", pattern='set_ops', diff=1, cmp='set', tags=['union all', 'duplicates'], why="UNION ALL keeps duplicates."),
     D(q="Return the employees who processed more than 5 orders in total, with their names.", sql="SELECT e.ID, e.`Last Name`, e.`First Name`, COUNT(*) n FROM employees e JOIN orders o ON o.`Employee ID` = e.ID GROUP BY e.ID, e.`Last Name`, e.`First Name` HAVING COUNT(*) > 5;",
       alt="SELECT e.ID, e.`Last Name`, e.`First Name`, (SELECT COUNT(*) FROM orders o WHERE o.`Employee ID` = e.ID) n FROM employees e WHERE (SELECT COUNT(*) FROM orders o WHERE o.`Employee ID` = e.ID) > 5;",
       pattern='group_having', diff=2, cmp='set', tags=['having', 'count', 'join', 'more than'], why="HAVING with join to names."),
     D(q="Return the customers who placed orders handled by at least 3 different employees.", sql="SELECT `Customer ID`, COUNT(DISTINCT `Employee ID`) n FROM orders GROUP BY `Customer ID` HAVING COUNT(DISTINCT `Employee ID`) >= 3;",
       alt="SELECT cid, n FROM (SELECT `Customer ID` cid, COUNT(DISTINCT `Employee ID`) n FROM orders GROUP BY `Customer ID`) t WHERE n >= 3;", pattern='group_having', diff=3, cmp='set', tags=['count distinct', 'having', 'at least'], why="Distinct count with >=."),
     D(q="Return the customers who placed orders handled by fewer than 3 different employees.", sql="SELECT `Customer ID`, COUNT(DISTINCT `Employee ID`) n FROM orders GROUP BY `Customer ID` HAVING COUNT(DISTINCT `Employee ID`) < 3;",
       alt="SELECT cid, n FROM (SELECT `Customer ID` cid, COUNT(DISTINCT `Employee ID`) n FROM orders GROUP BY `Customer ID`) t WHERE n < 3;", pattern='group_having', diff=3, cmp='set', tags=['count distinct', 'having', 'fewer than'], why="Opposite operator of the previous entry."),
    ]

FAMILIES = [family_categories, family_never, family_topn, family_group_count, family_aggregates, family_sales, family_dates, family_misc]

def all_variations():
    out = []
    for f in FAMILIES:
        for v in f():
            v['family'] = f.__name__
            out.append(v)
    return out
