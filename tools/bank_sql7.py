"""Slide-gap families: DML, executable PSM, DDL, transactions, lookup tables.

All disposable objects use zz_ names. Real-table DML is rollback-only.
"""


def S(number, question, sql, alt, explanation, pattern, tags, techniques,
      mode=None, check=None, cleanup=None):
    return dict(id='SQL7-%03d' % number, question=question, sql=sql, alt=alt,
                explanation=explanation, pattern=pattern, tags=tags.split('|'),
                techniques=techniques.split('|'), difficulty=3, cmp='ordered',
                mode=mode, check=check, cleanup=cleanup)


def module(body):
    return 'DELIMITER //\n' + body + '\n//\nDELIMITER ;\n'


SQL7 = [
 S(1, 'Insert two shippers with IDs 99001 and 99002 named Training A and Training B in one INSERT statement.',
   "INSERT INTO shippers (ID, Company) VALUES (99001,'Training A'),(99002,'Training B');",
   "INSERT INTO shippers (ID, Company) SELECT 99001,'Training A' UNION ALL SELECT 99002,'Training B';",
   'An explicit column list allows the remaining nullable columns to take their defaults. The alternative inserts the same rows from a UNION ALL source. Verification reads the inserted keys before rolling back.',
   'computed', 'insert|multi row|shippers|write', 'multi-row VALUES|INSERT SELECT UNION ALL',
   'rollback', 'SELECT ID, Company FROM shippers WHERE ID IN (99001,99002) ORDER BY ID;', None),
]

for number, cutoff, direction in [(2, '2006-03-01', '<'), (3, '2006-04-01', '>=')]:
    predicate = "`Order Date` %s '%s'" % (direction, cutoff)
    SQL7.append(S(number,
        'Insert into a scratch archive zz_archive all orders whose Order Date is %s %s, using INSERT SELECT.' % ('before' if direction == '<' else 'on or after', cutoff),
        'CREATE TABLE zz_archive LIKE orders; INSERT INTO zz_archive SELECT * FROM orders WHERE ' + predicate + ';',
        'CREATE TABLE zz_archive AS SELECT * FROM orders WHERE ' + predicate + ';',
        'INSERT SELECT copies only qualifying rows into an initially empty archive. CREATE TABLE LIKE retains the source definition; the independent CTAS alternative matches the requested data, not the indexes. Only the scratch archive is dropped after verification.',
        'date', 'insert select|archive|orders|date|write', 'LIKE then INSERT SELECT|filtered CTAS',
        'ddl', 'SELECT `Order ID`, `Order Date` FROM zz_archive ORDER BY `Order ID`;', 'DROP TABLE IF EXISTS zz_archive;'))

