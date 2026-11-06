"""Corpus-wide English paraphrases; retrieval only, never SQL verification input.

ponytail: lexical templates, not semantic inference; extend curated cues for new concepts.
"""
import re

from bank_combo import MEASURES


CURATED = {
    'TH-01': 'Compare removing duplicate result rows with grouping rows to calculate aggregates: DISTINCT versus GROUP BY.',
    'TH-02': 'Which conditions filter individual rows before aggregation and which filter grouped results afterward: WHERE versus HAVING?',
    'TH-03': 'When should a join retain unmatched left-side rows instead of returning only matching records?',
    'TH-04': 'Compare testing whether a correlated row exists with testing membership in a subquery result set.',
    'TH-05': 'Why can a NULL in a NOT IN subquery eliminate every result, and how does NOT EXISTS avoid that problem?',
    'TH-06': 'Explain counting all rows, only non-NULL column values, and unique non-NULL values with the different COUNT forms.',
    'TH-07': 'Compare combining query results while removing duplicates versus preserving duplicates with UNION ALL.',
    'TH-08': 'How can filtering, indexes, join choices and execution-plan inspection improve query performance?',
    'TH-09': 'Explain how an index speeds up row lookup and when the optimizer may choose a table scan instead.',
    'TH-10': 'Why select explicit columns rather than every column with SELECT star?',
    'TH-11': 'Explain pagination: how many rows LIMIT returns and how many rows OFFSET skips.',
    'TH-12': 'When should related data be retrieved with a nested SELECT instead of joining tables?',
    'TH-13': 'Explain row identifiers and references between parent and child tables using primary and foreign keys.',
    'TH-14': 'Explain missing values, UNKNOWN comparisons, IS NULL and SQL three-valued logic.',
    'TH-15': 'Compare sequential row numbers, competition ranking with gaps and dense ranking without gaps when values tie.',
    'TH-16': 'Why join the same table twice under different aliases to compare its rows?',
    'TH-17': 'In what sequence are FROM, WHERE, GROUP BY, HAVING, SELECT, DISTINCT, ORDER BY and LIMIT logically processed?',
    'TH-18': 'Compare deleting selected records, emptying a table and removing the table definition entirely.',
    'TH-19': 'Explain COUNT, SUM, AVG, MIN and MAX, including their treatment of missing values.',
    'TH-20': 'Compare a stored virtual query with a statement-scoped named result: view versus common table expression.',
    'TH-21': 'Why can an inclusive date range omit timestamps on its final day, and when is a half-open range safer?',
    'TH-22': 'Compare exact text equality with LIKE pattern matching and explain leading-wildcard index limitations.',
    'TH-23': 'Classify schema changes, row changes, access permissions and transaction commands into SQL language groups.',
    'TH-24': 'How do a primary key and a unique constraint differ in NULL handling and the number allowed per table?',
    'TH-25': 'Explain referential integrity and automatic deletion of dependent rows through ON DELETE CASCADE.',
    'TH-26': 'Explain atomic attributes, partial dependencies and transitive dependencies in the first three normal forms.',
    'TH-27': 'Compare the index that organizes table records with secondary indexes used for alternative lookups.',
    'TH-28': 'Why does column order matter in a multi-column index, and which leading columns can a lookup use?',
    'TH-29': 'How can an index supply every selected column without fetching the underlying table row?',
    'TH-30': 'Why can wrapping an indexed column in a function prevent an index range lookup? Explain sargable predicates.',
    'TH-31': 'Explain access types, chosen keys, estimated row counts and extra operations in a query execution plan.',
    'TH-32': 'What storage and write-performance costs come with maintaining too many indexes?',
    'TH-33': 'Explain transaction atomicity, consistency, isolation and durability.',
    'TH-34': 'How do you permanently save changes, undo a transaction or roll back to an intermediate savepoint?',
    'TH-35': 'Compare dirty reads, nonrepeatable reads and phantom reads across transaction isolation levels.',
    'TH-36': 'Explain circular lock waits between transactions, deadlock detection and retrying the aborted transaction.',
    'TH-37': 'Compare fixed-width and variable-width character storage and trailing-space behavior.',
    'TH-38': 'Compare storing calendar dates, date-time values and time-zone-converted timestamps.',
    'TH-39': 'Why use exact decimal arithmetic for money rather than approximate floating-point numbers?',
    'TH-40': 'How does an unknown value differ from an empty string or numeric zero?',
    'TH-41': 'Compare replacing NULL, choosing the first non-NULL expression and turning equal values into NULL.',
    'TH-42': 'Compare conditional expressions using CASE branches and the MySQL IF function.',
    'TH-43': 'Explain a Cartesian product that produces every possible pair of rows from two tables.',
    'TH-44': 'Explain retaining unmatched rows from the right table and simulating a full outer join using UNION.',
    'TH-45': 'Why prefer explicit JOIN ON clauses over comma-separated tables and join conditions in WHERE?',
    'TH-46': 'Why can filtering the right side in WHERE remove unmatched rows from a LEFT JOIN?',
    'TH-47': 'Explain set intersection and set difference, MySQL version support and alternatives using joins or EXISTS.',
    'TH-48': 'How do comparisons against every subquery value differ from comparisons against at least one value?',
    'TH-49': 'Explain subqueries that return a single value, a row, a table or depend on the outer row.',
    'TH-50': 'Explain anchor and recursive members of a recursive common table expression and how recursion terminates.',
    'TH-51': 'How can aggregates over a window preserve individual rows instead of collapsing them into groups?',
    'TH-52': 'How do you select the highest-ranked rows separately inside each category or other partition?',
    'TH-53': 'How do you find a particular price position, distinguishing row positions from distinct values and handling ties?',
    'TH-54': 'How do you detect repeated key combinations with grouping and a count greater than one?',
    'TH-55': 'How can grouped values be concatenated into one string with a chosen separator and ordering?',
    'TH-56': 'Why does strict grouping reject a selected column that is neither grouped, aggregated nor functionally dependent?',
    'TH-57': 'Can an aggregate condition filter the whole result as one implicit group without an explicit GROUP BY?',
    'TH-58': 'Where do missing values appear in ascending and descending MySQL sorting, and how can their position be controlled?',
    'TH-59': 'Does counting a constant differ from counting all rows, including rows with NULL columns?',
    'TH-60': 'Compare fractional division with integer-quotient division in MySQL.',
    'TH-61': 'Compare rounding to the nearest value, rounding upward, rounding downward and discarding decimal places.',
    'TH-62': 'How do you calculate elapsed days versus elapsed time in a selected unit between two timestamps?',
    'TH-63': 'How do date-format placeholders produce year, month, day and time strings?',
    'TH-64': 'Why can the byte length of a Unicode string differ from its character count?',
    'TH-65': 'How can UPDATE and DELETE use a joined table to determine which records to change?',
    'TH-66': 'Compare changing an existing row on a duplicate key with deleting and replacing that row.',
    'TH-67': 'Explain required values, uniqueness rules, check predicates and default column values.',
    'TH-68': 'Explain automatically generated numeric identifiers and choosing an artificial row key.',
    'TH-69': 'Compare a callable stored procedure, a value-returning function and an automatically executed trigger.',
    'TH-70': 'How do virtual tables expose saved queries, simplify access and restrict columns, and when can a view be updated?',
    'TH-71': 'How do parameterized prepared statements protect database queries against SQL injection attacks from untrusted input?',
    'TH-72': 'How do text comparison and sorting rules control case and accent sensitivity?',
    'TH-73': 'Compare simple wildcard text patterns with regular-expression matching.',
    'TH-74': 'Compare membership in a value list, alternative Boolean conditions and an inclusive interval test.',
    'TH-75': 'Why does counting an empty input return zero while SUM, AVG, MIN and MAX return NULL?',
    'TH-76': 'Why test existence instead of counting every matching row, and does the selected constant inside EXISTS matter?',
    'TH-77': 'Compare session-scoped temporary storage, statement-scoped CTEs and subqueries in FROM.',
    'TH-78': 'Distinguish logical row identity from physical clustered storage and compare business keys with generated keys.',
    'TH-79': 'Is a join always faster than a subquery, or do indexes, selectivity and the optimizer plan determine performance?',
    'TH-80': 'Explain selection, projection, join, union, intersection and difference in relational algebra.',
    'TH-81': 'Distinguish database structure, a stored database and the software system that manages databases.',
    'TH-82': 'Explain one-to-one, one-to-many and many-to-many relationships and how a junction table represents the last.',
    'MOCK-01': 'Customer names and job titles, ordered by surname descending then given name descending.',
    'MOCK-02': 'Distinct destination country or region count per employee, including employees without orders.',
    'MOCK-04': 'States or provinces represented by exactly one customer, with that customer name.',
    'MOCK-07': 'Employees tied for the greatest annual order count across all months of 2006.',
    'MOCK-08': 'Employees who have never handled a customer order from their own city; also retain employees with no orders.',
    'MOCK-09': 'Explain the cost of SELECT star and a missing order-date index, then select only required columns and improve the range lookup.',
    'MOCK-10': 'Compare returning exactly ten products with retaining all products tied at the tenth product price.',
    'MOCK-11': 'Products with at least fifty percent profit margin, computed relative to Standard Cost rather than List Price.',
    'MOCK-13': 'Order value is the sum of Unit Price multiplied by Quantity. Show order ID, gross total, shipping charge and shipping ratio rounded to four decimal places for positive totals whose fee exceeds fifteen percent of the total.',
    'MOCK-14': 'Monthly sold inventory quantities per product, using the movement creation timestamp and the Sold transaction type.',
    'MOCK-15': 'Unordered product pairs sharing the greatest number of distinct orders. Return only maximum-frequency pairs, retaining every pair tied for that maximum.',
    'LAB-01': 'Single-row catalogue statistics: product count, distinct category count and minimum, maximum and mean list prices.',
    'LAB-02': 'Compare row counts with counts of non-NULL shipment dates, carriers and payment methods, deriving the unshipped count without a row filter.',
    'LAB-03': 'Overall discounted sales amount, mean detail-line value and maximum detail-line value.',
    'LAB-04': 'Product count and mean catalogue price grouped by category, most populated categories first.',
    'LAB-05': 'Products with at least 100 units sold in sales-detail rows, ordered by units descending.',
    'LAB-06': 'Customers with at least three Closed orders, with closed-order counts, shipping totals and first and last closed-order dates.',
    'LAB-07': 'March 2006 orders with buyer company and the employee who handled them, ordered by placement date then order ID.',
    'LAB-08': 'All customers with their order counts, including zero-order customers first; explain the phantom row counted by COUNT star after a left join.',
    'LAB-09': 'Full outer shipper-order coverage using left and right joins with UNION, retaining unused carriers and orders without assigned carriers.',
    'LAB-10': 'Carrier by payment-method matrix including zero-count combinations, using a Cartesian grid followed by an outer join.',
    'LAB-11': 'Unique unordered customer pairs sharing a city, without self pairs or mirrored duplicates.',
    'LAB-12': 'Different products sharing the same supposedly unique Product Code, found through a self join.',
    'LAB-13': 'All purchase orders with vendor, status, creator and approver names, retaining unknown employees.',
    'LAB-14': 'Products above the overall mean price, showing the price difference from that mean.',
    'LAB-15': 'Most expensive products inside each category, including every product tied at the category maximum.',
    'LAB-16': 'Customers who purchased a Beverages product, with equivalent membership and existence queries.',
    'LAB-17': 'Employees with no created purchase orders; explain the NULL trap in NOT IN and replace it with NOT EXISTS.',
    'LAB-18': 'Other orders sharing both the buyer and salesperson of order 30, excluding that reference order.',
    'LAB-19': 'Combined customer, employee and supplier contact directory; compare duplicate-preserving and deduplicated customer-employee city unions.',
    'LAB-20': 'Products present in both customer sales details and supplier purchase details, using set intersection or membership.',
    'LAB-21': 'Products purchased from vendors but absent from sales details, using set difference or an anti-existence test.',
    'LAB-22': 'Employee contact formatting: uppercase surname, full display name, initials, lowercase email, email domain and name length.',
    'LAB-23': 'Split product codes into prefix and numeric suffix, shorten product names and count prefixes used by at least three products.',
    'LAB-24': 'Products with multiple semicolon-separated supplier identifiers, extracting first and last supplier and counting delimiters.',
    'LAB-25': 'Chronological monthly order counts and shipping-charge totals with year-month and readable month names.',
    'LAB-26': 'Shipping lead-time statistics per carrier: shipped-order count, mean and longest elapsed days, and same-day shipment count.',
    'LAB-27': 'Earliest five invoices with formatted dates, weekday, a computed thirty-day due date and overdue age relative to the execution date.',
    'LAB-28': 'Budget, Standard and Premium product price bands with product counts and mean prices in the requested band order.',
    'LAB-29': 'Unclosed order report with customer, carrier fallback, shipment fallback, paid status and readable order status.',
    'LAB-30': 'Employee status-count pivot including zero-order employees and the percentage of Closed orders.',
    'LAB-31': 'Five highest-spending customers by discounted revenue, with distinct order counts, first and last purchase dates and spending tiers.',
    'LAB-32': 'Category sales pivot for January through June 2006, with monthly discounted revenue and a half-year total.',
    'LAB-33': 'Stock-on-hand and replenishment report from Purchased, Sold, On Hold and Waste inventory movements; prioritize products requiring reorder.',
    'A3-01': 'Employee contact details: email addresses and business telephone numbers.',
    'A3-02': 'Distinct product category names without repeated categories.',
    'A3-03': 'Distinct customer city names in alphabetical order.',
    'A3-04': 'Suppliers with surnames beginning with the letter H.',
    'A3-05': 'Product names, categories, list prices and standard costs, highest list price first then highest standard cost.',
    'A3-06': 'Products in Pasta, Soups or Beverages priced above 10, sorted by product name alphabetically.',
    'A3-07': 'Employee names alphabetically by surname and then given name.',
    'A3-08': 'Orders paid using a credit card.',
    'A3-09': 'The ten most recent purchase orders.',
    'A3-10': 'Orders shipped during March, using shipping date rather than placement date.',
    'A3-11': 'Each sales-detail ID and its discounted line amount: quantity times unit price times one minus discount.',
    'A3-12': 'Mean unit price across sales-detail rows, not the product catalogue list price.',
    'A3-13': 'Number of purchase orders approved during 2006, using approval date.',
    'A3-14': 'Combined shipping charges for orders in June.',
    'A3-15': 'Customers based in New York whose job titles contain Manager.',
    'A3-16': 'Employee display names combining given name with an uppercase surname.',
    'A3-17': 'Short product names with the leading Northwind Traders prefix removed.',
    'A4-01': 'Product rows with the greatest absolute difference between List Price and Standard Cost.',
    'A4-02': 'Best-selling products by the total number of units ordered, retaining tied winners.',
    'A4-03': 'Overall mean catalogue list price across products.',
    'A4-04': 'Mean and standard deviation of product list prices within each category.',
    'A4-05': 'Employee headcount grouped by city.',
    'A4-06': 'Product count grouped by category.',
    'A4-07': 'Product categories ordered by average price from lowest to highest.',
    'A4-08': 'Product names with no matching sales-detail record: products never ordered.',
    'A4-09': 'Order count for each customer ID.',
    'A4-10': 'Employee identifiers tied for the highest number of processed orders.',
    'A4-11': 'Surnames of employees tied for the highest order count.',
    'A4-12': 'Discounted order subtotals obtained by adding the values of their detail lines.',
    'A4-13': 'Order identifiers with discounted subtotals greater than 1500, largest subtotal first.',
    'A4-14': 'All employees with order counts, reporting zero for employees without orders.',
    'A4-15': 'Sales revenue per product with product ID and name.',
    'A4-16': 'Products priced above the overall mean List Price.',
    'A4-17': 'Mean shipping charge per destination city for Closed orders, retaining means at least 100 and sorting ascending.',
    'A4-18': 'Products above their own category mean list price, also showing that category average.',
    'A4-19': 'Average elapsed days from order placement to shipment per employee, excluding unshipped orders.',
    'A4-20': 'Orders with customer company, employee surname, order placement date and readable order status.',
    'SQL6-001': 'Annual customer gross purchase totals and shipping totals for 2006, counting each order fee once and keeping shipping ratios above fifteen percent of positive order value.',
    'SQL6-002': 'Products with more than one hundred units Sold in an individual month of 2006, grouped using inventory transaction creation dates.',
    'SQL6-003': 'Employees with an order in 2006 but no order that year for a same-city customer; outside-year orders do not affect either test.',
    'SQL6-004': 'Customers with at least three different orders and more than three distinct purchased categories across their 2006 orders.',
}


