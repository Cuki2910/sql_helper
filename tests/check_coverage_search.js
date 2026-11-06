'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { createEngine, constraints, norm } = require('../js/search');
const bank = require('../data/bank.json');
const schema = require('../data/schema.json');
const engine = createEngine({ entries: bank.entries, schema });
const entries = bank.entries.filter((entry) => entry.id.startsWith('SQL8-'));
assert.equal(entries.length, 12);
assert.equal(new Set(entries.map((entry) => JSON.stringify([
  entry.tables, entry.coverage.groupBy, entry.coverage.measures
]))).size, 12);
assert.equal(constraints('Count orders, not distinct customers.').neg, false);
assert.equal(constraints('Count orders, not customers without orders.').neg, true);
assert.equal(constraints('Find employees who did not process orders.').neg, true);
assert.equal(constraints('Count orders, not distinct customers.').distinctOf, 'order');
assert.equal(constraints('Count distinct orders.').distinctOf, 'order');
for (const entry of entries) {
  assert.equal(entry.verification.status, 'execution-verified', entry.id);
  assert.equal(entry.sourceRef, 'tools/bank_sql8.py', entry.id);
  assert(entry.coverage.groupBy.length && entry.coverage.measures.length, entry.id);
  assert.equal(bank.entries.filter((other) => norm(other.question) === norm(entry.question)).length, 1, entry.id);
  assert(entry.aliases.length >= 2, entry.id);
}
const questions = [
  ['SQL8-001', 'Find employees with at least two orders for customers in the same residence city. Report employee ID, first name, last name, customer City and TotalOrders for each employee-city group. Exclude NULL cities and count orders, not distinct customers.'],
  ['SQL8-002', 'Identify employee and Ship City groups with at least two different customers. Return employee ID, first name, last name, shipping destination city and TotalCustomers. Use the destination on orders rather than the city where customers live, excluding NULL destinations.'],
  ['SQL8-003', 'Identify employee-category combinations that served at least two different customers in 2006. Return employee ID, first name, last name, product category and TotalCustomers. Exclude NULL categories and deduplicate customers across orders and line items.'],
  ['SQL8-004', 'Identify customers purchasing at least two different products within the same category. Return customer ID, company, category and TotalProducts for every customer-category group. Exclude NULL categories; repeated purchases count a product once.'],
  ['SQL8-005', 'Identify shipper and customer City groups with at least two different customers. Return shipper ID, company, residence city and TotalCustomers. Exclude NULL customer cities. Include orders without detail lines.'],
  ['SQL8-006', 'Identify supplier-category combinations from actual purchase orders with at least two different products. Return supplier ID, company, product category and TotalProducts. Exclude NULL categories and deduplicate products across purchase details.'],
  ['SQL8-007', 'Identify employees who created at least two purchase orders for the same supplier. Return creator employee ID, first name, last name, supplier ID, company and TotalPurchaseOrders for each creator-supplier pair. Use Created By. Include purchase orders without detail lines.'],
  ['SQL8-008', 'Show each supplier with purchase order count, total shipping fees and total quantity times unit cost. Include suppliers without purchase orders and purchase orders without lines, with zero totals. Count shipping once per purchase order even when several details exist.'],
  ['SQL8-009', 'Show each employee-customer combination with its order count and discounted sales total. Include orders without detail lines with zero sales; count an order once. Compute Quantity times Unit Price times (1 - Discount), treating NULL Discount as zero.'],
  ['SQL8-010', 'Show every employee with the number of distinct valid assigned privileges as TotalPrivileges. Include employees with no valid privileges with zero. Ignore repeated bridge rows and privilege IDs missing from the privileges lookup.'],
  ['SQL8-011', 'Show every order detail status with TotalLines and TotalOrders, counting different orders separately from detail lines. Include statuses with no lines using zeros. Ignore NULL Order IDs in the order count. Return status ID and status name.'],
  ['SQL8-012', 'Summarize inventory movements during 2006 by transaction type and product category. Return type ID, type name, category, distinct product count and total quantity. Use Transaction Created Date and exclude NULL categories; keep each movement type separate.']
];
const failures = [];
for (const [expected, question] of entries.map((entry) => [entry.id, entry.question]).concat(questions)) {
  for (const filter of [undefined, (match) => match.entry.verification.status === 'execution-verified']) {
    const match = engine.search(question, { limit: 5, filter }).results[0];
    if (match?.id !== expected || match.nCrit !== 0) {
      failures.push({ expected, got: match?.id, warnings: match?.warnings, question });
    }
  }
}
assert.deepEqual(failures, [], JSON.stringify(failures, null, 2));
const packagedRoot = path.join(__dirname, '../SQL Reference Finder.app/Contents/Resources/site/js');
for (const name of ['search.js', 'data_bank.js']) {
  assert(fs.readFileSync(path.join(__dirname, '../js', name)).equals(fs.readFileSync(path.join(packagedRoot, name))), name);
}
const packaged = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(packagedRoot, 'data_bank.js'), 'utf8'), packaged);
assert.equal(packaged.window.NW_BANK.entries.filter((entry) => entry.id.startsWith('SQL8-')).length, 12);
console.log('PASS 12 coverage entries, 24 exact/paraphrased questions, both verification filters, packaged app');