SQL7 += [
 S(4, 'Update Beverages products: raise List Price by 10 percent and set Reorder Level to 30 in the same UPDATE.',
   "UPDATE products SET `List Price`=`List Price`*1.10, `Reorder Level`=30 WHERE Category='Beverages';",
   "UPDATE products p JOIN (SELECT 'Beverages' AS category, 1.10 AS factor, 30 AS level) rule ON p.Category=rule.category SET p.`List Price`=p.`List Price`*rule.factor, p.`Reorder Level`=rule.level;",
   'Both assignments use the original price and the same category predicate. The alternative joins a rule row instead of filtering directly. Verification reads the changed columns inside a rolled-back transaction.',
   'computed', 'update|multiple columns|beverages|list price|reorder level|write', 'multi-column UPDATE WHERE|UPDATE JOIN rule',
   'rollback', "SELECT ID, `List Price`, `Reorder Level` FROM products WHERE Category='Beverages' ORDER BY ID;"),
 S(5, 'Update all products with CASE: set Reorder Level to 40 for List Price at least 30, otherwise 10; set Target Level to twice the new Reorder Level.',
   'UPDATE products SET `Reorder Level`=CASE WHEN `List Price`>=30 THEN 40 ELSE 10 END, `Target Level`=CASE WHEN `List Price`>=30 THEN 80 ELSE 20 END;',
   'UPDATE products SET `Reorder Level`=IF(`List Price`>=30,40,10), `Target Level`=IF(`List Price`>=30,80,20);',
   'No WHERE means every product is updated. Each expression explicitly computes its final value, avoiding dependence on assignment order. NULL prices take the ELSE branch in both CASE and IF.',
   'computed', 'update|case|all products|reorder level|target level|write', 'CASE assignments|IF assignments',
   'rollback', 'SELECT ID, `Reorder Level`, `Target Level` FROM products ORDER BY ID;'),
 S(6, 'Update Condiments products: reduce List Price by 5 percent and set Discontinued to 1.',
   "UPDATE products SET `List Price`=`List Price`*0.95, Discontinued=1 WHERE Category='Condiments';",
   "UPDATE products p JOIN (SELECT 'Condiments' AS category) chosen ON chosen.category=p.Category SET p.`List Price`=p.`List Price`-p.`List Price`*0.05, p.Discontinued=1;",
   'Only the chosen category changes. Subtraction of the discount independently expresses the price reduction. The permanent catalogue is restored by rollback.',
   'computed', 'update|multiple columns|condiments|reduce price|discontinued|write', 'filtered multi-column UPDATE|UPDATE JOIN discount',
   'rollback', "SELECT ID, `List Price`, Discontinued FROM products WHERE Category='Condiments' ORDER BY ID;"),
 S(7, 'Update products ordered before March 2006: set Reorder Level to 50 using a subquery in WHERE.',
   "UPDATE products SET `Reorder Level`=50 WHERE ID IN (SELECT d.`Product ID` FROM `order details` d JOIN orders o ON o.`Order ID`=d.`Order ID` WHERE o.`Order Date`<'2006-03-01');",
   "UPDATE products p JOIN `order details` d ON d.`Product ID`=p.ID JOIN orders o ON o.`Order ID`=d.`Order ID` SET p.`Reorder Level`=50 WHERE o.`Order Date`<'2006-03-01';",
   'The subquery reads order tables, not the table being changed, so it avoids the target-table subquery restriction. A matching product is assigned once even if it has multiple qualifying lines. The join is the independent formulation.',
   'subquery', 'update|subquery|where in|orders|before march|write', 'UPDATE WHERE IN subquery|multi-table UPDATE JOIN',
   'rollback', 'SELECT ID, `Reorder Level` FROM products ORDER BY ID;'),
 S(8, 'Update products appearing on at least three distinct orders: set Target Level to 200 using UPDATE JOIN.',
   'UPDATE products p JOIN (SELECT `Product ID` FROM `order details` GROUP BY `Product ID` HAVING COUNT(DISTINCT `Order ID`)>=3) popular ON popular.`Product ID`=p.ID SET p.`Target Level`=200;',
   'UPDATE products p SET p.`Target Level`=200 WHERE (SELECT COUNT(DISTINCT d.`Order ID`) FROM `order details` d WHERE d.`Product ID`=p.ID)>=3;',
   'The derived table has one row per qualifying product. DISTINCT counts orders rather than detail lines. The alternative independently counts matching orders for each product.',
   'group_having', 'update join|popular products|at least three|distinct orders|write', 'UPDATE JOIN grouped source|correlated COUNT in UPDATE',
   'rollback', 'SELECT ID, `Target Level` FROM products ORDER BY ID;'),
 S(9, 'Update products never ordered: set Reorder Level to 0 using NOT EXISTS rather than changing Discontinued.',
   'UPDATE products p SET p.`Reorder Level`=0 WHERE NOT EXISTS (SELECT 1 FROM `order details` d WHERE d.`Product ID`=p.ID);',
   'UPDATE products p LEFT JOIN `order details` d ON d.`Product ID`=p.ID SET p.`Reorder Level`=0 WHERE d.ID IS NULL;',
   'This variant changes replenishment policy, not the discontinued flag. NOT EXISTS and the anti-join both preserve products with any order line. Rollback restores the original levels.',
   'not_exists', 'update|not exists|never ordered|reorder level|write', 'UPDATE NOT EXISTS|UPDATE LEFT anti-join',
   'rollback', 'SELECT ID, `Reorder Level` FROM products ORDER BY ID;'),
 S(10, 'Delete from a scratch copy zz_orders all orders placed before February 2006, leaving later orders intact.',
   "CREATE TABLE zz_orders AS SELECT * FROM orders; DELETE FROM zz_orders WHERE `Order Date`<'2006-02-01';",
   "CREATE TABLE zz_orders AS SELECT * FROM orders; DELETE z FROM zz_orders z JOIN orders o ON o.`Order ID`=z.`Order ID` WHERE o.`Order Date`<'2006-02-01';",
   'A date predicate limits the deletion. The joined alternative identifies keys from the untouched source. Creating a scratch copy isolates the demonstration from the real orders.',
   'date', 'delete|where|before february|orders|write', 'DELETE WHERE date|joined DELETE by source key',
   'ddl', 'SELECT `Order ID`, `Order Date` FROM zz_orders ORDER BY `Order ID`;', 'DROP TABLE IF EXISTS zz_orders;'),
 S(11, 'Delete products with no order details from a scratch product copy zz_products using NOT EXISTS.',
   'CREATE TABLE zz_products AS SELECT * FROM products; DELETE FROM zz_products WHERE NOT EXISTS (SELECT 1 FROM `order details` d WHERE d.`Product ID`=zz_products.ID);',
   'CREATE TABLE zz_products AS SELECT * FROM products; DELETE p FROM zz_products p LEFT JOIN `order details` d ON d.`Product ID`=p.ID WHERE d.ID IS NULL;',
   'Both anti-join forms remove only unsold products. A NULL product reference in a detail cannot poison NOT EXISTS, unlike NOT IN. The check reads surviving keys instead of assuming an affected-row count.',
   'not_exists', 'delete|not exists|unsold products|write', 'DELETE NOT EXISTS|DELETE LEFT anti-join',
   'ddl', 'SELECT ID FROM zz_products ORDER BY ID;', 'DROP TABLE IF EXISTS zz_products;'),
 S(12, 'Delete every row without WHERE from scratch shippers zz_shippers, keeping the table available for another insert.',
   "CREATE TABLE zz_shippers AS SELECT * FROM shippers; DELETE FROM zz_shippers; INSERT INTO zz_shippers (ID,Company) VALUES (99001,'After delete');",
   "CREATE TABLE zz_shippers AS SELECT * FROM shippers; DELETE z FROM zz_shippers z JOIN shippers s ON s.ID=z.ID; INSERT INTO zz_shippers (ID,Company) VALUES (99001,'After delete');",
   'DELETE without WHERE removes all rows, not the table definition. Reinserting a sentinel proves that the table still exists and avoids a vacuous empty verification result. The alternative deletes all original keys through a join.',
   'computed', 'delete|without where|all rows|shippers|write', 'unfiltered DELETE|joined key DELETE',
   'ddl', 'SELECT ID, Company FROM zz_shippers ORDER BY ID;', 'DROP TABLE IF EXISTS zz_shippers;'),
]

for number, values, keys in [(13, "(1,'Replacement')", '1'),
                             (14, "(2,'New carrier')", '2'),
                             (15, "(1,'Replacement'),(2,'New carrier')", '1,2')]:
    setup = "CREATE TABLE zz_replace (id INT PRIMARY KEY, company VARCHAR(50), note VARCHAR(30) DEFAULT 'default note') ENGINE=InnoDB; INSERT INTO zz_replace VALUES (1,'Original','old note'); "
    SQL7.append(S(number,
        'Use REPLACE INTO on zz_replace for %s; omit note so its default is used, and show the final rows.' %
        {13: 'existing key 1 with company Replacement', 14: 'new key 2 with company New carrier', 15: 'both existing key 1 and new key 2 in one statement'}[number],
        setup + 'REPLACE INTO zz_replace (id,company) VALUES ' + values + ';',
        setup + 'DELETE FROM zz_replace WHERE id IN (' + keys + '); INSERT INTO zz_replace (id,company) VALUES ' + values + ';',
        'REPLACE has delete-and-insert semantics on a conflicting primary or unique key. Omitted columns receive defaults rather than preserving previous values, unlike ON DUPLICATE KEY UPDATE when that column is not assigned. The explicit DELETE then INSERT alternative reproduces this scratch-table state; foreign keys, triggers and concurrent access require extra care on real tables.',
        'computed', 'replace into|insert|duplicate key|default|write', 'REPLACE INTO|explicit DELETE then INSERT',
        'ddl', 'SELECT id,company,note FROM zz_replace ORDER BY id;', 'DROP TABLE IF EXISTS zz_replace;'))