MEASURE_WORDS = {
    'number of orders': ('distinct order count', 'number of separate orders'),
    'total quantity ordered': ('sum of ordered units', 'total units ordered'),
    'total sales value': ('discounted sales revenue', 'net sales amount after line discounts'),
    'number of different products ordered': ('distinct ordered product count', 'number of unique products ordered'),
    'number of different product categories ordered': ('distinct ordered category count', 'number of unique product categories ordered'),
    'number of different customers served': ('distinct customer count', 'number of unique customers served'),
}

REWRITES = [
    (r'\bnumber of different\b', ('count of distinct', 'number of unique')),
    (r'\bnumber of\b', ('count of', 'number of')),
    (r'\bhow many\b', ('the count of', 'the number of')),
    (r'\bcount the\b', ('tally the', 'report the count of')),
    (r'\btotal quantity\b', ('combined quantity', 'total units')),
    (r'\btotal sales(?: value| amount)?\b', ('sales revenue', 'sales amount')),
    (r'\bpayment type\b', ('payment method', 'tender type')),
    (r'\btaxes\b', ('tax charges', 'tax amounts')),
    (r'\bdiscounted (?:line )?revenue\b', ('net line sales amount after discount', 'discounted sales value')),
    (r'\bUnit Price multiplied by Quantity\b', ('Unit Price times Quantity', 'Quantity multiplied by Unit Price')),
    (r'\bShipping Fee\b', ('shipping charge', 'delivery fee')),
    (r'\bList Price\b', ('catalogue price', 'catalog price')),
    (r'\bStandard Cost\b', ('standard purchase cost', 'standard product cost')),
    (r'\baverage\b', ('mean', 'average value')),
    (r'\bdistinct\b', ('unique', 'different')),
    (r'\bprocessed\b', ('handled', 'processed')),
    (r'\bhandled\b', ('processed', 'handled')),
    (r'\bpurchased\b', ('bought', 'purchased')),
    (r'\bshipped\b', ('dispatched', 'shipped')),
    (r'\bnever (?:been )?ordered\b', ('absent from all orders', 'not present in any order')),
    (r'\bwith no orders\b', ('without matching orders', 'with zero orders')),
    (r'\bmore than\b', ('greater than', 'exceeding')),
    (r'\bfewer than\b', ('less than', 'below')),
    (r'\bat least\b', ('no fewer than', 'at least')),
    (r'\bat most\b', ('no more than', 'at most')),
    (r'\b(include|including) ties\b', ('retain all tied rows', 'include every tied row sharing the boundary value')),
    (r'\bdescending\b', ('highest to lowest', 'descending')),
    (r'\bascending\b', ('lowest to highest', 'ascending')),
    (r'\bFor each\b', ('Per', 'For each')),
    (r'\bFind the\b', ('Identify the', 'Retrieve the')),
    (r'\bFind\b', ('Identify', 'Retrieve')),
    (r'\bReturn\b', ('Display', 'Show')),
    (r'\bShow\b', ('Report', 'Display')),
    (r'\bList\b', ('Retrieve', 'Show')),
    (r'\bcalculate\b', ('compute', 'report')),
    (r'\bcompute\b', ('calculate', 'evaluate')),
    (r'^Count(?!\s*\()\b', ('Tally', 'Report the number of')),
    (r'\bProduce\b', ('Generate', 'Prepare')),
    (r'\bsorted? by\b', ('arranged by', 'ordered by')),
    (r'\bversus\b|\bvs\.?', ('compared to', 'versus')),
    (r'\bWhat is the difference between\b', ('How do these differ:', 'Compare')),
    (r'\bWhat (?:is|are)\b', ('Explain', 'Describe')),
    (r'\bWhy (?:does|do)\b', ('Explain why', 'Describe why')),
    (r'\bHow (?:do|does|can) you\b', ('Explain how to', 'Describe how to')),
]

