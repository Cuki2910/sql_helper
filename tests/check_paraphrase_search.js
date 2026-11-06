'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { createEngine, constraints, norm } = require('../js/search');
const bank = require('../data/bank.json');
const engine = createEngine({ entries: bank.entries, schema: require('../data/schema.json') });
const questions = [
  ['SQL6-038', 'Retrieve products priced above the average List Price of their respective categories. Display ID, Product Name, Category, and List Price. Arrange categories alphabetically and show products within each category from highest to lowest price.'],
  ['SQL6-009', 'List every product for which no matching record exists in order details. Display ID, Product Name, Category, and List Price without imposing any price restriction. Arrange the results by ID from smallest to largest.'],
  ['SQL6-039', 'Identify products that were absent from all orders dated in 2006. Retain both products never ordered and products purchased exclusively outside that year. Display ID, Product Name, and Category in ascending ID order.'],
  ['SQL6-036', "Show each customer's ID, First Name, and Last Name together with the dates of their earliest and most recent orders, labelled FirstOrderDate and LatestOrderDate. Keep customers without orders in the output, leaving both dates NULL. Order the results by customer ID ascending."],
  ['SQL6-037', 'Among customers who placed orders in 2006, report customer ID, the number of different orders as TotalOrders, and the number of different products purchased as TotalDistinctProducts. Repeated detail rows must not increase the order count, and purchasing the same product in multiple orders must not increase the distinct product count. Sort by TotalOrders descending, followed by customer ID ascending.'],
  ['SQL6-011', "Retrieve orders where the shipping charge exceeds one-fifth of the order's total value. Compute TotalValue by adding Unit Price multiplied by Quantity for all detail lines, without deducting discounts. Display Order ID, TotalValue, Shipping Fee, and ShippingRatio rounded to four decimal places. Omit orders whose TotalValue is not positive."],
  ['SQL6-040', 'Identify employees who handled orders for customers in at least four different cities during 2006. Show Employee ID, First Name, Last Name, and the number of distinct customer cities as TotalCities. Sort by TotalCities descending, then Employee ID ascending.'],
  ['SQL6-041', 'Identify customers who purchased products from exactly three different categories during 2006. Display customer ID, First Name, Last Name, and TotalCategories. Count each category once per customer, regardless of how many products or orders belong to it.'],
  ['SQL6-042', 'Find employees who handled orders during 2006 exclusively for customers living in cities different from their own. Require each employee to have handled at least one order that year. Exclude employees if their city or the city of any customer they served that year is NULL. Return Employee ID, First Name, and Last Name.'],
  ['TH6-010', "A query joins customers, orders, and order details, then uses COUNT(*) to report each customer's number of orders. Explain why this may overcount orders and how to correct it without removing the order details join."],
  ['TH6-005', "A report must return exactly ten products when at least ten are available, ordered from highest to lowest List Price. Another report must include every product tied at the tenth product's price. Explain why these requirements can produce different row counts and how the SQL approaches should differ."],
  ['SQL6-043', 'List pairs of different products that occurred together in three or more distinct orders placed during 2006. Show the smaller product ID as Product1ID, the larger as Product2ID, and the number of shared orders as OrdersTogether. Return each pair once and sort by OrdersTogether descending, then Product1ID and Product2ID ascending.'],
  ['SQL6-044', 'Find employees who processed orders for at least TWO DIFFERENT customers residing in the SAME city. Return Employee ID, First Name, Last Name, City, and Number of Distinct Customers for each qualifying employee-city combination. Use customers.City (NOT Ship City); exclude NULL cities and count each customer once even if they placed multiple orders.'],
  ['SQL6-044', 'Find employees who served at least two distinct customers living in the same city. For each employee and customer city, return employee ID, first name, last name, city and the distinct customer count. Exclude NULL cities.']
];
for (const [expected, question] of questions) {
  const isTheory = expected.startsWith('TH');
  if (isTheory) {
    assert.equal(engine.search(question, { kind: 'theory' }).results[0]?.id, expected);
    assert.equal(engine.entry(expected).verification.status, 'reference-text');
  }
  for (const filter of isTheory ? [undefined] : [undefined, (match) => match.entry.verification.status === 'execution-verified']) {
    const match = engine.search(question, { limit: 5, filter }).results[0];
    assert(match, `${expected}: no result`);
    assert.equal(match.id, expected, `${expected}: wrong first result`);
    assert.equal(match.nCrit, 0, `${expected}: ${JSON.stringify(match.warnings)}`);
  }
  console.log(`PASS ${expected}`);
}
assert.match(engine.entry('TH6-010').answer, /COUNT\(DISTINCT o\.`Order ID`\)/);
assert.match(engine.entry('TH6-005').answer, /RANK\(\) OVER \(ORDER BY `List Price` DESC\)/);
assert.equal(constraints(questions[4][1]).neg, false);
assert.deepEqual([...constraints(questions[6][1]).cmp], ['>=']);
assert.deepEqual([...constraints(questions[7][1]).cmp], ['=']);
assert.deepEqual([...constraints('shipping charge exceeds one-fifth of TotalValue').nums], ['20']);
assert.equal(norm('from highest to lowest price'), 'descending price');
assert.equal(norm('from smallest to largest'), 'ascending');
assert.equal(norm('orders within one quarter'), 'orders within 1 quarter');
assert.equal(constraints('Products without imposing any price restriction').neg, false);
assert.equal(constraints('Products with no matching record in order details').neg, true);
assert.equal(constraints('Products absent from orders in 2006').neg, true);
assert.equal(constraints(questions[12][1]).neg, false);
assert.equal(constraints('Find employees who did not process orders for customers in the same city.').neg, true);
const changedThreshold = engine.search(questions[5][1].replace('one-fifth', 'one-quarter')).results.find((match) => match.id === 'SQL6-011');
assert(changedThreshold && changedThreshold.warnings.some((warning) => /Number differs/.test(warning.msg)));
for (const name of ['search.js', 'data_bank.js']) {
  assert(fs.readFileSync(path.join(__dirname, '../js', name)).equals(
    fs.readFileSync(path.join(__dirname, '../SQL Reference Finder.app/Contents/Resources/site/js', name))), name);
}
console.log('PASS constraints, threshold warning, packaged app synchronization');