SQL7 += [
 S(16, 'Truncate a scratch AUTO_INCREMENT shipper table and insert a new carrier; demonstrate that the generated ID restarts, unlike plain DELETE.',
   "CREATE TABLE zz_truncate (id INT AUTO_INCREMENT PRIMARY KEY, company VARCHAR(50)) ENGINE=InnoDB; INSERT INTO zz_truncate (company) SELECT Company FROM shippers ORDER BY ID; TRUNCATE TABLE zz_truncate; INSERT INTO zz_truncate (company) VALUES ('After truncate');",
   "CREATE TABLE zz_truncate (id INT AUTO_INCREMENT PRIMARY KEY, company VARCHAR(50)) ENGINE=InnoDB; INSERT INTO zz_truncate (company) SELECT Company FROM shippers ORDER BY ID; DELETE FROM zz_truncate; ALTER TABLE zz_truncate AUTO_INCREMENT=1; INSERT INTO zz_truncate (company) VALUES ('After truncate');",
   'TRUNCATE empties the table, resets its generated-key counter and implicitly commits. Plain DELETE does not reset that counter; the alternative needs an explicit ALTER. Neither DDL script is rollback-safe, so only a disposable zz_ table is used.',
   'computed', 'truncate|delete|auto_increment|implicit commit|write', 'TRUNCATE reset|DELETE plus ALTER counter',
   'ddl', 'SELECT id,company FROM zz_truncate ORDER BY id;', 'DROP TABLE IF EXISTS zz_truncate;'),
 S(17, 'Create a stored function zz_full_name that returns Last Name, First Name with trailing spaces removed; call it for all employees.',
   module("CREATE FUNCTION zz_full_name(first_name VARCHAR(50), last_name VARCHAR(50)) RETURNS VARCHAR(103) DETERMINISTIC NO SQL BEGIN RETURN CONCAT(RTRIM(last_name),', ',RTRIM(first_name)); END") +
   'SELECT ID, zz_full_name(`First Name`,`Last Name`) FROM employees ORDER BY ID;',
   "SELECT ID, CONCAT(RTRIM(`Last Name`),', ',RTRIM(`First Name`)) FROM employees ORDER BY ID;",
   'The stored function is callable inside SELECT and declares DETERMINISTIC for binary-log safety. CONCAT propagates NULL names rather than silently inventing text. The direct expression independently checks the returned value; DELIMITER is a mysql client command, not server SQL.',
   'string_funcs', 'create function|full name|employees|delimiter|deterministic|write', 'stored name function|direct CONCAT expression',
   'ddl', '', 'DROP FUNCTION IF EXISTS zz_full_name;'),
 S(18, 'Create a stored function zz_price_band using IF: NULL price is Unknown, price at least 30 is High, otherwise Low; apply it to products.',
   module("CREATE FUNCTION zz_price_band(price DECIMAL(30,11)) RETURNS VARCHAR(7) DETERMINISTIC NO SQL BEGIN IF price IS NULL THEN RETURN 'Unknown'; ELSEIF price>=30 THEN RETURN 'High'; ELSE RETURN 'Low'; END IF; END") +
   'SELECT ID,zz_price_band(`List Price`) FROM products ORDER BY ID; SELECT zz_price_band(NULL),zz_price_band(30),zz_price_band(0);',
   "SELECT ID,CASE WHEN `List Price` IS NULL THEN 'Unknown' WHEN `List Price`>=30 THEN 'High' ELSE 'Low' END FROM products ORDER BY ID; SELECT 'Unknown','High','Low';",
   'IF separates the NULL case before comparing the threshold. A CASE expression is the independent alternative. Explicit boundary calls supplement the real data so both NULL and equality branches are exercised.',
   'computed', 'create function|if|price band|null|write', 'stored IF function|direct CASE classification',
   'ddl', '', 'DROP FUNCTION IF EXISTS zz_price_band;'),
 S(19, 'Create a stored function zz_order_total with READS SQL DATA returning discounted line revenue for an order, zero when missing; call it for all orders.',
   module('CREATE FUNCTION zz_order_total(order_key INT) RETURNS DECIMAL(30,4) READS SQL DATA BEGIN DECLARE amount DECIMAL(30,4); SELECT COALESCE(SUM(Quantity*`Unit Price`*(1-Discount)),0) INTO amount FROM `order details` WHERE `Order ID`=order_key; RETURN amount; END') +
   'SELECT `Order ID`,zz_order_total(`Order ID`) FROM orders ORDER BY `Order ID`; SELECT zz_order_total(-1);',
   'SELECT o.`Order ID`,CAST(COALESCE(SUM(d.Quantity*d.`Unit Price`*(1-d.Discount)),0) AS DECIMAL(30,4)) FROM orders o LEFT JOIN `order details` d ON d.`Order ID`=o.`Order ID` GROUP BY o.`Order ID` ORDER BY o.`Order ID`; SELECT CAST(0 AS DECIMAL(30,4));',
   'This function reads mutable tables, so READS SQL DATA is appropriate rather than claiming the result never changes. It sums discounted line amounts, excluding taxes and shipping. COALESCE defines missing or empty orders as zero, also tested with a missing key.',
   'aggregate', 'create function|reads sql data|order total|discount|write', 'stored aggregate function|LEFT JOIN grouped SUM',
   'ddl', '', 'DROP FUNCTION IF EXISTS zz_order_total;'),
 S(20, 'Create a BEFORE INSERT trigger on scratch zz_prices that normalizes negative or NULL prices to zero; leave positive prices unchanged.',
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB;\n' + module('CREATE TRIGGER zz_normalize BEFORE INSERT ON zz_prices FOR EACH ROW BEGIN IF NEW.price IS NULL OR NEW.price<0 THEN SET NEW.price=0; END IF; END'),
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB; CREATE TRIGGER zz_normalize BEFORE INSERT ON zz_prices FOR EACH ROW SET NEW.price=GREATEST(COALESCE(NEW.price,0),0);',
   'BEFORE INSERT may assign NEW.price before storage. IF and the null-aware GREATEST expression express the same normalization rule. The transactional probe includes negative, NULL and positive input; rollback removes the probe rows.',
   'computed', 'create trigger|before insert|normalize|price|null|write', 'trigger IF assignment|trigger GREATEST assignment',
   'ddl', 'START TRANSACTION; INSERT INTO zz_prices VALUES (1,-5),(2,NULL),(3,12.50); SELECT id,price FROM zz_prices ORDER BY id; ROLLBACK;',
   'DROP TRIGGER IF EXISTS zz_normalize; DROP TABLE IF EXISTS zz_prices;'),
 S(21, 'Create a BEFORE UPDATE trigger on scratch zz_prices that rejects negative or NULL prices with SIGNAL SQLSTATE 45000 and preserves the previous row.',
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB; INSERT INTO zz_prices VALUES (1,10);\n' +
   module("CREATE TRIGGER zz_validate BEFORE UPDATE ON zz_prices FOR EACH ROW BEGIN IF NEW.price IS NULL OR NEW.price<0 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Invalid price'; END IF; END"),
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB; INSERT INTO zz_prices VALUES (1,10);\n' +
   module("CREATE TRIGGER zz_validate BEFORE UPDATE ON zz_prices FOR EACH ROW BEGIN CASE WHEN NEW.price IS NOT NULL AND NEW.price>=0 THEN BEGIN END; ELSE SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Invalid price'; END CASE; END"),
   'SIGNAL rejects an invalid update rather than clamping it. A probe procedure catches only SQLSTATE 45000 and exposes whether each rejection actually occurred, then tests an allowed update. Its transaction is rolled back; cleanup drops both the trigger and probe procedure.',
   'computed', 'create trigger|before update|signal|45000|invalid price|write', 'IF guard with SIGNAL|CASE guard with SIGNAL',
   'ddl', module("CREATE PROCEDURE zz_probe() BEGIN DECLARE rejected INT DEFAULT 0; DECLARE CONTINUE HANDLER FOR SQLSTATE '45000' SET rejected=rejected+1; START TRANSACTION; UPDATE zz_prices SET price=-1 WHERE id=1; SELECT rejected,price FROM zz_prices WHERE id=1; UPDATE zz_prices SET price=NULL WHERE id=1; SELECT rejected,price FROM zz_prices WHERE id=1; UPDATE zz_prices SET price=15 WHERE id=1; SELECT rejected,price FROM zz_prices WHERE id=1; ROLLBACK; END") + 'CALL zz_probe();',
   'DROP PROCEDURE IF EXISTS zz_probe; DROP TRIGGER IF EXISTS zz_validate; DROP TABLE IF EXISTS zz_prices;'),
 S(22, 'Create an AFTER INSERT trigger on scratch zz_prices that logs each new row ID and price into zz_price_log.',
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB; CREATE TABLE zz_price_log (price_id INT,price DECIMAL(10,2)) ENGINE=InnoDB; CREATE TRIGGER zz_log AFTER INSERT ON zz_prices FOR EACH ROW INSERT INTO zz_price_log VALUES (NEW.id,NEW.price);',
   'CREATE TABLE zz_prices (id INT PRIMARY KEY,price DECIMAL(10,2)) ENGINE=InnoDB; CREATE TABLE zz_price_log (price_id INT,price DECIMAL(10,2)) ENGINE=InnoDB;\n' +
   module('CREATE TRIGGER zz_log AFTER INSERT ON zz_prices FOR EACH ROW BEGIN INSERT INTO zz_price_log (price_id,price) SELECT NEW.id,NEW.price; END'),
   'AFTER INSERT sees the values actually stored and writes one log row for each inserted row. Both scratch tables use InnoDB, so the transactional probe rolls back its source rows and its log rows together. The independent trigger uses INSERT SELECT rather than VALUES.',
   'computed', 'create trigger|after insert|audit log|write', 'AFTER trigger VALUES log|AFTER trigger SELECT log',
   'ddl', 'START TRANSACTION; INSERT INTO zz_prices VALUES (1,12.50),(2,0); SELECT price_id,price FROM zz_price_log ORDER BY price_id; ROLLBACK; SELECT COUNT(*) FROM zz_price_log;',
   'DROP TRIGGER IF EXISTS zz_log; DROP TABLE IF EXISTS zz_price_log; DROP TABLE IF EXISTS zz_prices;'),
 S(23, 'Create a procedure zz_employee_orders with an IN employee ID, then CALL it for employee 1 to list order IDs and dates.',
   module('CREATE PROCEDURE zz_employee_orders(IN employee_key INT) READS SQL DATA BEGIN SELECT `Order ID`,`Order Date` FROM orders WHERE `Employee ID`=employee_key ORDER BY `Order ID`; END') + 'CALL zz_employee_orders(1);',
   'SELECT o.`Order ID`,o.`Order Date` FROM employees e JOIN orders o ON o.`Employee ID`=e.ID WHERE e.ID=1 ORDER BY o.`Order ID`;',
   'IN is an input value supplied by CALL. The routine returns a result set rather than an OUT scalar. The independent join uses the employee key to select the same orders.',
   'select_filter', 'create procedure|in parameter|call|employee orders|write', 'IN procedure CALL|direct employee-order join',
   'ddl', '', 'DROP PROCEDURE IF EXISTS zz_employee_orders;'),
 S(24, 'Create a procedure zz_order_amount with IN order ID and OUT discounted revenue; CALL it for the smallest order ID and read the OUT variable.',
   module('CREATE PROCEDURE zz_order_amount(IN order_key INT, OUT amount DECIMAL(30,4)) READS SQL DATA BEGIN SELECT COALESCE(SUM(Quantity*`Unit Price`*(1-Discount)),0) INTO amount FROM `order details` WHERE `Order ID`=order_key; END') +
   'SET @order_key=(SELECT MIN(`Order ID`) FROM orders); CALL zz_order_amount(@order_key,@amount); SELECT @order_key,CAST(@amount AS DECIMAL(30,4));',
   'SELECT o.`Order ID`,CAST(COALESCE(SUM(d.Quantity*d.`Unit Price`*(1-d.Discount)),0) AS DECIMAL(30,4)) FROM orders o LEFT JOIN `order details` d ON d.`Order ID`=o.`Order ID` WHERE o.`Order ID`=(SELECT MIN(`Order ID`) FROM orders) GROUP BY o.`Order ID`;',
   'OUT writes the procedure result into a caller session variable, which is then selected explicitly. DECIMAL fixes the result scale. The alternative computes the same discounted revenue with a grouped join.',
   'aggregate', 'create procedure|in out|call|session variable|order total|write', 'OUT parameter SUM INTO|grouped LEFT JOIN sum',
   'ddl', '', 'DROP PROCEDURE IF EXISTS zz_order_amount;'),
 S(25, 'Create an IN procedure zz_employee_sales and CALL it for employee 2, returning that employee ID and total discounted order revenue including zero.',
   module('CREATE PROCEDURE zz_employee_sales(IN employee_key INT) READS SQL DATA BEGIN SELECT employee_key,CAST(COALESCE(SUM(d.Quantity*d.`Unit Price`*(1-d.Discount)),0) AS DECIMAL(30,4)) FROM orders o JOIN `order details` d ON d.`Order ID`=o.`Order ID` WHERE o.`Employee ID`=employee_key; END') + 'CALL zz_employee_sales(2);',
   'SELECT 2,CAST(COALESCE(SUM(t.amount),0) AS DECIMAL(30,4)) FROM (SELECT o.`Order ID`,SUM(d.Quantity*d.`Unit Price`*(1-d.Discount)) AS amount FROM orders o JOIN `order details` d ON d.`Order ID`=o.`Order ID` WHERE o.`Employee ID`=2 GROUP BY o.`Order ID`) t;',
   'The input parameter selects the responsible employee; an aggregate without GROUP BY returns a scalar even when no lines match. The independent query first totals each order and then sums those totals. Revenue excludes shipping and taxes.',
   'multi_agg', 'create procedure|in|call|employee sales|discount|write', 'IN procedure aggregate|two-stage order aggregation',
   'ddl', '', 'DROP PROCEDURE IF EXISTS zz_employee_sales;'),
]

