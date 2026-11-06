// Blind set 2: questions preregistered (sha256 in VALIDATION_REPORT) BEFORE any SQL4/TH4 entry existed. Expected IDs map slug -> entry written for that gap.
// null = topic deliberately not covered by any entry. Author knew the gap list when writing the entries, so this is NOT an independent exam sample.
const fs = require('fs'), path = require('path');
const { createEngine } = require('../js/search.js');
const root = path.join(__dirname, '..');
const bank = JSON.parse(fs.readFileSync(path.join(root, 'data/bank.json'), 'utf8'));
const schema = JSON.parse(fs.readFileSync(path.join(root, 'data/schema.json'), 'utf8'));
const E = { 'top3-category':['SQL4-001'],'share-customer':['SQL4-005'],'running-orders':null,'running-revenue':['SQL4-009'],'above-avg-order':['SQL4-012'],'above-avg-employee':['SQL4-013'],
 'gap-minmax':['SQL4-016'],'pivot-year':['SQL4-018'],'shipper-timely':['SQL4-019'],'q1-anti':['SQL4-025'],'rank-supplier':['SQL4-022'],'both-extremes':['SQL4-020'],'multi-city':['SQL4-028'],
 'avg-lines':['SQL4-021'],'po-shortfall':['SQL4-034'],'reorder-stock':['SQL4-015'],'same-city':['SQL4-029'],'top-shipper-fee':['SQL4-008'],'null-ship-share':['SQL4-007'],'median':['SQL4-024','TH3-039'],
 'ntile':['SQL4-033'],'group-concat':['SQL4-032'],'first-order':['SQL4-011'],'dml-insert':['SQL4-048'],'dml-update':['SQL4-049'],'dml-delete':['SQL4-050'],'ddl-view':['SQL4-055'],'ddl-ctas':['SQL4-054'],
 'dml-upsert':['SQL4-052'],'dml-dups':['SQL4-053'] };
const eng = createEngine({ entries: bank.entries, schema });
let n = 0, r1 = 0, r3 = 0, none = 0;
for (const c of JSON.parse(fs.readFileSync(path.join(root, 'tests/heldout_blind2_questions.json'), 'utf8'))) {
  const e = E[c.slug]; if (!e) continue; n++;
  const ids = eng.search(c.q, { limit: 5 }).results.map((r) => r.id), k = ids.findIndex((x) => e.includes(x));
  if (!ids.length) none++; if (k === 0) r1++; if (k >= 0 && k < 3) r3++;
  if (k !== 0) console.log('MISS', c.slug, '| got', ids[0] || 'none', '| want', e.join('|'), '| rank', k < 0 ? '-' : k + 1);
}
console.log(`blind2 in-scope ${n}: R@1 ${r1}/${n}  R@3 ${r3}/${n}  no-answer ${none}`);
