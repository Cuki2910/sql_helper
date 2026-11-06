'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { createEngine, constraints, norm, DEFAULT_WEIGHTS } = require('../js/search');
const root = path.join(__dirname, '..');
const load = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const bank = load('data/bank.json');
const engine = createEngine({ entries: bank.entries, schema: load('data/schema.json') });
const writes = [
  ['I am inserting two delivery companies together. What does the multirow statement look like?', 'SQL7-001'],
  ['Archive only the orders dated earlier than March 2006 with an insert from a query.', 'SQL7-002'],
  ['For beverages, updating price by ten percent must also put the reorder point at 30.', 'SQL7-004'],
  ['Deleting products that were never included on an order, preferably with NOT EXISTS.', 'SQL7-011'],
  ['I need REPLACE for a duplicate ID; any unspecified fields should go back to defaults.', 'SQL7-013'],
  ['I want a function for employee names formatted surname comma given name.', 'SQL7-017'],
  ['The function should return the discounted bill for one order and zero if it has no lines.', 'SQL7-019'],
  ['Before inserting a price, a trigger should turn negatives and missing values into zero.', 'SQL7-020'],
  ['On updating a price, the trigger must refuse negatives instead of silently fixing them.', 'SQL7-021'],
  ['A procedure receives a staff number and returns all orders assigned to that person.', 'SQL7-023'],
  ['An order number goes IN to my procedure; its total must come back OUT.', 'SQL7-024'],
  ['Use a cursor to accumulate beverage catalogue prices until there are no more rows.', 'SQL7-026'],
  ['Adding a CHECK should prevent amounts below zero without removing the amount column.', 'SQL7-035'],
  ['Add a foreign key so a child row survives parent deletion with its reference cleared.', 'SQL7-031'],
  ['Transfer funds inside a transaction, undo just the second attempt with a savepoint, then keep the earlier work.', 'SQL7-040'],
];
const reads = [
  'List employee first and last names alphabetically.',
  'Show each order and its discounted total, without defining a routine.',
  'Find the most expensive product in each category.',
  'Show customers who have never placed an order.',
  'Count orders for every employee, including employees with none.',
  'List beverages with List Price above 20.',
  'Show orders placed in January 2006.',
  'Use ROW_NUMBER window function to rank products by price.',
  'Calculate average List Price for each category.',
  'Show the three customers with highest total spending.',
  'List products and their supplier company names.',
  'Count order details belonging to each order.',
  'Show countries with at least two customers.',
  'Find products that were not ordered at all.',
  'Use the SUM aggregate function for revenue per customer.',
];
const known = new Set(bank.entries.flatMap((entry) => [entry.question, ...(entry.aliases || [])]).map(norm));
for (const [question] of writes) assert(!known.has(norm(question)), 'Copied question: ' + question);
const measure = (question) => {
  const result = engine.search(question, { limit: 3 });
  return {
    question, write: result.detected.constraints.write,
    results: result.results.map((match) => ({
      id: match.id, score: match.score, coverage: match.coverage,
      critical: match.nCrit, warnings: match.warnings,
    })),
  };
};
const writeResults = writes.map(([question, expected]) => ({ expected, ...measure(question) }));
const readResults = reads.map(measure);
const summary = {
  top1: writeResults.filter((item) => item.results[0]?.id === item.expected).length,
  top3: writeResults.filter((item) => item.results.some((match) => match.id === item.expected)).length,
  none: writeResults.filter((item) => !item.results.length).length,
  selectToSql7: readResults.filter((item) => item.results[0]?.id.startsWith('SQL7-')).length,
};
if (process.argv.includes('--json')) {
  console.log(JSON.stringify({ summary, writes: writeResults, reads: readResults }, null, 2));
} else {
  for (const item of writeResults) console.log(`${item.expected}\t${item.results[0]?.id || 'NONE'}\t${item.results[0]?.score.toFixed(4) || '-'}\t${item.results.map((match) => match.id).join(',')}\t${item.question}`);
  for (const item of readResults) console.log(`SELECT\t${item.results[0]?.id || 'NONE'}\twrite=${item.write}\t${item.question}`);
  console.log(JSON.stringify(summary));
}
if (!process.argv.includes('--measure')) {
  for (const forms of [['insert', 'inserts', 'inserted', 'inserting'], ['update', 'updates', 'updated', 'updating'], ['delete', 'deletes', 'deleted', 'deleting']]) {
    for (const verb of forms) assert.equal(constraints(`${verb} rows`).write, true, verb);
  }
  for (const verb of ['add', 'adds', 'added', 'adding']) {
    for (const object of ['constraint', 'check', 'index', 'column', 'key', 'rows']) assert.equal(constraints(`${verb} a ${object} to a table`).write, true, `${verb} ${object}`);
  }
  for (const object of ['trigger', 'function', 'procedure', 'cursor', 'savepoint']) assert.equal(constraints(`A ${object} for this task`).write, true, object);
  assert.equal(constraints('Transfer balances within a transaction').write, true);
  for (const question of reads) assert.equal(constraints(question).write, false, question);
  assert.equal(summary.selectToSql7, 0, 'Pure SELECT promoted to SQL7');
  assert.equal(DEFAULT_WEIGHTS.minScore, 0.22);
  assert.equal(DEFAULT_WEIGHTS.minCoverage, 0.45);
  assert.equal(DEFAULT_WEIGHTS.critPenalty, 0.55);
  for (const item of writeResults) assert.equal(item.write, true, item.question);
}