for number, label, source, expression, predicate in [
        (26, 'sum List Price for Beverages products', 'products', '`List Price`', "Category='Beverages'"),
        (27, 'sum quantities on the smallest order ID', '`order details`', 'Quantity', '`Order ID`=(SELECT MIN(`Order ID`) FROM orders)'),
        (28, 'count employee 3 orders before March 2006', 'orders', '1', "`Employee ID`=3 AND `Order Date`<'2006-03-01'")]:
    query = 'SELECT COALESCE(%s,0) FROM %s WHERE %s' % (expression, source, predicate)
    SQL7.append(S(number,
        'Create a procedure zz_cursor_total using DECLARE CURSOR, FETCH and a NOT FOUND handler to %s; return the total with OUT and CALL it.' % label,
        module('CREATE PROCEDURE zz_cursor_total(OUT total DECIMAL(30,4)) READS SQL DATA BEGIN DECLARE finished INT DEFAULT 0; DECLARE value_read DECIMAL(30,4); DECLARE rows_cursor CURSOR FOR ' + query + '; DECLARE CONTINUE HANDLER FOR NOT FOUND SET finished=1; SET total=0; OPEN rows_cursor; read_loop: LOOP FETCH rows_cursor INTO value_read; IF finished=1 THEN LEAVE read_loop; END IF; SET total=total+value_read; END LOOP; CLOSE rows_cursor; END') +
        'CALL zz_cursor_total(@total); SELECT CAST(@total AS DECIMAL(30,4));',
        'SELECT CAST(COALESCE(SUM(COALESCE(%s,0)),0) AS DECIMAL(30,4)) FROM %s WHERE %s;' % (expression, source, predicate),
        'Variables are declared before the cursor, followed by the NOT FOUND handler. The loop tests the handler flag immediately after FETCH, preventing an extra addition after end-of-data. A set-based SUM is simpler for this task and independently checks the cursor result, including an empty source returning zero.',
        'aggregate', 'create procedure|cursor|fetch|not found|out|call|' + label + '|write', 'cursor accumulation with handler|set-based SUM',
        'ddl', '', 'DROP PROCEDURE IF EXISTS zz_cursor_total;'))

