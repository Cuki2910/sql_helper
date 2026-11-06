"""Missing variants from the user's twelve practice questions; MySQL 8 syntax."""

ALIASES_SQL6 = {
    'MOCK-15': ["Find the pair or pairs of different products that appeared together in the greatest number of distinct orders. Display each unordered pair only once and include all pairs tied for the highest order count."],
    'VAR-030': ["Products with the three highest distinct non-NULL List Price values. Include every product tied at any of those three price levels, sorted by List Price descending then ID ascending."],
    'MOCK-07': ["Find all employees who processed the highest number of orders during 2006. Include every employee tied for the highest order count."],
    'SQL6-005': ['Categories with at least 5 products priced over 20, count and rounded average of those products.'],
    'SQL6-006': ['Categories having 2 or more products above 20 with their average price.'],
    'SQL6-007': ['Categories with at least 5 products overall whose average price over all their products exceeds 20.'],
    'SQL6-008': ["Products priced under their own category's average List Price."],
    'SQL6-009': ['Products that were never ordered: no row in order details.', 'Products for which no matching record exists in order details, regardless of price.'],
    'SQL6-010': ['Products not sold in 2006, including those never ordered at all.', 'Products absent from orders dated in 2006, even if purchased exclusively outside that year.'],
    'SQL6-011': ['Orders where shipping fee is over 20 percent of the order value, with the ratio.', 'Orders whose shipping charge exceeds one-fifth of total value, adding Unit Price multiplied by Quantity without deducting discounts. Omit nonpositive totals.'],
    'SQL6-012': ['Orders whose shipping fee is at most 5 percent of order value.'],
    'SQL6-013': ['Total shipping fees divided by total order value for 2006, one row.'],
    'SQL6-014': ['Mean of per-order shipping fee to order value ratios in 2006.'],
    'SQL6-015': ['Orders from April 2006 with the customer company and the employee full name, sorted by date.'],
    'SQL6-016': ['Orders between April and June 2006 with customer, employee and shipping company, including orders with no shipper.'],
    'SQL6-017': ['April 2006 orders that are still not shipped, showing customer company and employee name.'],
    'SQL6-018': ['Each employee with order count and total sales amount, also employees who never took an order, zero when none.'],
    'SQL6-019': ['Number of orders per employee in January to March 2006, showing employees with zero orders too.'],
    'SQL6-020': ['Orders with a shipping fee higher than the overall average fee and how far above it.'],
    'SQL6-021': ['Orders with a shipping fee lower than the overall average fee and how far below it.'],
    'SQL6-022': ['Orders whose shipping fee is at least double the overall average shipping fee.'],
    'SQL6-023': ['Row count of customer cities plus employee cities with UNION ALL versus UNION.'],
    'SQL6-024': ['Cities with more than one customer or employee living there, counted together.'],
    'SQL6-025': ['Cities that have both a customer and an employee, without INTERSECT.'],
    'SQL6-026': ['Employee label with first initial, last name and email name in brackets, longest last name first.'],
    'SQL6-027': ['Employees whose email user name before the at sign is longer than 5 characters, with its length.'],
    'SQL6-028': ['Per month number of orders placed and number not yet shipped.'],
    'SQL6-029': ['Per month share of orders that have not shipped, as a percentage with one decimal.'],
    'SQL6-030': ['Months where two or more orders have not been shipped.'],
    'SQL6-031': ['Orders shipped more than two days after they were placed, with the number of days.'],
    'SQL6-032': ['Orders shipped late by more than 2 days or never shipped, with the days taken.'],
    'SQL6-033': ['Average shipping delay in days for each order month.'],
    'SQL6-034': ['All pairs of products that appear in the same order, each pair once, with how many orders.'],
    'SQL6-035': ['Which products are bought in the same order as product 43 and how often.'],
    'SQL6-036': ['Each customer with earliest and latest order dates, retaining customers without orders with NULL dates.'],
    'SQL6-037': ['Among customers who placed orders in 2006, count different orders and different products purchased without counting repeated detail rows twice.'],
    'SQL6-038': ['Products priced above the average List Price of their respective categories, sorted by category alphabetically then highest to lowest price.'],
    'SQL6-039': ['Identify products absent from all orders dated in 2006, retaining products never ordered and products purchased exclusively outside that year. Return ID, Product Name, and Category.'],
    'SQL6-040': ['Identify employees who handled orders for customers in at least four different cities during 2006, with the number of distinct customer cities as TotalCities.'],
    'SQL6-041': ['Identify customers who purchased products from exactly three different categories during 2006. Count each category once per customer regardless of products or orders.'],
    'SQL6-042': ['Employees who handled orders during 2006 exclusively for customers living in cities different from their own. Require at least one annual order and exclude NULL employee or customer cities.'],
    'SQL6-043': ['Product pairs that occurred together in three or more distinct orders placed during 2006. Show the smaller product ID first and count shared orders once per pair.'],
    'SQL6-044': ['For each employee and customer city, count distinct customers served. Keep employee-city groups with at least two customers, excluding NULL cities and ignoring repeated orders.'],
}


def S(number, question, sql, alt, explanation, pattern, tags, techniques, cmp='set'):
    return dict(id='SQL6-%03d' % number, question=question, sql=sql, alt=alt,
                explanation=explanation, pattern=pattern, tags=tags.split('|'),
                techniques=techniques.split('|'), difficulty=3, cmp=cmp)


