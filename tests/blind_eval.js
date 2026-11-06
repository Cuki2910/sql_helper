// Blind set: 30 paraphrases written from a topic list BEFORE opening aliases. Labels assigned AFTER seeing results (author bias possible).
// expected=[] => no matching bank entry exists (out of scope); any answer then is a wrong answer, reported separately.
const fs = require('fs'), path = require('path');
const { createEngine } = require('../js/search.js');
const root = path.join(__dirname, '..');
const bank = JSON.parse(fs.readFileSync(path.join(root, 'data/bank.json'), 'utf8'));
const schema = JSON.parse(fs.readFileSync(path.join(root, 'data/schema.json'), 'utf8'));
const qs = JSON.parse(fs.readFileSync(path.join(root, 'tests/heldout_blind_questions.json'), 'utf8'));
const exp = {4:['VAR-010','COMBO-1688'],6:['VAR-014'],9:['SQL3-043'],11:['SQL3-040','SQL3-028'],12:['SQL3-051']};
const eng = createEngine({ entries: bank.entries, schema });
let n = 0, r1 = 0, r3 = 0, oos = 0, oosNone = 0, oosWarn = 0;
qs.forEach((q, i) => {
  const out = eng.search(q, { limit: 5 }), ids = out.results.map((r) => r.id), top = out.results[0], e = exp[i + 1];
  if (e) { n++; const k = ids.findIndex((x) => e.includes(x)); if (k === 0) r1++; if (k >= 0 && k < 3) r3++; if (k !== 0) console.log('MISS', i + 1, q, '| got', ids[0] || 'none', '| want', e.join('|'), '| rank', k < 0 ? '-' : k + 1); }
  else { oos++; if (!top) oosNone++; else { if (top.nCrit > 0) oosWarn++; else console.log('OOS-ANSWERED', i + 1, q, '|', top.id); } }
});
console.log(`in-scope ${n}: R@1 ${r1}/${n}  R@3 ${r3}/${n}`);
console.log(`out-of-scope ${oos}: no answer ${oosNone}, answered with warning ${oosWarn}, answered silently ${oos - oosNone - oosWarn}`);