for number, action in [(29, 'RESTRICT'), (30, 'CASCADE'), (31, 'SET NULL')]:
    parent = 'CREATE TABLE zz_parent (id INT PRIMARY KEY) ENGINE=InnoDB; INSERT INTO zz_parent VALUES (1); '
    columns = "id INT NOT NULL AUTO_INCREMENT, parent_id INT, amount DECIMAL(10,2) NOT NULL DEFAULT 0, PRIMARY KEY (id)"
    constraints = ', CONSTRAINT zz_amount CHECK (amount>=0), CONSTRAINT zz_parent_fk FOREIGN KEY (parent_id) REFERENCES zz_parent(id) ON DELETE ' + action
    finish = "INSERT INTO zz_child (parent_id) VALUES (1); INSERT INTO zz_child (parent_id,amount) VALUES (NULL,12.50); "
    if action != 'RESTRICT':
        finish += 'DELETE FROM zz_parent WHERE id=1; '
    check = ('SELECT id,parent_id,amount FROM zz_child ORDER BY id; '
             "SELECT COLUMN_NAME,IS_NULLABLE,COLUMN_DEFAULT,EXTRA FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_child' ORDER BY ORDINAL_POSITION; "
             "SELECT CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_child' ORDER BY CONSTRAINT_TYPE; "
             "SELECT DELETE_RULE FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='zz_child';")
    SQL7.append(S(number,
        'Create scratch tables zz_parent and zz_child: child has AUTO_INCREMENT PRIMARY KEY, a nullable FOREIGN KEY with ON DELETE %s, nonnegative CHECK amount and DEFAULT 0; %s.' %
        (action, 'keep the referenced parent' if action == 'RESTRICT' else 'delete the referenced parent and show the child effect'),
        parent + 'CREATE TABLE zz_child (' + columns + constraints + ') ENGINE=InnoDB; ' + finish,
        parent + 'CREATE TABLE zz_child (' + columns + ') ENGINE=InnoDB; ALTER TABLE zz_child ADD CONSTRAINT zz_amount CHECK (amount>=0), ADD CONSTRAINT zz_parent_fk FOREIGN KEY (parent_id) REFERENCES zz_parent(id) ON DELETE ' + action + '; ' + finish,
        'Both tables are disposable InnoDB tables with matching integer key types. The foreign-key action is part of the schema contract, not just a data filter. The independent alternative adds constraints through ALTER; verification compares rows, column defaults, key types and the declared delete rule. CHECK is enforced by MySQL 8.0.28.',
        'computed', 'create table|primary key|auto_increment|foreign key|check|default|' + action.lower() + '|write', 'inline CREATE constraints|ALTER ADD constraints',
        'ddl', check, 'DROP TABLE IF EXISTS zz_child; DROP TABLE IF EXISTS zz_parent;'))