SQL6 = [
    S(1, "For each customer, calculate TotalOrderValue and TotalShippingFee for orders placed during 2006. Calculate each order's value as the sum of Unit Price multiplied by Quantity, without applying discounts. Count each order's Shipping Fee only once. Return customer ID, First Name, Last Name, TotalOrderValue, TotalShippingFee, and ShippingRatio. Include only customers with a positive TotalOrderValue whose TotalShippingFee exceeds 15% of TotalOrderValue. Round ShippingRatio to 4 decimal places.",
      """SELECT c.ID, c.`First Name`, c.`Last Name`,
       SUM(v.OrderValue) AS TotalOrderValue,
       SUM(o.`Shipping Fee`) AS TotalShippingFee,
       ROUND(SUM(o.`Shipping Fee`) / SUM(v.OrderValue), 4) AS ShippingRatio
FROM customers c
JOIN orders o ON o.`Customer ID` = c.ID
LEFT JOIN (
    SELECT `Order ID`, SUM(`Unit Price` * Quantity) AS OrderValue
    FROM `order details`
    GROUP BY `Order ID`
) v ON v.`Order ID` = o.`Order ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY c.ID, c.`First Name`, c.`Last Name`
HAVING SUM(v.OrderValue) > 0
   AND SUM(o.`Shipping Fee`) > 0.15 * SUM(v.OrderValue);""",
      """WITH fees AS (
    SELECT `Customer ID`, SUM(`Shipping Fee`) AS TotalShippingFee
    FROM orders
    WHERE `Order Date` >= '2006-01-01' AND `Order Date` < '2007-01-01'
    GROUP BY `Customer ID`
), amounts AS (
    SELECT o.`Customer ID`, SUM(d.`Unit Price` * d.Quantity) AS TotalOrderValue
    FROM orders o
    JOIN `order details` d ON d.`Order ID` = o.`Order ID`
    WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
    GROUP BY o.`Customer ID`
)
SELECT c.ID, c.`First Name`, c.`Last Name`, a.TotalOrderValue,
       f.TotalShippingFee, ROUND(f.TotalShippingFee / a.TotalOrderValue, 4) AS ShippingRatio
FROM customers c
JOIN fees f ON f.`Customer ID` = c.ID
JOIN amounts a ON a.`Customer ID` = c.ID
WHERE a.TotalOrderValue > 0 AND f.TotalShippingFee > 0.15 * a.TotalOrderValue;""",
      "Aggregate detail rows to one row per order before summing shipping fees per customer. Equal fees on different orders must both count: SUM(DISTINCT Shipping Fee) is not a fix. The LEFT JOIN also retains the fee of an order without details. Use gross Unit Price * Quantity, not discounts; filter the unrounded ratio and round only for display. SUM ignores NULL amounts and fees.",
      'multi_agg', 'customer shipping ratio|2006|15 percent|two level aggregation|avoid duplicate shipping|gross order value',
      'per-order aggregation before customer totals|independent customer fee and value aggregates'),
    S(2, "Using inventory transactions, find products whose total quantity sold exceeds 100 within an individual month of 2006. Include only transactions whose transaction type is 'Sold', and use Transaction Created Date for filtering and grouping. Return Month in YYYY-MM format, Product ID, Product Name, and TotalQuantity. Sort by Month ascending, then TotalQuantity descending.",
      """SELECT DATE_FORMAT(it.`Transaction Created Date`, '%Y-%m') AS Month,
       it.`Product ID`, p.`Product Name`, SUM(it.Quantity) AS TotalQuantity
FROM `inventory transactions` it
JOIN `inventory transaction types` tt ON tt.ID = it.`Transaction Type`
JOIN products p ON p.ID = it.`Product ID`
WHERE tt.`Type Name` = 'Sold'
  AND it.`Transaction Created Date` >= '2006-01-01'
  AND it.`Transaction Created Date` < '2007-01-01'
GROUP BY Month, it.`Product ID`, p.`Product Name`
HAVING SUM(it.Quantity) > 100
ORDER BY Month, TotalQuantity DESC, it.`Product ID`;""",
      """SELECT v.Month, p.ID AS `Product ID`, p.`Product Name`, v.TotalQuantity
FROM (
    SELECT CONCAT(YEAR(it.`Transaction Created Date`), '-',
                  LPAD(MONTH(it.`Transaction Created Date`), 2, '0')) AS Month,
           it.`Product ID`, SUM(it.Quantity) AS TotalQuantity
    FROM `inventory transactions` it
    WHERE YEAR(it.`Transaction Created Date`) = 2006
      AND EXISTS (SELECT 1 FROM `inventory transaction types` tt
                  WHERE tt.ID = it.`Transaction Type` AND tt.`Type Name` = 'Sold')
    GROUP BY Month, it.`Product ID`
) v
JOIN products p ON p.ID = v.`Product ID`
WHERE v.TotalQuantity > 100
ORDER BY v.Month, v.TotalQuantity DESC, p.ID;""",
      "WHERE selects Sold transactions created in 2006, then GROUP BY forms one group per month and product. HAVING filters monthly SUM(Quantity) strictly above 100, not annual quantity or transaction count. Look up Sold by Type Name rather than assuming its numeric ID. Product ID breaks any remaining sort ties.",
      'group_having', 'monthly sold quantity|inventory transactions|transaction created date|2006|having sum|over 100',
      'monthly GROUP BY with HAVING|derived monthly totals with EXISTS type lookup', 'ordered'),
    S(3, "Find employees who processed at least one order during 2006 but did not process any orders during that year for customers based in the same city as the employee. Return employee ID, First Name, and Last Name. Orders outside 2006 must not affect either condition. Sort by employee ID ascending.",
      """SELECT e.ID, e.`First Name`, e.`Last Name`
FROM employees e
WHERE EXISTS (
    SELECT 1 FROM orders o
    WHERE o.`Employee ID` = e.ID
      AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
)
AND NOT EXISTS (
    SELECT 1 FROM orders o
    JOIN customers c ON c.ID = o.`Customer ID`
    WHERE o.`Employee ID` = e.ID AND c.City = e.City
      AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
)
ORDER BY e.ID;""",
      """SELECT e.ID, e.`First Name`, e.`Last Name`
FROM employees e
JOIN orders o ON o.`Employee ID` = e.ID
LEFT JOIN customers c ON c.ID = o.`Customer ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY e.ID, e.`First Name`, e.`Last Name`, e.City
HAVING SUM(CASE WHEN c.City = e.City THEN 1 ELSE 0 END) = 0
ORDER BY e.ID;""",
      "EXISTS requires activity in 2006; NOT EXISTS rejects any same-city customer order in that same year. Repeat the date range in both subqueries so older or newer orders cannot change either condition. City equality uses ordinary SQL =, so a NULL city does not establish a same-city match. Filtering individual rows by different cities would wrongly retain employees who also have same-city orders.",
      'not_exists', 'employee active in 2006|same city|never during year|exists and not exists|date scope',
      'correlated EXISTS and NOT EXISTS|conditional aggregation after annual order join', 'ordered'),
    S(4, "Find customers who placed at least 3 distinct orders during 2006 and purchased products from more than 3 distinct categories across those orders. Return customer ID, First Name, Last Name, TotalOrders, and TotalCategories. Count each order only once even if it contains multiple order detail rows. Sort by TotalCategories descending, then TotalOrders descending, then customer ID ascending.",
      """SELECT c.ID, c.`First Name`, c.`Last Name`,
       COUNT(DISTINCT o.`Order ID`) AS TotalOrders,
       COUNT(DISTINCT p.Category) AS TotalCategories
FROM customers c
JOIN orders o ON o.`Customer ID` = c.ID
LEFT JOIN `order details` d ON d.`Order ID` = o.`Order ID`
LEFT JOIN products p ON p.ID = d.`Product ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY c.ID, c.`First Name`, c.`Last Name`
HAVING COUNT(DISTINCT o.`Order ID`) >= 3 AND COUNT(DISTINCT p.Category) > 3
ORDER BY TotalCategories DESC, TotalOrders DESC, c.ID;""",
      """WITH annual_orders AS (
    SELECT `Order ID`, `Customer ID` FROM orders
    WHERE `Order Date` >= '2006-01-01' AND `Order Date` < '2007-01-01'
), order_counts AS (
    SELECT `Customer ID`, COUNT(*) AS TotalOrders FROM annual_orders
    GROUP BY `Customer ID`
), category_counts AS (
    SELECT o.`Customer ID`, COUNT(DISTINCT p.Category) AS TotalCategories
    FROM annual_orders o
    JOIN `order details` d ON d.`Order ID` = o.`Order ID`
    JOIN products p ON p.ID = d.`Product ID`
    GROUP BY o.`Customer ID`
)
SELECT c.ID, c.`First Name`, c.`Last Name`, o.TotalOrders, p.TotalCategories
FROM customers c
JOIN order_counts o ON o.`Customer ID` = c.ID
JOIN category_counts p ON p.`Customer ID` = c.ID
WHERE o.TotalOrders >= 3 AND p.TotalCategories > 3
ORDER BY p.TotalCategories DESC, o.TotalOrders DESC, c.ID;""",
      "Count distinct order IDs and distinct product categories independently after the joins. The category requirement applies across the customer's annual orders, not separately to every order. LEFT JOIN retains orders without details or valid categories in TotalOrders; COUNT(DISTINCT Category) ignores NULL. Apply >= 3 to orders but > 3 to categories, within 2006 only.",
      'multi_agg', 'customers|2006|at least 3 orders|more than 3 categories|count distinct orders|count distinct categories',
      'two COUNT(DISTINCT) measures after LEFT JOIN|separate annual order and category aggregates', 'ordered'),
    S(5, 'Find product categories containing at least 5 products with List Price greater than 20. Return Category, TotalProducts, and AveragePrice rounded to 2 decimal places. Sort by TotalProducts descending.',
      'SELECT Category, COUNT(*) AS TotalProducts, ROUND(AVG(`List Price`), 2) AS AveragePrice FROM products WHERE `List Price` > 20 GROUP BY Category HAVING COUNT(*) >= 5 ORDER BY TotalProducts DESC, Category;',
      'SELECT Category, TotalProducts, ROUND(PriceSum / TotalProducts, 2) AS AveragePrice FROM (SELECT Category, COUNT(*) AS TotalProducts, SUM(`List Price`) AS PriceSum FROM products WHERE `List Price` > 20 GROUP BY Category) t WHERE TotalProducts >= 5 ORDER BY TotalProducts DESC, Category;',
      'Reading A: the price condition filters rows first (WHERE), so both TotalProducts and AveragePrice describe only products above 20, and the count threshold is tested on those (HAVING). EMPTY RESULT in this dump: no category has 5 products above 20 (the most is 3), so this is a pattern reference; compare SQL6-006 (threshold 2) and SQL6-007 (reading B: count all products, filter on the average). Category is added as the last sort key so tied counts come back in a fixed order.',
      'group_having', 'price filter before grouping|category|count having|average|where vs having',
      'WHERE then HAVING COUNT|derived table with SUM and COUNT', 'ordered'),
    S(6, 'Find product categories containing at least 2 products with List Price greater than 20. Return Category, TotalProducts, and AveragePrice rounded to 2 decimal places. Sort by TotalProducts descending.',
      'SELECT Category, COUNT(*) AS TotalProducts, ROUND(AVG(`List Price`), 2) AS AveragePrice FROM products WHERE `List Price` > 20 GROUP BY Category HAVING COUNT(*) >= 2 ORDER BY TotalProducts DESC, Category;',
      'SELECT Category, TotalProducts, ROUND(PriceSum / TotalProducts, 2) AS AveragePrice FROM (SELECT Category, COUNT(*) AS TotalProducts, SUM(`List Price`) AS PriceSum FROM products WHERE `List Price` > 20 GROUP BY Category) t WHERE TotalProducts >= 2 ORDER BY TotalProducts DESC, Category;',
      'Threshold variant of SQL6-005 that returns rows: three categories have at least 2 products above 20. The price filter is in WHERE, so the average covers only those qualifying products.',
      'group_having', 'price filter before grouping|category|count having|average|threshold variant',
      'WHERE then HAVING COUNT|derived table with SUM and COUNT', 'ordered'),
    S(7, 'Find product categories containing at least 5 products in total and average List Price greater than 20. Return Category, TotalProducts, and AveragePrice rounded to 2 decimal places. Calculate average using all products in each category. Sort by TotalProducts descending.',
      'SELECT Category, COUNT(*) AS TotalProducts, ROUND(AVG(`List Price`), 2) AS AveragePrice FROM products GROUP BY Category HAVING COUNT(*) >= 5 AND AVG(`List Price`) > 20 ORDER BY TotalProducts DESC, Category;',
      'SELECT Category, TotalProducts, ROUND(AvgPrice, 2) AS AveragePrice FROM (SELECT Category, COUNT(*) AS TotalProducts, AVG(`List Price`) AS AvgPrice FROM products GROUP BY Category) t WHERE TotalProducts >= 5 AND AvgPrice > 20 ORDER BY TotalProducts DESC, Category;',
      'Reading B, different from SQL6-005: nothing filters rows, so every product counts toward both the total and the average, and BOTH conditions are group conditions in HAVING. Moving `List Price` > 20 into WHERE would silently change the average and the count. The comparison uses the unrounded average. One category qualifies (Dried Fruit & Nuts: 5 products, average 23.95).',
      'group_having', 'all products in category|having two conditions|average|count|where vs having',
      'HAVING on COUNT and AVG|derived table then outer filter', 'ordered'),
    S(8, 'List products whose List Price is below the average List Price within their own category. Return ID, Product Name, Category, and List Price. Sort by Category ascending, List Price descending.',
      'SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p WHERE p.`List Price` < (SELECT AVG(q.`List Price`) FROM products q WHERE q.Category = p.Category) ORDER BY p.Category, p.`List Price` DESC, p.ID;',
      'SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p JOIN (SELECT Category, AVG(`List Price`) AS avg_price FROM products GROUP BY Category) a ON a.Category = p.Category WHERE p.`List Price` < a.avg_price ORDER BY p.Category, p.`List Price` DESC, p.ID;',
      'Opposite direction of the above-category-average pattern (VAR-088). The inner query is correlated on Category, so each product is compared with its own category average, not the table-wide one. The join version computes all category averages once. A category with one product never qualifies, because the product equals its own average. ID is added as the last sort key for ties.',
      'correlated', 'below category average|correlated subquery|own category|group average join',
      'correlated AVG subquery|join to grouped averages', 'ordered'),
    S(9, 'Find products that never appeared in any order details. Return ID, Product Name, Category, and List Price. Include products regardless of price. Sort by ID ascending.',
      'SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p WHERE NOT EXISTS (SELECT 1 FROM `order details` d WHERE d.`Product ID` = p.ID) ORDER BY p.ID;',
      'SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p LEFT JOIN `order details` d ON d.`Product ID` = p.ID WHERE d.ID IS NULL ORDER BY p.ID;',
      "Anti-join: keep products with no matching order-detail row. 'Regardless of price' means no price filter, so products with a NULL List Price stay in. NOT EXISTS is safe when the link column has NULLs, where NOT IN would return nothing. In the LEFT JOIN form test a column of the detail table that is never NULL in real rows (its own key), not the join column.",
      'not_exists', 'never ordered|anti join|products without order details|not exists',
      'NOT EXISTS|LEFT JOIN IS NULL', 'ordered'),
    S(10, 'Find products that did not appear in any orders placed during 2006. Return ID, Product Name, Category, and List Price. Sort by ID ascending.',
      "SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p WHERE NOT EXISTS (SELECT 1 FROM `order details` d JOIN orders o ON o.`Order ID` = d.`Order ID` WHERE d.`Product ID` = p.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01') ORDER BY p.ID;",
      "SELECT p.ID, p.`Product Name`, p.Category, p.`List Price` FROM products p LEFT JOIN (SELECT DISTINCT d.`Product ID` AS pid FROM `order details` d JOIN orders o ON o.`Order ID` = d.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01') x ON x.pid = p.ID WHERE x.pid IS NULL ORDER BY p.ID;",
      "Differs from SQL6-009: the year condition belongs inside the subquery, next to the join to orders, because the order date lives on the orders table. Putting the date test outside would turn it into 'never ordered at all'. Products never ordered in any year are included too. The half-open date range keeps an index on Order Date usable.",
      'not_exists', 'not ordered in year|anti join|2006|not exists with join',
      'NOT EXISTS with join to orders|LEFT JOIN to distinct 2006 products', 'ordered'),
    S(11, 'Find orders whose Shipping Fee is more than 20% of TotalValue. Calculate TotalValue as SUM(Unit Price * Quantity), without applying discounts. Return Order ID, TotalValue, Shipping Fee, and ShippingRatio rounded to 4 decimal places. Exclude orders with zero or negative TotalValue.',
      'SELECT o.`Order ID`, SUM(d.`Unit Price` * d.Quantity) AS TotalValue, o.`Shipping Fee`, ROUND(o.`Shipping Fee` / SUM(d.`Unit Price` * d.Quantity), 4) AS ShippingRatio FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` GROUP BY o.`Order ID`, o.`Shipping Fee` HAVING SUM(d.`Unit Price` * d.Quantity) > 0 AND o.`Shipping Fee` > 0.2 * SUM(d.`Unit Price` * d.Quantity);',
      'SELECT `Order ID`, TotalValue, `Shipping Fee`, ROUND(`Shipping Fee` / TotalValue, 4) AS ShippingRatio FROM (SELECT o.`Order ID`, o.`Shipping Fee`, SUM(d.`Unit Price` * d.Quantity) AS TotalValue FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` GROUP BY o.`Order ID`, o.`Shipping Fee`) t WHERE TotalValue > 0 AND `Shipping Fee` > 0.2 * TotalValue;',
      "TotalValue is an aggregate per order, so every condition on it goes in HAVING (or in an outer WHERE over a derived table); WHERE cannot see it. The zero-or-negative exclusion also protects the division. 'More than 20%' is Shipping Fee > 0.2 * TotalValue, not a comparison of the ratio against 20. Orders with no detail lines vanish from the inner join, which is right because their TotalValue is undefined. Two orders qualify in this dump (74 and 73).",
      'group_having', 'shipping fee ratio|order total|having on aggregate|division guard|no discount',
      'HAVING on SUM expression|derived table then outer WHERE', 'set'),
    S(12, 'Find orders whose Shipping Fee is at most 5% of TotalValue. Calculate TotalValue as SUM(Unit Price * Quantity), without applying discounts. Return Order ID, TotalValue, Shipping Fee, and ShippingRatio rounded to 4 decimal places. Exclude orders with zero or negative TotalValue.',
      'SELECT o.`Order ID`, SUM(d.`Unit Price` * d.Quantity) AS TotalValue, o.`Shipping Fee`, ROUND(o.`Shipping Fee` / SUM(d.`Unit Price` * d.Quantity), 4) AS ShippingRatio FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` GROUP BY o.`Order ID`, o.`Shipping Fee` HAVING SUM(d.`Unit Price` * d.Quantity) > 0 AND o.`Shipping Fee` <= 0.05 * SUM(d.`Unit Price` * d.Quantity);',
      'SELECT `Order ID`, TotalValue, `Shipping Fee`, ROUND(`Shipping Fee` / TotalValue, 4) AS ShippingRatio FROM (SELECT o.`Order ID`, o.`Shipping Fee`, SUM(d.`Unit Price` * d.Quantity) AS TotalValue FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` GROUP BY o.`Order ID`, o.`Shipping Fee`) t WHERE TotalValue > 0 AND `Shipping Fee` <= 0.05 * TotalValue;',
      "Variant of SQL6-011 with the comparison reversed and the percentage changed. 'At most' is <=, so an order exactly at 5% is kept. An order with a zero Shipping Fee passes this test, so the question does not exclude it.",
      'group_having', 'shipping fee ratio|order total|having on aggregate|at most|no discount',
      'HAVING on SUM expression|derived table then outer WHERE', 'set'),
    S(13, "For orders placed in 2006, calculate the overall shipping ratio as the sum of Shipping Fees divided by the sum of order values. Calculate each order's value as SUM(Unit Price * Quantity), without applying discounts. Include only orders with positive order value and non-NULL Shipping Fee. Count each order's Shipping Fee once. Return one row OverallShippingRatio rounded to 4 decimal places.",
      "SELECT ROUND(SUM(fee) / SUM(val), 4) AS OverallShippingRatio FROM (SELECT o.`Order ID`, o.`Shipping Fee` AS fee, SUM(d.`Unit Price` * d.Quantity) AS val FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND o.`Shipping Fee` IS NOT NULL GROUP BY o.`Order ID`, o.`Shipping Fee` HAVING SUM(d.`Unit Price` * d.Quantity) > 0) t;",
      "WITH v AS (SELECT `Order ID`, SUM(`Unit Price` * Quantity) AS val FROM `order details` GROUP BY `Order ID` HAVING SUM(`Unit Price` * Quantity) > 0) SELECT ROUND(SUM(o.`Shipping Fee`) / SUM(v.val), 4) AS OverallShippingRatio FROM orders o JOIN v ON v.`Order ID` = o.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND o.`Shipping Fee` IS NOT NULL;",
      'Ratio of totals: add the fees and the values first, then divide once. The order value is computed per order BEFORE joining it back to the fee, so each Shipping Fee is counted once; summing the fee directly over the joined detail lines would count it once per line. Both the positive-value and non-NULL-fee rules apply to the same set of orders in numerator and denominator. Result 0.0278 over 39 orders; compare SQL6-014, the average of per-order ratios, which is a different number.',
      'multi_agg', 'overall ratio|ratio of sums|fee counted once|fan out|2006',
      'derived table of per-order values|CTE of per-order values', 'set'),
    S(14, "For orders placed in 2006, calculate the average of each order's shipping ratio, where an order's ratio is its Shipping Fee divided by its order value. Calculate each order's value as SUM(Unit Price * Quantity), without applying discounts. Include only orders with positive order value and non-NULL Shipping Fee. Return one row AverageShippingRatio rounded to 4 decimal places.",
      "SELECT ROUND(AVG(fee / val), 4) AS AverageShippingRatio FROM (SELECT o.`Order ID`, o.`Shipping Fee` AS fee, SUM(d.`Unit Price` * d.Quantity) AS val FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND o.`Shipping Fee` IS NOT NULL GROUP BY o.`Order ID`, o.`Shipping Fee` HAVING SUM(d.`Unit Price` * d.Quantity) > 0) t;",
      "WITH v AS (SELECT `Order ID`, SUM(`Unit Price` * Quantity) AS val FROM `order details` GROUP BY `Order ID` HAVING SUM(`Unit Price` * Quantity) > 0) SELECT ROUND(SUM(o.`Shipping Fee` / v.val) / COUNT(*), 4) AS AverageShippingRatio FROM orders o JOIN v ON v.`Order ID` = o.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND o.`Shipping Fee` IS NOT NULL;",
      'Average of ratios: one ratio per order, then AVG, so every order weighs the same whatever its size. This differs from SQL6-013 (ratio of totals, where large orders dominate): 0.0768 here against 0.0278 there for the same 39 orders. Say which one the question asks for before choosing.',
      'multi_agg', 'average of ratios|per order ratio|2006|average vs ratio of sums',
      'AVG over per-order ratio|SUM divided by COUNT in CTE', 'set'),
    S(15, 'List the orders placed in April 2006 with Order ID, Order Date, customer Company, and the employee full name (First Name and Last Name joined with a space). Sort by Order Date ascending, then Order ID.',
      """SELECT o.`Order ID`, o.`Order Date`, c.Company, CONCAT(e.`First Name`, ' ', e.`Last Name`) AS Employee
FROM orders o
JOIN customers c ON c.ID = o.`Customer ID`
JOIN employees e ON e.ID = o.`Employee ID`
WHERE o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-05-01'
ORDER BY o.`Order Date`, o.`Order ID`;""",
      """SELECT o.`Order ID`, o.`Order Date`,
       (SELECT c.Company FROM customers c WHERE c.ID = o.`Customer ID`) AS Company,
       (SELECT CONCAT(e.`First Name`, ' ', e.`Last Name`) FROM employees e WHERE e.ID = o.`Employee ID`) AS Employee
FROM orders o
WHERE o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-05-01'
ORDER BY o.`Order Date`, o.`Order ID`;""",
      'Three-table join: orders to customers and to employees through their foreign keys. Order Date can carry a time of day, so the month is a half-open range on the bare column; = on a date would miss rows and a function on the column blocks the index. 17 orders in this dump. April, not March: compare LAB-07.',
      'inner_join', 'three table join|orders in a month|customer and employee names|half open date range|april 2006',
      'JOIN orders to customers and employees|scalar subqueries per order', 'ordered'),
    S(16, 'List the orders placed from April to June 2006 with Order ID, Order Date, customer Company, employee full name, and the shipper Company. Keep orders that have no shipper (show NULL). Sort by Order Date, then Order ID.',
      """SELECT o.`Order ID`, o.`Order Date`, c.Company, CONCAT(e.`First Name`, ' ', e.`Last Name`) AS Employee, s.Company AS Shipper
FROM orders o
JOIN customers c ON c.ID = o.`Customer ID`
JOIN employees e ON e.ID = o.`Employee ID`
LEFT JOIN shippers s ON s.ID = o.`Shipper ID`
WHERE o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-07-01'
ORDER BY o.`Order Date`, o.`Order ID`;""",
      """SELECT o.`Order ID`, o.`Order Date`,
       (SELECT c.Company FROM customers c WHERE c.ID = o.`Customer ID`) AS Company,
       (SELECT CONCAT(e.`First Name`, ' ', e.`Last Name`) FROM employees e WHERE e.ID = o.`Employee ID`) AS Employee,
       (SELECT s.Company FROM shippers s WHERE s.ID = o.`Shipper ID`) AS Shipper
FROM orders o
WHERE o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-07-01'
ORDER BY o.`Order Date`, o.`Order ID`;""",
      'Variant of SQL6-015: wider range and a fourth table. Shipper ID is NULL on some orders, so shippers is LEFT JOINed; an inner join would silently drop those orders. 33 orders, 3 of them without a shipper. The column is Company because shippers has no Shipper Name column.',
      'left_join', 'orders with shipper|keep orders without shipper|left join null|three month range|four table join',
      'LEFT JOIN shippers after inner joins|scalar subqueries return NULL when no match', 'ordered'),
    S(17, 'List the orders placed in April 2006 that have not shipped yet (Shipped Date is NULL). Return Order ID, Order Date, customer Company, and employee full name. Sort by Order ID.',
      """SELECT o.`Order ID`, o.`Order Date`, c.Company, CONCAT(e.`First Name`, ' ', e.`Last Name`) AS Employee
FROM orders o
JOIN customers c ON c.ID = o.`Customer ID`
JOIN employees e ON e.ID = o.`Employee ID`
WHERE o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-05-01' AND o.`Shipped Date` IS NULL
ORDER BY o.`Order ID`;""",
      """WITH april AS (
    SELECT `Order ID`, `Order Date`, `Customer ID`, `Employee ID` FROM orders
    WHERE `Order Date` >= '2006-04-01' AND `Order Date` < '2006-05-01' AND `Shipped Date` IS NULL
)
SELECT a.`Order ID`, a.`Order Date`, c.Company, CONCAT(e.`First Name`, ' ', e.`Last Name`) AS Employee
FROM april a
JOIN customers c ON c.ID = a.`Customer ID`
JOIN employees e ON e.ID = a.`Employee ID`
ORDER BY a.`Order ID`;""",
      'Variant of SQL6-015 with a NULL test: IS NULL, never = NULL. Orders 80 and 81 qualify in this dump.',
      'inner_join', 'three table join|not shipped|is null|april 2006|orders in a month',
      'IS NULL filter in WHERE|CTE filters first then joins', 'ordered'),
    S(18, 'For every employee, including employees with no orders, return employee ID, First Name, Last Name, TotalOrders, and TotalSales. Calculate TotalSales as SUM(Unit Price * Quantity) without discounts, show 0 when there are no sales, and round to 2 decimal places. Sort by TotalSales descending, then ID.',
      """SELECT e.ID, e.`First Name`, e.`Last Name`,
       COUNT(DISTINCT o.`Order ID`) AS TotalOrders,
       ROUND(COALESCE(SUM(d.`Unit Price` * d.Quantity), 0), 2) AS TotalSales
FROM employees e
LEFT JOIN orders o ON o.`Employee ID` = e.ID
LEFT JOIN `order details` d ON d.`Order ID` = o.`Order ID`
GROUP BY e.ID, e.`First Name`, e.`Last Name`
ORDER BY TotalSales DESC, e.ID;""",
      """SELECT e.ID, e.`First Name`, e.`Last Name`,
       (SELECT COUNT(*) FROM orders o WHERE o.`Employee ID` = e.ID) AS TotalOrders,
       ROUND(COALESCE((SELECT SUM(d.`Unit Price` * d.Quantity) FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` WHERE o.`Employee ID` = e.ID), 0), 2) AS TotalSales
FROM employees e
ORDER BY TotalSales DESC, e.ID;""",
      'Both joins are LEFT so an employee with no orders survives. Joining order details multiplies each order by its lines, so orders are counted with COUNT(DISTINCT order ID); COUNT(*) would count the NULL row as 1. COALESCE turns the NULL sum into 0. 9 rows; Steven Thorpe (ID 5) has 0 orders and 0.00 sales, Nancy Freehafer leads with 22255.25.',
      'left_join', 'all employees|including employees without orders|left join|count distinct|coalesce sum|total sales',
      'two LEFT JOINs with COUNT DISTINCT|correlated scalar subqueries', 'ordered'),
    S(19, 'For every employee, including those with none, count the orders placed in the first quarter of 2006 (January to March). Return ID, First Name, Last Name, and OrdersQ1. Sort by OrdersQ1 descending, then ID.',
      """SELECT e.ID, e.`First Name`, e.`Last Name`, COUNT(o.`Order ID`) AS OrdersQ1
FROM employees e
LEFT JOIN orders o ON o.`Employee ID` = e.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2006-04-01'
GROUP BY e.ID, e.`First Name`, e.`Last Name`
ORDER BY OrdersQ1 DESC, e.ID;""",
      """SELECT e.ID, e.`First Name`, e.`Last Name`, COALESCE(q.n, 0) AS OrdersQ1
FROM employees e
LEFT JOIN (SELECT `Employee ID`, COUNT(*) AS n FROM orders WHERE `Order Date` >= '2006-01-01' AND `Order Date` < '2006-04-01' GROUP BY `Employee ID`) q ON q.`Employee ID` = e.ID
ORDER BY OrdersQ1 DESC, e.ID;""",
      'Variant of SQL6-018: the date condition belongs in ON, not WHERE. In WHERE it would remove the NULL-extended rows and the employees with no orders in the quarter would vanish. COUNT(o.`Order ID`) on the right-hand column counts 0 for them. 9 rows; employees 2, 5 and 7 have 0.',
      'left_join', 'all employees|left join condition in on|zero counts|first quarter 2006|where vs on',
      'date test inside ON|LEFT JOIN to pre-aggregated derived table', 'ordered'),
    S(20, 'Find the orders whose Shipping Fee is above the average Shipping Fee of all orders. Return Order ID, Shipping Fee, and AboveAverage (fee minus the average, rounded to 2 decimal places). Sort by Shipping Fee descending, then Order ID.',
      """SELECT `Order ID`, `Shipping Fee`, ROUND(`Shipping Fee` - (SELECT AVG(`Shipping Fee`) FROM orders), 2) AS AboveAverage
FROM orders
WHERE `Shipping Fee` > (SELECT AVG(`Shipping Fee`) FROM orders)
ORDER BY `Shipping Fee` DESC, `Order ID`;""",
      """SELECT o.`Order ID`, o.`Shipping Fee`, ROUND(o.`Shipping Fee` - a.avg_fee, 2) AS AboveAverage
FROM orders o
CROSS JOIN (SELECT AVG(`Shipping Fee`) AS avg_fee FROM orders) a
WHERE o.`Shipping Fee` > a.avg_fee
ORDER BY o.`Shipping Fee` DESC, o.`Order ID`;""",
      'Scalar subquery: one value, the table-wide average (44.54 in this dump), so it is not correlated; compare SQL3-057, which uses the average of the same customer. The comparison uses the unrounded average. 14 rows. Order ID is the last sort key because many fees tie.',
      'subquery', 'above average shipping fee|scalar subquery|compare to overall average|difference from average',
      'scalar subquery in WHERE and SELECT|CROSS JOIN to one-row derived table', 'ordered'),
    S(21, 'Find the orders whose Shipping Fee is below the average Shipping Fee of all orders. Return Order ID, Shipping Fee, and BelowAverage (average minus fee, rounded to 2 decimal places). Sort by Shipping Fee ascending, then Order ID.',
      """SELECT `Order ID`, `Shipping Fee`, ROUND((SELECT AVG(`Shipping Fee`) FROM orders) - `Shipping Fee`, 2) AS BelowAverage
FROM orders
WHERE `Shipping Fee` < (SELECT AVG(`Shipping Fee`) FROM orders)
ORDER BY `Shipping Fee`, `Order ID`;""",
      """SELECT o.`Order ID`, o.`Shipping Fee`, ROUND(a.avg_fee - o.`Shipping Fee`, 2) AS BelowAverage
FROM orders o
CROSS JOIN (SELECT AVG(`Shipping Fee`) AS avg_fee FROM orders) a
WHERE o.`Shipping Fee` < a.avg_fee
ORDER BY o.`Shipping Fee`, o.`Order ID`;""",
      'Direction variant of SQL6-020. 34 rows, many of them with Shipping Fee 0; no fee is NULL here, but a NULL fee would fail the comparison and drop out.',
      'subquery', 'below average shipping fee|scalar subquery|compare to overall average',
      'scalar subquery in WHERE and SELECT|CROSS JOIN to one-row derived table', 'ordered'),
    S(22, 'Find the orders whose Shipping Fee is at least twice the average Shipping Fee of all orders. Return Order ID, Shipping Fee, and Multiple (fee divided by the average, rounded to 2 decimal places). Sort by Shipping Fee descending, then Order ID.',
      """SELECT `Order ID`, `Shipping Fee`, ROUND(`Shipping Fee` / (SELECT AVG(`Shipping Fee`) FROM orders), 2) AS Multiple
FROM orders
WHERE `Shipping Fee` >= 2 * (SELECT AVG(`Shipping Fee`) FROM orders)
ORDER BY `Shipping Fee` DESC, `Order ID`;""",
      """SELECT o.`Order ID`, o.`Shipping Fee`, ROUND(o.`Shipping Fee` / a.avg_fee, 2) AS Multiple
FROM orders o
JOIN (SELECT AVG(`Shipping Fee`) AS avg_fee FROM orders) a ON o.`Shipping Fee` >= 2 * a.avg_fee
ORDER BY o.`Shipping Fee` DESC, o.`Order ID`;""",
      'Threshold variant of SQL6-020: a multiple of the average instead of any amount above it. At least is >=, so a fee exactly at twice the average would be kept. 8 rows.',
      'subquery', 'twice the average|scalar subquery|multiple of average|shipping fee',
      'scalar subquery with multiplier|derived table in join condition', 'ordered'),
    S(23, 'Combine the City column of customers and employees. Return the number of rows when duplicates are kept (UNION ALL) as AllRows, and the number of rows when duplicates are removed (UNION) as DistinctRows.',
      """SELECT (SELECT COUNT(*) FROM (SELECT City FROM customers UNION ALL SELECT City FROM employees) a) AS AllRows,
       (SELECT COUNT(*) FROM (SELECT City FROM customers UNION SELECT City FROM employees) d) AS DistinctRows;""",
      """WITH x AS (SELECT City FROM customers UNION ALL SELECT City FROM employees)
SELECT COUNT(*) AS AllRows, COUNT(DISTINCT City) AS DistinctRows FROM x;""",
      'UNION ALL keeps every row: 29 customers + 9 employees = 38. UNION removes duplicate rows across the whole result: 19 distinct cities. UNION ALL is cheaper because it skips the duplicate removal. COUNT(DISTINCT City) gives the same 19 only because no City is NULL; UNION would keep one NULL row.',
      'set_ops', 'union vs union all|combine cities|duplicates kept|row counts',
      'UNION ALL and UNION in derived tables|UNION ALL once then COUNT DISTINCT', 'set'),
    S(24, 'For every city that appears among customers and employees combined, return City and People (customers plus employees living there). Keep only cities with more than one person. Sort by People descending, then City.',
      """SELECT City, COUNT(*) AS People
FROM (SELECT City FROM customers UNION ALL SELECT City FROM employees) t
GROUP BY City
HAVING COUNT(*) > 1
ORDER BY People DESC, City;""",
      """SELECT x.City,
       (SELECT COUNT(*) FROM customers c WHERE c.City = x.City) + (SELECT COUNT(*) FROM employees e WHERE e.City = x.City) AS People
FROM (SELECT City FROM customers UNION SELECT City FROM employees) x
WHERE (SELECT COUNT(*) FROM customers c WHERE c.City = x.City) + (SELECT COUNT(*) FROM employees e WHERE e.City = x.City) > 1
ORDER BY People DESC, x.City;""",
      'Needs UNION ALL, not UNION: UNION would collapse the duplicates first and every city would count 1. Group the stacked list and filter the groups in HAVING. Seattle has the most people (6).',
      'set_ops', 'union all then group|people per city|customers and employees|having count',
      'UNION ALL then GROUP BY HAVING|distinct city list with correlated counts', 'ordered'),
    S(25, 'Find the cities where both a customer and an employee are located. Return each City once.',
      """SELECT DISTINCT c.City
FROM customers c
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.City = c.City);""",
      """SELECT City FROM customers WHERE City IN (SELECT City FROM employees) GROUP BY City;""",
      'Intersection of two city lists. INTERSECT does not exist before MySQL 8.0.31, so use EXISTS or IN. DISTINCT matters: several customers can share the city. Only Seattle qualifies in this dump.',
      'exists', 'cities in both tables|intersect replacement|customers and employees same city|exists',
      'EXISTS with DISTINCT|IN subquery with GROUP BY', 'set'),
    S(26, "Show each employee as a label like N. Freehafer (nancy): first initial, a dot and a space, the last name, then the part of the E-mail Address before the @ in parentheses. Return EmployeeLabel. Sort by the length of the last name descending, then Last Name.",
      """SELECT CONCAT(LEFT(`First Name`, 1), '. ', `Last Name`, ' (', SUBSTRING_INDEX(`E-mail Address`, '@', 1), ')') AS EmployeeLabel
FROM employees
ORDER BY CHAR_LENGTH(`Last Name`) DESC, `Last Name`;""",
      """SELECT CONCAT(SUBSTRING(`First Name`, 1, 1), '. ', `Last Name`, ' (', SUBSTRING(`E-mail Address`, 1, LOCATE('@', `E-mail Address`) - 1), ')') AS EmployeeLabel
FROM employees
ORDER BY CHAR_LENGTH(`Last Name`) DESC, `Last Name`;""",
      "String building with CONCAT. LEFT(s, 1) is the initial; SUBSTRING_INDEX(email, '@', 1) is everything before the first @. Sort on CHAR_LENGTH (characters), not LENGTH (bytes). CONCAT returns NULL if any argument is NULL. 9 rows; A. Hellung-Larsen (anne) is first.",
      'string_funcs', 'concat|left|substring index|email before at|char length sort',
      'LEFT with SUBSTRING_INDEX|SUBSTRING with LOCATE', 'ordered'),
    S(27, "Return each employee's ID, the part of the E-mail Address before the @ as UserName, and its length as NameLength, only for user names longer than 5 characters. Sort by NameLength descending, then ID.",
      """SELECT ID, SUBSTRING_INDEX(`E-mail Address`, '@', 1) AS UserName, CHAR_LENGTH(SUBSTRING_INDEX(`E-mail Address`, '@', 1)) AS NameLength
FROM employees
WHERE CHAR_LENGTH(SUBSTRING_INDEX(`E-mail Address`, '@', 1)) > 5
ORDER BY NameLength DESC, ID;""",
      """SELECT ID, u AS UserName, CHAR_LENGTH(u) AS NameLength
FROM (SELECT ID, SUBSTRING(`E-mail Address`, 1, LOCATE('@', `E-mail Address`) - 1) AS u FROM employees) t
WHERE CHAR_LENGTH(u) > 5
ORDER BY NameLength DESC, ID;""",
      'Variant of SQL6-026: filter on the length of the extracted part. The alias cannot be used in WHERE, so the expression is repeated, or computed once in a derived table. LOCATE returns the position of the @, 0 if absent.',
      'string_funcs', 'email user name|char length filter|substring index|string length',
      'repeat the string expression in WHERE|derived table computes it once', 'ordered'),
    S(28, 'For each month of Order Date (format YYYY-MM), return the number of orders placed as OrdersPlaced and the number not yet shipped (Shipped Date is NULL) as NotShipped. Sort by month.',
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, COUNT(*) AS OrdersPlaced, SUM(`Shipped Date` IS NULL) AS NotShipped
FROM orders
GROUP BY Month
ORDER BY Month;""",
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, COUNT(*) AS OrdersPlaced, COUNT(*) - COUNT(`Shipped Date`) AS NotShipped
FROM orders
GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')
ORDER BY Month;""",
      'Conditional counting. In MySQL a condition is 1 or 0, so SUM(`Shipped Date` IS NULL) counts the NULLs. COUNT(column) skips NULLs, so COUNT(*) - COUNT(`Shipped Date`) gives the same number. 6 months; not shipped: March 3, April 2, May 4.',
      'cond_agg', 'orders per month|not shipped|sum of condition|count minus count column|date format',
      'SUM of a boolean condition|COUNT(*) minus COUNT(column)', 'ordered'),
    S(29, 'For each month of Order Date (format YYYY-MM), return the percentage of orders not yet shipped (Shipped Date is NULL) as PercentNotShipped, rounded to 1 decimal place. Sort by month.',
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, ROUND(100 * SUM(`Shipped Date` IS NULL) / COUNT(*), 1) AS PercentNotShipped
FROM orders
GROUP BY Month
ORDER BY Month;""",
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, ROUND(100 * AVG(`Shipped Date` IS NULL), 1) AS PercentNotShipped
FROM orders
GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')
ORDER BY Month;""",
      'Variant of SQL6-028: a ratio instead of a count. The average of a 0/1 condition is the fraction that is 1, so AVG(cond) is a shorter way to write SUM(cond) / COUNT(*). March 37.5, April 11.8, May 50.0, the other months 0.0.',
      'cond_agg', 'percentage per month|not shipped|average of condition|date format',
      'SUM of condition divided by COUNT|AVG of a 0/1 condition', 'ordered'),
    S(30, 'List the months of Order Date (format YYYY-MM) in which at least 2 orders had not shipped (Shipped Date is NULL). Return Month and NotShipped. Sort by NotShipped descending, then Month.',
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, SUM(`Shipped Date` IS NULL) AS NotShipped
FROM orders
GROUP BY Month
HAVING SUM(`Shipped Date` IS NULL) >= 2
ORDER BY NotShipped DESC, Month;""",
      """SELECT Month, NotShipped
FROM (SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, COUNT(*) - COUNT(`Shipped Date`) AS NotShipped FROM orders GROUP BY DATE_FORMAT(`Order Date`, '%Y-%m')) t
WHERE NotShipped >= 2
ORDER BY NotShipped DESC, Month;""",
      'Variant of SQL6-028: the count is a group condition, so it goes in HAVING (or in an outer WHERE over a derived table). 3 months qualify: May 4, March 3, April 2.',
      'cond_agg', 'months with not shipped orders|having on conditional sum|threshold',
      'HAVING on SUM of condition|derived table then outer WHERE', 'ordered'),
    S(31, 'Find the orders that were shipped more than 2 days after the order date. Return Order ID and DaysToShip (Shipped Date minus Order Date in days). Sort by DaysToShip descending, then Order ID.',
      """SELECT `Order ID`, DATEDIFF(`Shipped Date`, `Order Date`) AS DaysToShip
FROM orders
WHERE DATEDIFF(`Shipped Date`, `Order Date`) > 2
ORDER BY DaysToShip DESC, `Order ID`;""",
      """SELECT `Order ID`, TIMESTAMPDIFF(DAY, DATE(`Order Date`), DATE(`Shipped Date`)) AS DaysToShip
FROM orders
WHERE DATE(`Shipped Date`) > DATE(`Order Date`) + INTERVAL 2 DAY
ORDER BY DaysToShip DESC, `Order ID`;""",
      'DATEDIFF(later, earlier) returns whole days and ignores the time of day. A NULL Shipped Date gives NULL, which fails the comparison, so unshipped orders are excluded here; compare SQL6-032. 3 orders qualify (42 after 14 days, 30 after 7, and one after 3).',
      'date', 'datediff|days to ship|shipped late|more than 2 days',
      'DATEDIFF in SELECT and WHERE|TIMESTAMPDIFF with DATE and INTERVAL', 'ordered'),
    S(32, 'Find the orders that were shipped more than 2 days after the order date or have not shipped at all. Return Order ID, Order Date, Shipped Date, and DaysToShip. Sort by Order ID.',
      """SELECT `Order ID`, `Order Date`, `Shipped Date`, DATEDIFF(`Shipped Date`, `Order Date`) AS DaysToShip
FROM orders
WHERE DATEDIFF(`Shipped Date`, `Order Date`) > 2 OR `Shipped Date` IS NULL
ORDER BY `Order ID`;""",
      """SELECT `Order ID`, `Order Date`, `Shipped Date`, DATEDIFF(`Shipped Date`, `Order Date`) AS DaysToShip
FROM orders
WHERE COALESCE(DATEDIFF(`Shipped Date`, `Order Date`), 999) > 2
ORDER BY `Order ID`;""",
      'Variant of SQL6-031 that keeps the NULLs. Without the IS NULL branch the unshipped orders are lost, because NULL > 2 is not true. 12 rows: the 3 late orders and the 9 unshipped ones. DaysToShip is NULL for the unshipped.',
      'date', 'datediff|late or not shipped|is null with or|null handling',
      'OR with IS NULL|COALESCE to a large sentinel', 'ordered'),
    S(33, 'For each month of Order Date (format YYYY-MM), return the average number of days between Order Date and Shipped Date as AvgDaysToShip, rounded to 2 decimal places. Sort by month.',
      """SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, ROUND(AVG(DATEDIFF(`Shipped Date`, `Order Date`)), 2) AS AvgDaysToShip
FROM orders
GROUP BY Month
ORDER BY Month;""",
      """SELECT Month, ROUND(SUM(days) / COUNT(days), 2) AS AvgDaysToShip
FROM (SELECT DATE_FORMAT(`Order Date`, '%Y-%m') AS Month, DATEDIFF(`Shipped Date`, `Order Date`) AS days FROM orders) t
GROUP BY Month
ORDER BY Month;""",
      'Variant of SQL6-031 as an aggregate. AVG skips NULL, so unshipped orders do not count in the average; the alternative divides by COUNT(`Shipped Date`) to do the same. 6 months: January 2.50, February 1.67, March 4.00, and 0.00 for April to June.',
      'date', 'average days to ship|datediff|per month|avg skips null',
      'AVG of DATEDIFF|SUM divided by COUNT of shipped', 'ordered'),
    S(34, 'List every pair of different products that were ordered together in the same order. Show each pair once, with Product1 smaller than Product2, and TimesTogether (number of distinct orders containing both). Sort by TimesTogether descending, then Product1, Product2.',
      """SELECT a.`Product ID` AS Product1, b.`Product ID` AS Product2, COUNT(DISTINCT a.`Order ID`) AS TimesTogether
FROM `order details` a
JOIN `order details` b ON a.`Order ID` = b.`Order ID` AND a.`Product ID` < b.`Product ID`
GROUP BY a.`Product ID`, b.`Product ID`
ORDER BY TimesTogether DESC, Product1, Product2;""",
      """WITH d AS (SELECT DISTINCT `Order ID` AS oid, `Product ID` AS pid FROM `order details`)
SELECT x.pid AS Product1, y.pid AS Product2, COUNT(*) AS TimesTogether
FROM d x
JOIN d y ON x.oid = y.oid AND x.pid < y.pid
GROUP BY x.pid, y.pid
ORDER BY TimesTogether DESC, Product1, Product2;""",
      'Self join of order details on the order. a.`Product ID` < b.`Product ID` removes the pair with itself and keeps each pair once; <> would list every pair twice. 19 pairs; the top three tie at 2 orders: (1, 43), (7, 51), (40, 41). Compare MOCK-15 (only the most frequent pair) and SQL5-028 (at least 2 orders).',
      'self_join', 'products ordered together|self join|pairs|each pair once',
      'self join with less-than|CTE of distinct order-product pairs', 'ordered'),
    S(35, 'Find the products that were ordered together with product 43 in the same order. Return PartnerProduct and TimesTogether (number of distinct orders), sorted by TimesTogether descending, then PartnerProduct.',
      """SELECT b.`Product ID` AS PartnerProduct, COUNT(DISTINCT a.`Order ID`) AS TimesTogether
FROM `order details` a
JOIN `order details` b ON a.`Order ID` = b.`Order ID` AND b.`Product ID` <> a.`Product ID`
WHERE a.`Product ID` = 43
GROUP BY b.`Product ID`
ORDER BY TimesTogether DESC, PartnerProduct;""",
      """SELECT `Product ID` AS PartnerProduct, COUNT(DISTINCT `Order ID`) AS TimesTogether
FROM `order details`
WHERE `Product ID` <> 43 AND `Order ID` IN (SELECT `Order ID` FROM `order details` WHERE `Product ID` = 43)
GROUP BY `Product ID`
ORDER BY TimesTogether DESC, PartnerProduct;""",
      'Variant of SQL6-034 fixed on one product, so the pair is no longer unordered: <> is right here because the other product can be smaller or larger. Two partners in this dump: product 1 (2 orders) and product 81 (1 order).',
      'self_join', 'products bought with a given product|self join|market basket|in subquery',
      'self join fixed on one product|IN subquery of orders containing it', 'ordered'),
    S(36, "Show each customer's ID, First Name, and Last Name with their earliest and most recent order dates as FirstOrderDate and LatestOrderDate. Keep customers without orders, with both dates NULL. Sort by customer ID ascending.",
      '''SELECT c.ID, c.`First Name`, c.`Last Name`, MIN(o.`Order Date`) AS FirstOrderDate, MAX(o.`Order Date`) AS LatestOrderDate
FROM customers c LEFT JOIN orders o ON o.`Customer ID` = c.ID
GROUP BY c.ID, c.`First Name`, c.`Last Name`
ORDER BY c.ID;''',
      '''SELECT c.ID, c.`First Name`, c.`Last Name`,
       (SELECT MIN(o.`Order Date`) FROM orders o WHERE o.`Customer ID` = c.ID) AS FirstOrderDate,
       (SELECT MAX(o.`Order Date`) FROM orders o WHERE o.`Customer ID` = c.ID) AS LatestOrderDate
FROM customers c ORDER BY c.ID;''',
      'LEFT JOIN retains every customer. MIN and MAX ignore NULL dates and return NULL when no dated order exists. Do not filter the joined orders in WHERE or substitute zero for a missing date.',
      'left_join', 'customer|earliest order|latest order|first order date|last order date|include customers without orders',
      'LEFT JOIN with MIN and MAX|correlated date aggregates', 'ordered'),
    S(37, 'For customers who placed orders in 2006, return customer ID, COUNT of distinct orders as TotalOrders, and COUNT of distinct products purchased as TotalDistinctProducts. Count each order and product only once per customer. Sort by TotalOrders descending, then customer ID ascending.',
      '''SELECT c.ID, COUNT(DISTINCT o.`Order ID`) AS TotalOrders, COUNT(DISTINCT d.`Product ID`) AS TotalDistinctProducts
FROM customers c JOIN orders o ON o.`Customer ID` = c.ID
LEFT JOIN `order details` d ON d.`Order ID` = o.`Order ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY c.ID ORDER BY TotalOrders DESC, c.ID;''',
      '''SELECT c.ID,
       (SELECT COUNT(*) FROM orders o WHERE o.`Customer ID` = c.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01') AS TotalOrders,
       (SELECT COUNT(DISTINCT d.`Product ID`) FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID` WHERE o.`Customer ID` = c.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01') AS TotalDistinctProducts
FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.`Customer ID` = c.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01')
ORDER BY TotalOrders DESC, c.ID;''',
      'COUNT(DISTINCT Order ID) prevents line joins from inflating the order count. COUNT(DISTINCT Product ID) deduplicates products across all annual orders. LEFT JOIN keeps annual orders without detail lines, contributing one order and zero products.',
      'group_having', 'customer|2006|distinct order count|distinct product count|avoid duplicate counts',
      'COUNT DISTINCT after LEFT JOIN|independent correlated counts', 'ordered'),
    S(38, 'Retrieve products priced above the average List Price of their own category. Display ID, Product Name, Category, and List Price. Sort by Category alphabetically, then List Price descending.',
      '''SELECT p.ID, p.`Product Name`, p.Category, p.`List Price`
FROM products p
WHERE p.`List Price` > (SELECT AVG(q.`List Price`) FROM products q WHERE q.Category <=> p.Category)
ORDER BY p.Category ASC, p.`List Price` DESC;''',
      '''SELECT p.ID, p.`Product Name`, p.Category, p.`List Price`
FROM products p JOIN (SELECT Category, AVG(`List Price`) AS avg_price FROM products GROUP BY Category) g ON g.Category <=> p.Category
WHERE p.`List Price` > g.avg_price
ORDER BY p.Category ASC, p.`List Price` DESC;''',
      'Compare each product with its own category average, not the global average. AVG ignores NULL prices; equal-to-average prices do not qualify. NULL categories form one group using the MySQL NULL-safe equality operator. Order categories first, then prices descending within each category.',
      'correlated', 'above category average|list price|category alphabetical|price descending',
      'correlated AVG|join to category averages', 'ordered'),
    S(39, 'Find products that did not appear in any orders placed during 2006. Include products never ordered and products purchased only outside 2006. Return ID, Product Name, and Category. Sort by ID ascending.',
      '''SELECT p.ID, p.`Product Name`, p.Category FROM products p
WHERE NOT EXISTS (SELECT 1 FROM `order details` d JOIN orders o ON o.`Order ID` = d.`Order ID` WHERE d.`Product ID` = p.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01')
ORDER BY p.ID;''',
      '''SELECT p.ID, p.`Product Name`, p.Category FROM products p
LEFT JOIN (SELECT DISTINCT d.`Product ID` AS pid FROM `order details` d JOIN orders o ON o.`Order ID` = d.`Order ID` WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01') y ON y.pid = p.ID
WHERE y.pid IS NULL ORDER BY p.ID;''',
      'The year restriction belongs inside NOT EXISTS. Products with no details and products ordered only before or after 2006 remain. Unlike SQL6-010, the projection intentionally omits List Price.',
      'not_exists', 'products absent from 2006 orders|never ordered|outside year|three output columns',
      'NOT EXISTS with annual orders|LEFT JOIN to annual product set', 'ordered'),
    S(40, 'Find employees who processed orders during 2006 for customers in at least 4 different cities. Return Employee ID, First Name, Last Name, and the count of distinct customer cities as TotalCities. Sort by TotalCities descending, then Employee ID ascending.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, COUNT(DISTINCT c.City) AS TotalCities
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY e.ID, e.`First Name`, e.`Last Name`
HAVING COUNT(DISTINCT c.City) >= 4
ORDER BY TotalCities DESC, e.ID ASC;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, cities.TotalCities
FROM employees e JOIN (
  SELECT annual.EmployeeID, COUNT(*) AS TotalCities FROM (
    SELECT DISTINCT o.`Employee ID` AS EmployeeID, c.City
    FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
    WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND c.City IS NOT NULL
  ) annual GROUP BY annual.EmployeeID HAVING COUNT(*) >= 4
) cities ON cities.EmployeeID = e.ID
ORDER BY cities.TotalCities DESC, e.ID ASC;''',
      'Count customer cities, not customers or orders. Repeated customers and cities count once per employee across all 2006 orders. COUNT(DISTINCT City) ignores NULL, which is not a distinct city. No restriction applies to the employee city.',
      'group_having', 'employee|2006|at least four distinct customer cities|TotalCities',
      'COUNT DISTINCT with HAVING|deduplicated employee-city pairs', 'ordered'),
    S(41, 'Find customers who purchased products from exactly 3 different categories during 2006. Return customer ID, First Name, Last Name, and TotalCategories. Count each category only once per customer across all their orders and products.',
      '''SELECT c.ID, c.`First Name`, c.`Last Name`, COUNT(DISTINCT p.Category) AS TotalCategories
FROM customers c JOIN orders o ON o.`Customer ID` = c.ID
JOIN `order details` d ON d.`Order ID` = o.`Order ID`
JOIN products p ON p.ID = d.`Product ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY c.ID, c.`First Name`, c.`Last Name`
HAVING COUNT(DISTINCT p.Category) = 3;''',
      '''SELECT c.ID, c.`First Name`, c.`Last Name`, categories.TotalCategories
FROM customers c JOIN (
  SELECT annual.CustomerID, COUNT(*) AS TotalCategories FROM (
    SELECT DISTINCT o.`Customer ID` AS CustomerID, p.Category
    FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID`
    JOIN products p ON p.ID = d.`Product ID`
    WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01' AND p.Category IS NOT NULL
  ) annual GROUP BY annual.CustomerID HAVING COUNT(*) = 3
) categories ON categories.CustomerID = c.ID;''',
      'Exactly three means HAVING COUNT(DISTINCT Category) = 3, not >= 3 or > 3. Deduplicate categories across all annual orders, not per order. NULL is not a category and orders outside 2006 contribute nothing.',
      'group_having', 'customer|2006|exactly three categories|distinct category count|TotalCategories',
      'COUNT DISTINCT with HAVING equality|deduplicated customer-category pairs'),
    S(42, 'Find employees who processed at least one order during 2006 exclusively for customers in cities different from their own. Exclude employees if their city or any customer city served during 2006 is NULL. Return Employee ID, First Name, and Last Name.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`
FROM employees e
WHERE e.City IS NOT NULL
  AND EXISTS (SELECT 1 FROM orders o WHERE o.`Employee ID` = e.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01')
  AND NOT EXISTS (
    SELECT 1 FROM orders o LEFT JOIN customers c ON c.ID = o.`Customer ID`
    WHERE o.`Employee ID` = e.ID AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
      AND (c.City IS NULL OR c.City = e.City)
  );''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
LEFT JOIN customers c ON c.ID = o.`Customer ID`
WHERE e.City IS NOT NULL AND o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY e.ID, e.`First Name`, e.`Last Name`, e.City
HAVING COUNT(*) = COUNT(c.City) AND SUM(c.City = e.City) = 0;''',
      'EXISTS requires an order in 2006; NOT EXISTS rejects any annual order for a same-city customer or a customer with NULL city. Employee city must also be non-NULL. A simple City <> comparison silently skips NULLs and cannot disqualify an employee who also served a same-city customer. Orders outside 2006 affect neither condition. Unlike SQL6-003, NULL cities explicitly disqualify the employee.',
      'not_exists', 'employee|2006|exclusively different customer cities|at least one annual order|exclude NULL cities',
      'EXISTS and NOT EXISTS with NULL guard|grouped city checks'),
    S(43, 'List pairs of different products that appeared together in at least 3 distinct orders placed during 2006. Return the smaller product ID as Product1ID, the larger as Product2ID, and the number of shared orders as OrdersTogether. Return each pair once. Sort by OrdersTogether descending, then Product1ID and Product2ID ascending.',
      '''SELECT a.`Product ID` AS Product1ID, b.`Product ID` AS Product2ID, COUNT(DISTINCT o.`Order ID`) AS OrdersTogether
FROM orders o JOIN `order details` a ON a.`Order ID` = o.`Order ID`
JOIN `order details` b ON b.`Order ID` = a.`Order ID` AND a.`Product ID` < b.`Product ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
GROUP BY a.`Product ID`, b.`Product ID`
HAVING COUNT(DISTINCT o.`Order ID`) >= 3
ORDER BY OrdersTogether DESC, Product1ID ASC, Product2ID ASC;''',
      '''WITH annual_products AS (
  SELECT DISTINCT d.`Order ID`, d.`Product ID`
  FROM `order details` d JOIN orders o ON o.`Order ID` = d.`Order ID`
  WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
)
SELECT a.`Product ID` AS Product1ID, b.`Product ID` AS Product2ID, COUNT(*) AS OrdersTogether
FROM annual_products a JOIN annual_products b ON a.`Order ID` = b.`Order ID` AND a.`Product ID` < b.`Product ID`
GROUP BY a.`Product ID`, b.`Product ID` HAVING COUNT(*) >= 3
ORDER BY OrdersTogether DESC, Product1ID ASC, Product2ID ASC;''',
      'Filter Order Date on orders before counting co-occurrences. The strict product-ID inequality excludes self pairs and mirrored pairs. COUNT(DISTINCT Order ID), or deduplicating order-product rows first, prevents repeated detail lines from inflating the shared-order count. HAVING >= 3 includes the exact threshold; orders outside 2006 do not count.',
      'self_join', 'product pairs|2006|three or more distinct orders|OrdersTogether|each unordered pair once',
      'self join with COUNT DISTINCT|deduplicated annual order-product CTE', 'ordered'),
    S(44, 'Find employees who processed orders for at least TWO DIFFERENT customers residing in the SAME city. Return Employee ID, First Name, Last Name, City, and Number of Distinct Customers for each qualifying employee-city combination. Use customers.City (NOT Ship City); exclude NULL cities and count each customer once even if they placed multiple orders.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, c.City,
       COUNT(DISTINCT c.ID) AS `Number of Distinct Customers`
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
WHERE c.City IS NOT NULL
GROUP BY e.ID, e.`First Name`, e.`Last Name`, c.City
HAVING COUNT(DISTINCT c.ID) >= 2;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, served.City,
       COUNT(*) AS `Number of Distinct Customers`
FROM employees e JOIN (
  SELECT DISTINCT o.`Employee ID` AS EmployeeID, c.City, c.ID AS CustomerID
  FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
  WHERE c.City IS NOT NULL
) served ON served.EmployeeID = e.ID
GROUP BY e.ID, e.`First Name`, e.`Last Name`, served.City
HAVING COUNT(*) >= 2;''',
      'Group by employee and customer residence city, not Ship City or employee city. COUNT(DISTINCT customer ID) counts repeated orders only once per customer. Exclude NULL cities before grouping. The threshold applies separately to each employee-city combination; there is no year restriction.',
      'group_having', 'employee|same customer city|at least two distinct customers|employee-city groups|exclude NULL cities',
      'COUNT DISTINCT with HAVING|deduplicated employee-city-customer triples'),
]
