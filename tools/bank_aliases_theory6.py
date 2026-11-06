"""Retrieval-only paraphrases for TH6 theory entries. Never part of verification."""
ALIASES_TH6 = {
 'TH6-001': ['AND is evaluated before OR; add parentheses to mixed conditions.', 'Why does my OR condition return too many rows in WHERE.'],
 'TH6-002': ['WHERE removes rows while CASE WHEN only labels them or counts conditionally.', 'Difference between filtering rows and computing a category column.'],
 'TH6-003': ['AVG ignores NULL but SUM divided by COUNT star does not; AVG DISTINCT weights.', 'Average of unique values versus average of all non-NULL values.'],
 'TH6-004': ['Total sales must multiply price and quantity per row before SUM.', 'Why SUM of price times SUM of quantity gives a wrong revenue.'],
 'TH6-005': ['Top N with LIMIT drops boundary ties; a threshold subquery or RANK keeps ties at the Nth row, unlike DENSE_RANK for distinct price levels.', 'Exactly N rows versus all rows tied at the Nth value.', "A report must return exactly ten products when at least ten are available, ordered highest to lowest List Price; another report includes every product tied at the tenth product's price.", 'Explain why these requirements produce different row counts and how the SQL approaches should differ.'],
 'TH6-006': ['Get the whole row with the highest value: MAX alone does not show the row.', 'MAX versus ORDER BY DESC LIMIT 1 when several rows tie for the maximum.'],
 'TH6-007': ['Pairs of rows in a self join without mirrored duplicates: less-than versus not-equal.', 'Why id less than id removes (B, A) when (A, B) exists.'],
 'TH6-008': ['OR on one table versus UNION of two selects, duplicate removal.', 'When UNION returns fewer rows than OR because identical rows collapse.'],
 'TH6-009': ['Subquery returns more than 1 row error when using equals instead of IN.', 'Scalar subquery with equals versus IN for several values.'],
 'TH6-010': ['Count customers after a join to orders: COUNT star counts child rows, use COUNT DISTINCT.', 'DISTINCT does not fix double counting from a one-to-many join.', "A query joins customers, orders, and order details, then uses COUNT(*) to report each customer's number of orders: why this may overcount orders and how to correct it without removing the order details join.", 'Retain the detail join and count distinct order IDs per customer instead of counting joined detail rows.'],
 'TH6-011': ['Explicit CAST versus automatic type conversion, effect on index use.', 'Convert text to number or date on purpose, DIV versus decimal division.'],
 'TH6-012': ['GROUP BY gives no sorted result; ORDER BY inside OVER does not sort the output.', 'Window ORDER BY versus final ORDER BY of the query.'],
}