SQL7 += [
 S(32, 'Alter scratch shippers zz_schema to add Active TINYINT NOT NULL DEFAULT 1, preserving every existing shipper.',
   'CREATE TABLE zz_schema AS SELECT ID,Company FROM shippers; ALTER TABLE zz_schema ADD COLUMN Active TINYINT NOT NULL DEFAULT 1;',
   'CREATE TABLE zz_schema (ID INT NOT NULL, Company VARCHAR(50), Active TINYINT NOT NULL DEFAULT 1); INSERT INTO zz_schema (ID,Company) SELECT ID,Company FROM shippers;',
   'ALTER backfills existing rows with the explicit default. The independent definition-before-insert approach produces the same schema and data. Only the scratch table is altered.',
   'computed', 'alter table|add column|not null|default|shippers|write', 'ALTER ADD column|CREATE column before INSERT',
   'ddl', "SELECT ID,Company,Active FROM zz_schema ORDER BY ID; SELECT COLUMN_NAME,COLUMN_TYPE,IS_NULLABLE,COLUMN_DEFAULT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_schema' ORDER BY ORDINAL_POSITION;",
   'DROP TABLE IF EXISTS zz_schema;'),
 S(33, 'Alter a scratch shipper copy zz_schema to drop the Company column while retaining all IDs.',
   'CREATE TABLE zz_schema AS SELECT ID,Company FROM shippers; ALTER TABLE zz_schema DROP COLUMN Company;',
   'CREATE TABLE zz_schema AS SELECT ID FROM shippers;',
   'DROP COLUMN permanently removes that column and its data. The projected CTAS alternative independently creates only the requested surviving schema. Cleanup drops the scratch table rather than changing shippers.',
   'computed', 'alter table|drop column|shippers|write', 'ALTER DROP COLUMN|projected CTAS',
   'ddl', "SELECT ID FROM zz_schema ORDER BY ID; SELECT COLUMN_NAME,COLUMN_TYPE FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_schema' ORDER BY ORDINAL_POSITION;",
   'DROP TABLE IF EXISTS zz_schema;'),
 S(34, 'Alter scratch products zz_schema to add Replenish INT DEFAULT 0 and drop the copied Category column; retain IDs and product names.',
   'CREATE TABLE zz_schema AS SELECT ID,`Product Name`,Category FROM products; ALTER TABLE zz_schema ADD COLUMN Replenish INT DEFAULT 0, DROP COLUMN Category;',
   'CREATE TABLE zz_schema AS SELECT ID,`Product Name` FROM products; ALTER TABLE zz_schema ADD COLUMN Replenish INT DEFAULT 0;',
   'One ALTER may combine adding and dropping columns. The alternative projects out Category before adding Replenish. Verification compares the surviving data and actual column metadata.',
   'computed', 'alter table|add column|drop column|products|write', 'combined ADD DROP ALTER|projection then ADD ALTER',
   'ddl', "SELECT ID,`Product Name`,Replenish FROM zz_schema ORDER BY ID; SELECT COLUMN_NAME,COLUMN_TYPE,COLUMN_DEFAULT FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_schema' ORDER BY ORDINAL_POSITION;",
   'DROP TABLE IF EXISTS zz_schema;'),
 S(35, 'Add a named nonnegative CHECK constraint zz_nonnegative to scratch zz_constraint.amount, then insert a valid amount.',
   'CREATE TABLE zz_constraint (id INT PRIMARY KEY,amount DECIMAL(10,2) NOT NULL); ALTER TABLE zz_constraint ADD CONSTRAINT zz_nonnegative CHECK (amount>=0); INSERT INTO zz_constraint VALUES (1,12.50);',
   'CREATE TABLE zz_constraint (id INT PRIMARY KEY,amount DECIMAL(10,2) NOT NULL,CONSTRAINT zz_nonnegative CHECK (amount>=0)); INSERT INTO zz_constraint SELECT 1,12.50;',
   'A CHECK rejects false predicates but permits UNKNOWN; NOT NULL therefore separately forbids a missing amount. ALTER validates existing data before installing the rule. The inline definition is independent of the ALTER path.',
   'computed', 'alter table|add constraint|check|not null|write', 'ALTER ADD CHECK|inline CHECK definition',
   'ddl', "SELECT id,amount FROM zz_constraint; SELECT CONSTRAINT_NAME,CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_constraint' ORDER BY CONSTRAINT_NAME;",
   'DROP TABLE IF EXISTS zz_constraint;'),
 S(36, 'Drop a named CHECK constraint from scratch zz_constraint so a negative amount can subsequently be inserted.',
   'CREATE TABLE zz_constraint (id INT PRIMARY KEY,amount DECIMAL(10,2),CONSTRAINT zz_nonnegative CHECK (amount>=0)); ALTER TABLE zz_constraint DROP CHECK zz_nonnegative; INSERT INTO zz_constraint VALUES (1,-5);',
   'CREATE TABLE zz_constraint (id INT PRIMARY KEY,amount DECIMAL(10,2)); INSERT INTO zz_constraint SELECT 1,-5;',
   'DROP CHECK removes the constraint rather than the amount column. Inserting a negative value proves that the rule no longer blocks it. The independent alternative defines the final unconstrained schema directly.',
   'computed', 'alter table|drop constraint|drop check|negative|write', 'ALTER DROP CHECK|unconstrained CREATE',
   'ddl', "SELECT id,amount FROM zz_constraint; SELECT CONSTRAINT_TYPE FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='zz_constraint' ORDER BY CONSTRAINT_TYPE;",
   'DROP TABLE IF EXISTS zz_constraint;'),
 S(37, 'Drop the FOREIGN KEY zz_parent_fk from scratch zz_child while keeping parent_id, then allow an orphan parent ID.',
   'CREATE TABLE zz_parent (id INT PRIMARY KEY) ENGINE=InnoDB; CREATE TABLE zz_child (id INT PRIMARY KEY,parent_id INT,CONSTRAINT zz_parent_fk FOREIGN KEY (parent_id) REFERENCES zz_parent(id)) ENGINE=InnoDB; ALTER TABLE zz_child DROP FOREIGN KEY zz_parent_fk; INSERT INTO zz_child VALUES (1,999);',
   'CREATE TABLE zz_parent (id INT PRIMARY KEY) ENGINE=InnoDB; CREATE TABLE zz_child (id INT PRIMARY KEY,parent_id INT,KEY zz_parent_fk (parent_id)) ENGINE=InnoDB; INSERT INTO zz_child SELECT 1,999;',
   'DROP FOREIGN KEY takes the constraint name, not the column name. The supporting index may remain after removal, so the alternative explicitly adds that index as well. Verification checks both the orphan row and absence of the foreign-key rule.',
   'computed', 'alter table|drop foreign key|constraint|orphan|write', 'ALTER DROP FOREIGN KEY|CREATE without reference',
   'ddl', "SELECT id,parent_id FROM zz_child; SELECT COUNT(*) FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA=DATABASE() AND TABLE_NAME='zz_child';",
   'DROP TABLE IF EXISTS zz_child; DROP TABLE IF EXISTS zz_parent;'),
]

