"""Targeted join/grain/measure/filter gaps, not threshold or date permutations."""


def S(number, question, sql, alt, explanation, grain, measures, filters, pattern='group_having'):
    return dict(id='SQL8-%03d' % number, question=question, sql=sql, alt=alt,
                explanation=explanation, pattern=pattern, difficulty=3, cmp='set',
                tags=['group by', 'distinct', *grain.split('|')],
                techniques=['grouped join', 'independent preaggregation or correlated subqueries'],
                coverage=dict(groupBy=grain.split('|'), measures=measures.split('|'),
                              filters=filters.split('|') if filters else []))


SQL8 = [
    S(1, 'Find employee and customer residence city combinations with at least 2 distinct orders. Return Employee ID, First Name, Last Name, City, and TotalOrders. Use customers.City and exclude NULL cities. Count orders rather than customers; repeated orders by one customer count separately.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, c.City,
       COUNT(DISTINCT o.`Order ID`) AS TotalOrders
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
WHERE c.City IS NOT NULL
GROUP BY e.ID, e.`First Name`, e.`Last Name`, c.City
HAVING COUNT(DISTINCT o.`Order ID`) >= 2;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, served.City, COUNT(*) AS TotalOrders
FROM employees e JOIN (
  SELECT DISTINCT o.`Employee ID` AS EmployeeID, c.City, o.`Order ID`
  FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
  WHERE c.City IS NOT NULL
) served ON served.EmployeeID = e.ID
GROUP BY e.ID, e.`First Name`, e.`Last Name`, served.City
HAVING COUNT(*) >= 2;''',
      'The grain is employee plus customer residence city. Unlike SQL6-044, the measure is orders, so two orders from one customer qualify. No order-details join or year restriction is needed.',
      'employees.ID|customers.City', 'COUNT DISTINCT orders.Order ID', 'customers.City IS NOT NULL|TotalOrders >= 2'),
    S(2, 'Find employee and shipping destination city combinations serving at least 2 different customers. Return Employee ID, First Name, Last Name, Ship City, and TotalCustomers. Use orders.Ship City rather than customer residence city. Exclude NULL shipping cities and count each customer once per employee and destination city.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, o.`Ship City`,
       COUNT(DISTINCT c.ID) AS TotalCustomers
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
WHERE o.`Ship City` IS NOT NULL
GROUP BY e.ID, e.`First Name`, e.`Last Name`, o.`Ship City`
HAVING COUNT(DISTINCT c.ID) >= 2;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, served.`Ship City`, COUNT(*) AS TotalCustomers
FROM employees e JOIN (
  SELECT DISTINCT o.`Employee ID` AS EmployeeID, o.`Ship City`, c.ID AS CustomerID
  FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
  WHERE o.`Ship City` IS NOT NULL
) served ON served.EmployeeID = e.ID
GROUP BY e.ID, e.`First Name`, e.`Last Name`, served.`Ship City`
HAVING COUNT(*) >= 2;''',
      'Shipping destination and customer residence are different dimensions. One customer may contribute once in each destination city; NULL residence cities remain eligible when the shipping city is known.',
      'employees.ID|orders.Ship City', 'COUNT DISTINCT customers.ID', 'orders.Ship City IS NOT NULL|TotalCustomers >= 2'),
    S(3, 'Find employee and product category combinations that served at least 2 distinct customers during 2006. Return Employee ID, First Name, Last Name, Category, and TotalCustomers. Exclude NULL categories. Count each customer once per employee and category across all qualifying orders and detail lines.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, p.Category,
       COUNT(DISTINCT c.ID) AS TotalCustomers
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
JOIN `order details` d ON d.`Order ID` = o.`Order ID`
JOIN products p ON p.ID = d.`Product ID`
WHERE o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2007-01-01'
  AND p.Category IS NOT NULL
GROUP BY e.ID, e.`First Name`, e.`Last Name`, p.Category
HAVING COUNT(DISTINCT c.ID) >= 2;''',
      '''WITH served AS (
  SELECT DISTINCT o.`Employee ID` AS EmployeeID, p.Category, c.ID AS CustomerID
  FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
  JOIN `order details` d ON d.`Order ID` = o.`Order ID`
  JOIN products p ON p.ID = d.`Product ID`
  WHERE YEAR(o.`Order Date`) = 2006 AND p.Category IS NOT NULL
)
SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`, served.Category, COUNT(*) AS TotalCustomers
FROM employees e JOIN served ON served.EmployeeID = e.ID
GROUP BY e.ID, e.`First Name`, e.`Last Name`, served.Category
HAVING COUNT(*) >= 2;''',
      'Group by employee and category, then deduplicate customers across both orders and product lines. The half-open annual interval includes the last second of 2006 but excludes 2007.',
      'employees.ID|products.Category', 'COUNT DISTINCT customers.ID', 'Order Date in 2006|Category IS NOT NULL|TotalCustomers >= 2'),
    S(4, 'Find customer and product category combinations containing at least 2 distinct purchased products. Return Customer ID, Company, Category, and TotalProducts. Exclude NULL categories. Count a product once per customer and category even across repeated orders or detail lines.',
      '''SELECT c.ID AS `Customer ID`, c.Company, p.Category, COUNT(DISTINCT p.ID) AS TotalProducts
FROM customers c JOIN orders o ON o.`Customer ID` = c.ID
JOIN `order details` d ON d.`Order ID` = o.`Order ID`
JOIN products p ON p.ID = d.`Product ID`
WHERE p.Category IS NOT NULL
GROUP BY c.ID, c.Company, p.Category
HAVING COUNT(DISTINCT p.ID) >= 2;''',
      '''SELECT c.ID AS `Customer ID`, c.Company, bought.Category, COUNT(*) AS TotalProducts
FROM customers c JOIN (
  SELECT DISTINCT o.`Customer ID` AS CustomerID, p.Category, p.ID AS ProductID
  FROM orders o JOIN `order details` d ON d.`Order ID` = o.`Order ID`
  JOIN products p ON p.ID = d.`Product ID` WHERE p.Category IS NOT NULL
) bought ON bought.CustomerID = c.ID
GROUP BY c.ID, c.Company, bought.Category HAVING COUNT(*) >= 2;''',
      'This is a product count within each customer-category pair, not a category count per customer or quantity sum. Repeated purchases of the same product do not increase TotalProducts.',
      'customers.ID|products.Category', 'COUNT DISTINCT products.ID', 'Category IS NOT NULL|TotalProducts >= 2'),
    S(5, 'Find shipper and customer residence city combinations serving at least 2 distinct customers. Return Shipper ID, ShipperCompany, City, and TotalCustomers. Use customers.City, exclude NULL cities, and count each customer once for each shipper and city, including orders that have no detail lines.',
      '''SELECT s.ID AS `Shipper ID`, s.Company AS ShipperCompany, c.City,
       COUNT(DISTINCT c.ID) AS TotalCustomers
FROM shippers s JOIN orders o ON o.`Shipper ID` = s.ID
JOIN customers c ON c.ID = o.`Customer ID`
WHERE c.City IS NOT NULL
GROUP BY s.ID, s.Company, c.City HAVING COUNT(DISTINCT c.ID) >= 2;''',
      '''SELECT s.ID AS `Shipper ID`, s.Company AS ShipperCompany, served.City, COUNT(*) AS TotalCustomers
FROM shippers s JOIN (
  SELECT DISTINCT o.`Shipper ID` AS ShipperID, c.City, c.ID AS CustomerID
  FROM orders o JOIN customers c ON c.ID = o.`Customer ID`
  WHERE c.City IS NOT NULL
) served ON served.ShipperID = s.ID
GROUP BY s.ID, s.Company, served.City HAVING COUNT(*) >= 2;''',
      'The order header already links shippers to customers. Joining order details would unnecessarily discard orders with no lines. The city is the customer residence, not the shipping destination.',
      'shippers.ID|customers.City', 'COUNT DISTINCT customers.ID', 'customers.City IS NOT NULL|TotalCustomers >= 2'),
    S(6, 'Find supplier and product category combinations with at least 2 different products actually procured through purchase orders. Return Supplier ID, SupplierCompany, Category, and TotalProducts. Exclude NULL categories. Use purchase history rather than the products.Supplier IDs text field; repeated purchase lines count each product once.',
      '''SELECT s.ID AS `Supplier ID`, s.Company AS SupplierCompany, p.Category,
       COUNT(DISTINCT p.ID) AS TotalProducts
FROM suppliers s JOIN `purchase orders` po ON po.`Supplier ID` = s.ID
JOIN `purchase order details` d ON d.`Purchase Order ID` = po.`Purchase Order ID`
JOIN products p ON p.ID = d.`Product ID`
WHERE p.Category IS NOT NULL
GROUP BY s.ID, s.Company, p.Category HAVING COUNT(DISTINCT p.ID) >= 2;''',
      '''SELECT s.ID AS `Supplier ID`, s.Company AS SupplierCompany, bought.Category, COUNT(*) AS TotalProducts
FROM suppliers s JOIN (
  SELECT DISTINCT po.`Supplier ID` AS SupplierID, p.Category, p.ID AS ProductID
  FROM `purchase orders` po JOIN `purchase order details` d ON d.`Purchase Order ID` = po.`Purchase Order ID`
  JOIN products p ON p.ID = d.`Product ID` WHERE p.Category IS NOT NULL
) bought ON bought.SupplierID = s.ID
GROUP BY s.ID, s.Company, bought.Category HAVING COUNT(*) >= 2;''',
      'Actual suppliers are established by purchase orders and their detail lines, not the catalogue Supplier IDs string. Count distinct products within each supplier-category group, regardless of repeated orders or lines.',
      'suppliers.ID|products.Category', 'COUNT DISTINCT products.ID', 'purchase history|Category IS NOT NULL|TotalProducts >= 2'),
    S(7, 'Find purchase order creator and supplier combinations with at least 2 distinct purchase orders. Return Employee ID, First Name, Last Name, Supplier ID, SupplierCompany, and TotalPurchaseOrders. Use purchase orders.Created By rather than Approved By or Submitted By. Include purchase orders with no detail lines.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       s.ID AS `Supplier ID`, s.Company AS SupplierCompany, COUNT(*) AS TotalPurchaseOrders
FROM employees e JOIN `purchase orders` po ON po.`Created By` = e.ID
JOIN suppliers s ON s.ID = po.`Supplier ID`
GROUP BY e.ID, e.`First Name`, e.`Last Name`, s.ID, s.Company HAVING COUNT(*) >= 2;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       s.ID AS `Supplier ID`, s.Company AS SupplierCompany, totals.TotalPurchaseOrders
FROM (
  SELECT po.`Created By` AS EmployeeID, po.`Supplier ID` AS SupplierID,
         COUNT(DISTINCT po.`Purchase Order ID`) AS TotalPurchaseOrders
  FROM `purchase orders` po GROUP BY po.`Created By`, po.`Supplier ID`
  HAVING COUNT(DISTINCT po.`Purchase Order ID`) >= 2
) totals JOIN employees e ON e.ID = totals.EmployeeID JOIN suppliers s ON s.ID = totals.SupplierID;''',
      'Created By, Approved By and Submitted By are separate employee roles. Header-only counting retains purchase orders with no lines and avoids multiplying counts by the number of purchased items.',
      'purchase orders.Created By|suppliers.ID', 'COUNT DISTINCT purchase orders.Purchase Order ID', 'TotalPurchaseOrders >= 2'),
    S(8, 'For every supplier, return Supplier ID, SupplierCompany, TotalPurchaseOrders, TotalShippingFee, and TotalItemCost. Count each purchase order once and sum its Shipping Fee once. Calculate item cost as the sum of Quantity multiplied by Unit Cost from purchase order details. Include suppliers without purchase orders and purchase orders without details, using zero totals.',
      '''SELECT s.ID AS `Supplier ID`, s.Company AS SupplierCompany,
       COUNT(po.`Purchase Order ID`) AS TotalPurchaseOrders,
       COALESCE(SUM(po.`Shipping Fee`), 0) AS TotalShippingFee,
       COALESCE(SUM(items.ItemCost), 0) AS TotalItemCost
FROM suppliers s LEFT JOIN `purchase orders` po ON po.`Supplier ID` = s.ID
LEFT JOIN (
  SELECT `Purchase Order ID`, SUM(Quantity * `Unit Cost`) AS ItemCost
  FROM `purchase order details` GROUP BY `Purchase Order ID`
) items ON items.`Purchase Order ID` = po.`Purchase Order ID`
GROUP BY s.ID, s.Company;''',
      '''SELECT s.ID AS `Supplier ID`, s.Company AS SupplierCompany,
       (SELECT COUNT(*) FROM `purchase orders` po WHERE po.`Supplier ID` = s.ID) AS TotalPurchaseOrders,
       COALESCE((SELECT SUM(po.`Shipping Fee`) FROM `purchase orders` po WHERE po.`Supplier ID` = s.ID), 0) AS TotalShippingFee,
       COALESCE((SELECT SUM(d.Quantity * d.`Unit Cost`) FROM `purchase orders` po
                 JOIN `purchase order details` d ON d.`Purchase Order ID` = po.`Purchase Order ID`
                 WHERE po.`Supplier ID` = s.ID), 0) AS TotalItemCost
FROM suppliers s;''',
      'Aggregate purchase lines to one row per purchase order before joining headers. This prevents fan-out from duplicating shipping fees or order counts. SUM(DISTINCT Shipping Fee) is wrong when different orders have equal fees.',
      'suppliers.ID', 'COUNT purchase orders|SUM header Shipping Fee once|SUM Quantity * Unit Cost', 'all suppliers|include empty purchase orders', 'multi_agg'),
    S(9, 'For each employee and customer combination with orders, return Employee ID, First Name, Last Name, Customer ID, CustomerCompany, TotalOrders, and TotalSales. Sum discounted sales as Quantity multiplied by Unit Price multiplied by (1 - Discount), treating NULL Discount as zero. Count each order once and include orders without detail lines with zero sales.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       c.ID AS `Customer ID`, c.Company AS CustomerCompany, COUNT(*) AS TotalOrders,
       COALESCE(SUM(items.Sales), 0) AS TotalSales
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
LEFT JOIN (
  SELECT `Order ID`, SUM(Quantity * `Unit Price` * (1 - COALESCE(Discount, 0))) AS Sales
  FROM `order details` GROUP BY `Order ID`
) items ON items.`Order ID` = o.`Order ID`
GROUP BY e.ID, e.`First Name`, e.`Last Name`, c.ID, c.Company;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       c.ID AS `Customer ID`, c.Company AS CustomerCompany,
       COUNT(DISTINCT o.`Order ID`) AS TotalOrders,
       COALESCE(SUM(d.Quantity * d.`Unit Price` * (1 - COALESCE(d.Discount, 0))), 0) AS TotalSales
FROM employees e JOIN orders o ON o.`Employee ID` = e.ID
JOIN customers c ON c.ID = o.`Customer ID`
LEFT JOIN `order details` d ON d.`Order ID` = o.`Order ID`
GROUP BY e.ID, e.`First Name`, e.`Last Name`, c.ID, c.Company;''',
      'The grain is employee-customer, not employee-customer-category. Preaggregating detail sales preserves orders with no lines and prevents counting one order once per detail. The independent direct join uses COUNT DISTINCT for order IDs.',
      'employees.ID|customers.ID', 'COUNT DISTINCT orders.Order ID|SUM discounted detail sales', 'include orders without details|NULL Discount = 0', 'multi_agg'),
    S(10, 'For every employee, return Employee ID, First Name, Last Name, and TotalPrivileges, the number of distinct valid privileges assigned. Include employees with no valid assignments with zero. Repeated assignments count once, and privilege IDs absent from the privileges lookup do not count.',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       COUNT(DISTINCT p.`Privilege ID`) AS TotalPrivileges
FROM employees e LEFT JOIN `employee privileges` ep ON ep.`Employee ID` = e.ID
LEFT JOIN privileges p ON p.`Privilege ID` = ep.`Privilege ID`
GROUP BY e.ID, e.`First Name`, e.`Last Name`;''',
      '''SELECT e.ID AS `Employee ID`, e.`First Name`, e.`Last Name`,
       (SELECT COUNT(*) FROM privileges p WHERE EXISTS (
         SELECT 1 FROM `employee privileges` ep
         WHERE ep.`Employee ID` = e.ID AND ep.`Privilege ID` = p.`Privilege ID`
       )) AS TotalPrivileges
FROM employees e;''',
      'The outer employee table retains zero-assignment employees. Count distinct lookup keys rather than bridge rows, so duplicate or orphaned assignments do not inflate the total.',
      'employees.ID', 'COUNT DISTINCT privileges.Privilege ID', 'all employees|valid privilege lookup entries', 'multi_agg'),
    S(11, 'For every order-detail status, return Status ID, Status Name, TotalLines, and TotalOrders. Count detail lines and distinct Order IDs separately. Include statuses with no detail lines with zero counts. Repeated lines from one order increase TotalLines but count that order once; NULL Order IDs do not count as an order.',
      '''SELECT s.`Status ID`, s.`Status Name`, COUNT(d.ID) AS TotalLines,
       COUNT(DISTINCT d.`Order ID`) AS TotalOrders
FROM `order details status` s LEFT JOIN `order details` d ON d.`Status ID` = s.`Status ID`
GROUP BY s.`Status ID`, s.`Status Name`;''',
      '''SELECT s.`Status ID`, s.`Status Name`,
       (SELECT COUNT(*) FROM `order details` d WHERE d.`Status ID` = s.`Status ID`) AS TotalLines,
       (SELECT COUNT(DISTINCT d.`Order ID`) FROM `order details` d
        WHERE d.`Status ID` = s.`Status ID`) AS TotalOrders
FROM `order details status` s;''',
      'A line count and an order count have different units. COUNT(d.ID) avoids the synthetic NULL row from LEFT JOIN, while COUNT DISTINCT Order ID deduplicates orders and ignores NULL references.',
      'order details status.Status ID', 'COUNT order details.ID|COUNT DISTINCT order details.Order ID', 'all line statuses', 'multi_agg'),
    S(12, 'For each inventory transaction type and product category represented during 2006, return Transaction Type, Type Name, Category, TotalProducts, and TotalQuantity. Count distinct products and sum transaction Quantity. Use Transaction Created Date, exclude NULL categories, and keep Purchased, Sold, On Hold, and Waste types separate.',
      '''SELECT t.ID AS `Transaction Type`, t.`Type Name`, p.Category,
       COUNT(DISTINCT p.ID) AS TotalProducts, SUM(i.Quantity) AS TotalQuantity
FROM `inventory transaction types` t
JOIN `inventory transactions` i ON i.`Transaction Type` = t.ID
JOIN products p ON p.ID = i.`Product ID`
WHERE i.`Transaction Created Date` >= '2006-01-01'
  AND i.`Transaction Created Date` < '2007-01-01' AND p.Category IS NOT NULL
GROUP BY t.ID, t.`Type Name`, p.Category;''',
      '''WITH movements AS (
  SELECT i.`Transaction Type`, p.Category, p.ID AS ProductID, SUM(i.Quantity) AS Quantity
  FROM `inventory transactions` i JOIN products p ON p.ID = i.`Product ID`
  WHERE YEAR(i.`Transaction Created Date`) = 2006 AND p.Category IS NOT NULL
  GROUP BY i.`Transaction Type`, p.Category, p.ID
)
SELECT t.ID AS `Transaction Type`, t.`Type Name`, m.Category,
       COUNT(*) AS TotalProducts, SUM(m.Quantity) AS TotalQuantity
FROM `inventory transaction types` t JOIN movements m ON m.`Transaction Type` = t.ID
GROUP BY t.ID, t.`Type Name`, m.Category;''',
      'Transaction Created Date controls the inventory reporting year, not a linked sales or purchase date. Repeated movements increase quantity but not the distinct product count. Type IDs are resolved through the lookup rather than hard-coded.',
      'inventory transaction types.ID|products.Category', 'COUNT DISTINCT products.ID|SUM inventory transactions.Quantity', 'Transaction Created Date in 2006|Category IS NOT NULL', 'multi_agg'),
]

ALIASES_SQL8 = {
    'SQL8-001': ['Employees with two or more orders for customers residing in one city, grouped by employee and customer city, counting orders rather than people.'],
    'SQL8-002': ['Employees serving two or more distinct customers at one shipping destination, grouped by employee and Ship City.'],
    'SQL8-003': ['Employee-category groups serving two or more different customers in 2006, with repeated purchases counted once per customer.'],
    'SQL8-004': ['Customer-category groups with two or more different purchased products, deduplicated across order lines and orders.'],
    'SQL8-005': ['Shippers serving two or more customers living in one city, using customer residence and retaining orders with no details.'],
    'SQL8-006': ['Supplier-category groups with two or more different products in actual procurement history, counting each product once.'],
    'SQL8-007': ['Employees who created two or more purchase orders for one supplier, grouped by creator and supplier rather than approver.'],
    'SQL8-008': ['Supplier purchasing summary with order counts, shipping fees counted once per order, and detail item costs, including unused suppliers.'],
    'SQL8-009': ['Employee-customer order counts and discounted revenue, retaining orders without lines and treating unknown discounts as zero.'],
    'SQL8-010': ['All employees with the count of distinct assigned privileges existing in the lookup, including zero and ignoring duplicate assignments.'],
    'SQL8-011': ['All order detail statuses with separate counts of lines and different orders, including unused statuses with zeros.'],
    'SQL8-012': ['Inventory quantities and unique products by movement type and category in 2006, using transaction creation dates.'],
}