PROTECTED = re.compile(r'(```[\s\S]*?```|`[^`]*`|"[^"\n]*"|\'[^\'\n]*\'|(?m:^\s*(?:SELECT|WITH|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP)\b)[\s\S]*)')
REWRITE_PATTERN = re.compile('|'.join('(?P<rule%d>%s)' % (index, pattern)
                                     for index, (pattern, _) in enumerate(REWRITES)), re.I)


def rewrite(text, style):
    chunks = PROTECTED.split(text)
    for index in range(0, len(chunks), 2):
        chunks[index] = REWRITE_PATTERN.sub(lambda match: REWRITES[int(match.lastgroup[4:])][1][style], chunks[index])
    return ''.join(chunks)


def combo_aliases(question):
    aliases = []
    for measure in MEASURES.values():
        phrase = measure['phrase']
        if phrase not in question:
            continue
        for wording in MEASURE_WORDS[phrase]:
            alias = question.replace(phrase, wording)
            alias = re.sub(r'^For each (.+?), calculate the (.+?)\.', r'Report the \2 for each \1.', alias)
            alias = re.sub(r'^Find the (.+?) whose (.+?) is (.+?)\.', r'Identify the \1 with \2 \3.', alias)
            alias = alias.replace('Consider only orders placed', 'Restrict the calculation to orders placed')
            aliases.append(alias)
        break
    if not aliases:
        aliases = [rewrite(question, style) for style in range(2)]
    return aliases


def enrich_aliases(entry):
    existing = list(entry.get('aliases', []))
    question = entry['question']
    candidates = combo_aliases(question) if entry['id'].startswith('COMBO-') else []
    cue = CURATED.get(entry['id'])
    if cue:
        candidates.append(cue if entry['kind'] == 'theory' else cue + ' ' + question)
    seeds = existing[:2] + [question]
    for style in range(2):
        for seed in seeds + ([cue] if cue else []):
            candidates.append(rewrite(seed, style))
    if entry['kind'] == 'theory':
        summary = re.split(r'(?<=[.!?])\s+(?=[A-Z])', entry['answer'])[0]
        candidates.append(question + ' ' + summary)
    seen = {' '.join(question.lower().split())}
    aliases = []
    for alias in existing + candidates:
        key = ' '.join(alias.lower().split())
        if key and key not in seen:
            seen.add(key)
            aliases.append(alias)
            if len(aliases) >= max(3, len(existing) + 2):
                break
    return aliases
