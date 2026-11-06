// Blind set 3: questions hashed BEFORE any SQL5/TH5 entry or alias was written; entries were written from a measured coverage gap
// (tables, columns, techniques with 0-3 entries). Expected IDs assigned by slug AFTER writing entries. No synonyms/aliases were tuned on this set before the first run.
const fs = require('fs'), path = require('path');
const { createEngine } = require('../js/search.js');
const root = path.join(__dirname, '..');
const bank = JSON.parse(fs.readFileSync(path.join(root, 'data/bank.json'), 'utf8'));
const schema = JSON.parse(fs.readFileSync(path.join(root, 'data/schema.json'), 'utf8'));
const E = { 'order-status-count':['SQL5-001'],'line-status':['SQL5-002'],'po-status':['SQL5-003'],'no-privilege':['SQL5-004'],'emp-privilege':['SQL5-005'],'strings-like':['SQL5-006'],'bottle-like':['SQL5-007'],
 'numeric-prefix':['SQL5-008'],'all-cities':['SQL5-009'],'cities-both':['SQL5-010'],'right-join':['SQL5-012'],'cross-matrix':['SQL5-013'],'payment-null':['SQL5-014'],'job-manager':['SQL5-015'],'weekend':['SQL5-016'],
 'closed-card':['SQL5-017'],'po-approval-days':['SQL5-018'],'po-unpaid':['SQL5-019'],'supplier-two-po':['SQL5-020'],'invoice-before-order':['SQL5-021'],'waste-products':['SQL5-022'],'min-reorder-null':['SQL5-023'] };
const eng = createEngine({ entries: bank.entries, schema });
let n = 0, r1 = 0, r3 = 0, none = 0;
for (const c of JSON.parse(fs.readFileSync(path.join(root, 'tests/heldout_blind3_questions.json'), 'utf8'))) {
  const e = E[c.slug]; n++;
  const ids = eng.search(c.q, { limit: 5 }).results.map((r) => r.id), k = ids.findIndex((x) => e.includes(x));
  if (!ids.length) none++; if (k === 0) r1++; if (k >= 0 && k < 3) r3++;
  if (k !== 0) console.log('MISS', c.slug, '| got', ids[0] || 'none', '| want', e.join('|'), '| rank', k < 0 ? '-' : k + 1);
}
console.log(`blind3 ${n}: R@1 ${r1}/${n}  R@3 ${r3}/${n}  no-answer ${none}`);