for number, ending, label in [(38, 'COMMIT', 'commit the transfer'), (39, 'ROLLBACK', 'roll back the entire transfer')]:
    setup = 'CREATE TABLE zz_accounts (id INT PRIMARY KEY,balance DECIMAL(10,2) NOT NULL,CHECK (balance>=0)) ENGINE=InnoDB; INSERT INTO zz_accounts VALUES (1,100),(2,50); '
    SQL7.append(S(number,
        'Start a transaction on scratch accounts with balances 100 and 50, transfer 25 from account 1 to account 2, then %s.' % label,
        setup + 'START TRANSACTION; SELECT id FROM zz_accounts WHERE id IN (1,2) ORDER BY id FOR UPDATE; UPDATE zz_accounts SET balance=balance-25 WHERE id=1; UPDATE zz_accounts SET balance=balance+25 WHERE id=2; ' + ending + ';',
        setup + 'START TRANSACTION; SELECT id FROM zz_accounts WHERE id IN (1,2) ORDER BY id FOR UPDATE; UPDATE zz_accounts SET balance=CASE id WHEN 1 THEN balance-25 WHEN 2 THEN balance+25 END WHERE id IN (1,2); ' + ending + ';',
        'Both accounts are locked in key order before either balance changes. The scratch setup guarantees the source exists and has sufficient funds; CHECK forbids negative balances. COMMIT persists both writes, whereas ROLLBACK undoes both. This answer owns its transaction and must never be wrapped in another START TRANSACTION.',
        'computed', 'start transaction|' + ending.lower() + '|transfer|accounts|write', 'two locked UPDATE statements|single CASE UPDATE',
        'ddl', 'SELECT id,balance FROM zz_accounts ORDER BY id;', 'DROP TABLE IF EXISTS zz_accounts;'))

