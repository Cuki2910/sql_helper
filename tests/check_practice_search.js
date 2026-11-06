'use strict';
const assert = require('assert/strict');
const fs = require('fs');
const path = require('path');
const { createEngine, norm } = require('../js/search');
const root = path.join(__dirname, '..');
const load = (name) => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
const bank = load('data/bank.json');
const engine = createEngine({ entries: bank.entries, schema: load('data/schema.json') });
const questions = load('tests/practice_questions.json');
assert.equal(questions.length, 12);
const added = bank.entries.filter((entry) => entry.id.startsWith('SQL6-'));
assert.equal(added.length, 44);
for (const entry of added) {
  assert.equal(entry.verification.status, 'execution-verified', entry.id);
  assert.equal(bank.entries.filter((other) => norm(other.question) === norm(entry.question)).length, 1, entry.id);
}
for (const question of questions) {
  const result = engine.search(question.q, {
    limit: 5,
    filter: (match) => match.entry.verification.status === 'execution-verified'
  }).results[0];
  assert(result, `Q${question.no}: no result`);
  assert.equal(result.id, question.expected, `Q${question.no}: wrong first result`);
  assert.equal(result.nCrit, 0, `Q${question.no}: ${JSON.stringify(result.warnings)}`);
  console.log(`PASS Q${question.no}: ${result.id}`);
}
