'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { createEngine, constraints, norm } = require('../js/search');
const root = path.join(__dirname, '..');
const load = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const bank = load('data/bank.json');
const added = bank.entries.filter((entry) => entry.id.startsWith('SQL7-'));
assert.equal(added.length, 44);
for (const entry of added) {
  assert.equal(entry.verification.status, 'execution-verified', entry.id);
  assert.equal(entry.verification.empty, false, entry.id);
  assert(entry.aliases.length >= 2, entry.id);
  assert.notEqual(norm(entry.answer), norm(entry.alternative), entry.id);
  assert.equal(constraints(entry.question).write, Number(entry.id.slice(5)) <= 40, entry.id);
  if (/START TRANSACTION/i.test(entry.answer)) assert.equal(entry.verification.mode, 'ddl', entry.id);
  if (entry.verification.mode === 'ddl') assert(entry.verification.cleanup, entry.id);
  if (entry.id === 'SQL7-040') {
    for (const body of [entry.answer, entry.alternative]) assert.match(body, /EXIT HANDLER FOR SQLEXCEPTION BEGIN ROLLBACK; RESIGNAL;/);
  }
}
assert.equal(bank.entries.filter((entry) => /^TH5-00[5-9]$|^TH5-010$/.test(entry.id)).length, 6);

const engine = createEngine({ entries: bank.entries, schema: load('data/schema.json') });
const bankQuestions = new Set(bank.entries.flatMap((entry) => [entry.question, ...(entry.aliases || [])]).map(norm));
const cases = [
  ['Insert Training A at 99001 and Training B at 99002 into shippers together, not with two separate statements.', 'SQL7-001'],
  ['Use INSERT SELECT to archive only orders earlier than 2006-03-01 into zz_archive.', 'SQL7-002'],
  ['Update the Beverages category to multiply List Price by 1.10 and replace Reorder Level with 30.', 'SQL7-004'],
  ['Update every product with CASE so price >= 30 means reorder 40 and target 80, otherwise reorder 10 and target 20.', 'SQL7-005'],
  ['Use a WHERE subquery in UPDATE to assign reorder 50 to products included in orders before March 2006.', 'SQL7-007'],
  ['Update Target Level to 200 by joining products to a grouped query having three distinct order IDs or more.', 'SQL7-008'],
  ['Delete from zz_products every product for which no order detail exists.', 'SQL7-011'],
  ['Replace scratch carrier key 1 with Replacement, resetting its old note through the omitted default.', 'SQL7-013'],
  ['Truncate the copied carrier table before inserting again so its AUTO_INCREMENT sequence restarts.', 'SQL7-016'],
  ['Create a full-name function joining trimmed employee Last Name and First Name with comma space.', 'SQL7-017'],
  ['Create a before-update price trigger that signals 45000 rather than accepting NULL or negative prices.', 'SQL7-021'],
  ['Create a procedure taking an order ID IN and returning discounted revenue OUT, then CALL for the minimum order key.', 'SQL7-024'],
  ['Create a cursor procedure fetching Beverages List Price values into an accumulated OUT total.', 'SQL7-026'],
  ['Create a child table with AUTO_INCREMENT key, amount DEFAULT 0 and CHECK, and a cascading parent foreign key.', 'SQL7-030'],
  ['Start a transaction with SAVEPOINT to retain a transfer of 10 while rolling back an insufficient-funds transfer of 200.', 'SQL7-040'],
];
let correct = 0;
for (const [question, expected] of cases) {
  assert(!bankQuestions.has(norm(question)), 'Regression question copied from bank');
  const top = engine.search(question, { limit: 5 }).results[0];
  const matched = top && top.id === expected;
  if (matched) correct++;
  assert(!top || constraints(top.entry.question).write || top.warnings.some((warning) => warning.sev === 'critical' && /CHANGES data or structure/.test(warning.msg)), question);
  console.log(`${matched ? 'PASS' : 'MISS'} ${expected}: ${top ? top.id : 'none'}; critical=${top ? top.nCrit : 0}`);
}
console.log(`SQL7 retrieval regression: ${correct}/${cases.length}; silent write mismatch: 0`);
assert(correct >= 13, 'SQL7 retrieval regression below 13/15');

const readOnly = bank.entries.filter((entry) => entry.kind === 'sql' && !constraints(entry.question).write);
const retrievalEngine = createEngine({ entries: readOnly, schema: load('data/schema.json') });
for (const question of ['Replace shippers rows', 'Truncate a table', 'Create a stored function', 'Create a procedure', 'Create a trigger', 'Start a transaction', 'Commit the transfer', 'Rollback the transaction']) {
  assert.equal(constraints(question).write, true, question);
  const top = retrievalEngine.search(question, { limit: 1 }).results[0];
  assert(!top || top.warnings.some((warning) => warning.sev === 'critical' && /CHANGES data or structure/.test(warning.msg)), question);
}
console.log('PASS write-intent warnings with retrieval-only candidates');