SQL7 += [
 S(40, 'Use SAVEPOINT on scratch accounts: keep an initial transfer of 10, undo a later transfer of 200 that fails for insufficient funds, then COMMIT the initial transfer.',
   'CREATE TABLE zz_accounts (id INT PRIMARY KEY,balance DECIMAL(10,2) NOT NULL) ENGINE=InnoDB; INSERT INTO zz_accounts VALUES (1,100),(2,50);\n' +
   module("CREATE PROCEDURE zz_transfer() BEGIN DECLARE rejected INT DEFAULT 0; DECLARE CONTINUE HANDLER FOR SQLSTATE '45000' SET rejected=1; DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END; START TRANSACTION; SELECT id FROM zz_accounts WHERE id IN (1,2) ORDER BY id FOR UPDATE; UPDATE zz_accounts SET balance=balance-10 WHERE id=1; UPDATE zz_accounts SET balance=balance+10 WHERE id=2; SAVEPOINT second_transfer; UPDATE zz_accounts SET balance=balance+200 WHERE id=2; IF (SELECT balance FROM zz_accounts WHERE id=1)<200 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Insufficient funds'; END IF; IF rejected=1 THEN ROLLBACK TO SAVEPOINT second_transfer; ELSE UPDATE zz_accounts SET balance=balance-200 WHERE id=1; END IF; RELEASE SAVEPOINT second_transfer; COMMIT; SELECT rejected; END") + 'CALL zz_transfer();',
   'CREATE TABLE zz_accounts (id INT PRIMARY KEY,balance DECIMAL(10,2) NOT NULL) ENGINE=InnoDB; INSERT INTO zz_accounts VALUES (1,100),(2,50);\n' +
   module("CREATE PROCEDURE zz_transfer() BEGIN DECLARE rejected INT DEFAULT 0; DECLARE EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL; END; START TRANSACTION; SELECT id FROM zz_accounts WHERE id IN (1,2) ORDER BY id FOR UPDATE; UPDATE zz_accounts SET balance=balance+CASE id WHEN 1 THEN -10 ELSE 10 END WHERE id IN (1,2); SAVEPOINT second_transfer; BEGIN DECLARE EXIT HANDLER FOR SQLSTATE '45000' BEGIN ROLLBACK TO SAVEPOINT second_transfer; SET rejected=1; END; UPDATE zz_accounts SET balance=balance+200 WHERE id=2; IF (SELECT balance FROM zz_accounts WHERE id=1)<200 THEN SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Insufficient funds'; END IF; UPDATE zz_accounts SET balance=balance-200 WHERE id=1; END; RELEASE SAVEPOINT second_transfer; COMMIT; SELECT rejected; END") + 'CALL zz_transfer();',
   'This deliberately credits the second transfer before detecting insufficient funds, making partial rollback observable rather than a no-op. ROLLBACK TO undoes that credit but keeps the earlier transfer; COMMIT persists the surviving work. The alternative uses a scoped EXIT handler instead of a flag-controlled rollback. Unexpected SQL exceptions roll back the entire transaction and are rethrown. Production code should validate funds before crediting.',
   'computed', 'start transaction|savepoint|rollback|commit|insufficient funds|signal|write', 'CONTINUE handler partial rollback|scoped EXIT handler partial rollback',
   'ddl', 'SELECT id,balance FROM zz_accounts ORDER BY id;', 'DROP PROCEDURE IF EXISTS zz_transfer; DROP TABLE IF EXISTS zz_accounts;'),
 S(41, 'List every orders tax status ID and name with its number of orders, including unused tax statuses.',
   'SELECT s.ID,s.`Tax Status Name`,COUNT(o.`Order ID`) AS order_count FROM `orders tax status` s LEFT JOIN orders o ON o.`Tax Status`=s.ID GROUP BY s.ID,s.`Tax Status Name` ORDER BY s.ID;',
   'SELECT s.ID,s.`Tax Status Name`,(SELECT COUNT(*) FROM orders o WHERE o.`Tax Status`=s.ID) AS order_count FROM `orders tax status` s ORDER BY s.ID;',
   'Starting from the tax-status lookup retains unused definitions. Counting the optional order key produces zero rather than one for an unmatched status. The scalar subquery counts each status independently. All 48 orders in the supplied dump have NULL Tax Status, so both lookup counts are zero; that does not imply there are no orders.',
   'left_join', 'orders tax status|tax status name|order count|include unused', 'LEFT JOIN count|correlated scalar count'),
 S(42, 'List sales report titles, Group By and Display fields, with default reports first then titles alphabetically.',
   'SELECT Title,`Group By`,`Display`,`Default` FROM `sales reports` ORDER BY `Default` DESC,Title;',
   'SELECT r.Title,r.`Group By`,r.`Display`,r.`Default` FROM (SELECT Title,`Group By`,`Display`,`Default`,ROW_NUMBER() OVER (ORDER BY `Default` DESC,Title) AS position FROM `sales reports`) r ORDER BY r.position;',
   'Sales reports stores report definitions rather than sales transactions. Quoting protects identifiers such as Group By and Default. The window alternative assigns the same requested sort order before projection.',
   'order_limit', 'sales reports|title|group by|display|default report', 'direct metadata sort|ROW_NUMBER ordered projection'),
 S(43, 'List all privilege IDs and names alphabetically, including definitions not assigned to an employee.',
   'SELECT `Privilege ID`,`Privilege Name` FROM privileges ORDER BY `Privilege Name`,`Privilege ID`;',
   'WITH definitions AS (SELECT DISTINCT `Privilege ID`,`Privilege Name` FROM privileges) SELECT `Privilege ID`,`Privilege Name` FROM definitions ORDER BY `Privilege Name`,`Privilege ID`;',
   'The privilege lookup is the source of definitions, so no assignment join is needed to include unused privileges. DISTINCT in the CTE is safe because Privilege ID is a primary key. The final order includes the key as a tie-break.',
   'order_limit', 'privileges|privilege name|definitions|all', 'direct privilege lookup|CTE DISTINCT definitions'),
 S(44, 'List each order details status name with its number of order lines, keeping statuses with zero lines.',
   'SELECT s.`Status ID`,s.`Status Name`,COUNT(d.ID) AS line_count FROM `order details status` s LEFT JOIN `order details` d ON d.`Status ID`=s.`Status ID` GROUP BY s.`Status ID`,s.`Status Name` ORDER BY s.`Status ID`;',
   'SELECT s.`Status ID`,s.`Status Name`,COALESCE(t.line_count,0) FROM `order details status` s LEFT JOIN (SELECT `Status ID`,COUNT(*) AS line_count FROM `order details` GROUP BY `Status ID`) t ON t.`Status ID`=s.`Status ID` ORDER BY s.`Status ID`;',
   'This lookup describes line-level statuses, not whole-order statuses. LEFT JOIN keeps every definition and COUNT of the line key avoids counting a NULL padding row. The independent alternative aggregates detail lines before joining.',
   'left_join', 'order details status|status name|line count|include zero', 'LEFT JOIN line count|preaggregated status counts'),
]
