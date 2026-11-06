// Usage: node tests/eval.js [-v]   (also used by tests/index.html through the same logic)
// Held-out set (tests/heldout.json) is NOT part of the searchable bank. Written by the developer, so it measures
// regression and robustness to rewording, NOT accuracy on a real exam.
const fs = require('fs'), path = require('path');
const { createEngine } = require('../js/search.js');
const root = path.join(__dirname, '..');
const bank = JSON.parse(fs.readFileSync(path.join(root, 'data/bank.json'), 'utf8'));
const schema = JSON.parse(fs.readFileSync(path.join(root, 'data/schema.json'), 'utf8'));
const cases = JSON.parse(fs.readFileSync(path.join(root, 'tests/heldout.json'), 'utf8'));
const verbose = process.argv.includes('-v');

const bankQs = new Set(bank.entries.map((e) => e.question.toLowerCase().trim()));
for (const c of cases) c.expected = c.expected.map((x) => { if (x[0] !== '@') return x; const hit = bank.entries.find((e) => e.question === x.slice(1)); if (!hit) { console.error('UNRESOLVED expected:', x); process.exit(3); } return hit.id; });
const leak = cases.filter((c) => bankQs.has(c.q.toLowerCase().trim()));
if (leak.length) { console.error('HELD-OUT LEAK:', leak.map((c) => c.q)); process.exit(2); }

const eng = createEngine({ entries: bank.entries, schema });
let sameRes = 0, n = 0, r1 = 0, r3 = 0, mrr = 0, wrongTop = 0, wrongNoWarn = 0, answered = 0, lat = [], unrelatedFP = 0, unrelated = 0, trapOk = 0, traps = 0, trapSilent = 0;
const byCat = {}, fails = [];
for (const c of cases) {
  const out = eng.search(c.q, { limit: 5 }); lat.push(out.ms);
  const ids = out.results.map((r) => r.id), top = out.results[0];
  const cat = (byCat[c.cat] = byCat[c.cat] || { n: 0, r1: 0 });
  if (c.cat === 'unrelated') { unrelated++; if (top) { unrelatedFP++; fails.push(['FALSE MATCH', c.q, ids[0]]); } continue; }
  if (c.trap) {
    traps++;
    const ok = !top || top.nCrit > 0 || !(c.avoid || []).includes(top.id);
    if (ok) trapOk++; else { trapSilent++; fails.push(['TRAP SILENT', c.q, ids[0], top.entry.question]); }
    continue;
  }
  n++; cat.n++;
  const rank = ids.findIndex((id) => c.expected.includes(id));
  if (rank !== 0 && top) { const h = (x) => x && x.verification && x.verification.hash; const eh = c.expected.map((i) => h(bank.entries.find((x) => x.id === i))).filter(Boolean); if (h(top.entry) && eh.includes(h(top.entry))) sameRes++; }
  if (rank === 0) { r1++; cat.r1++; } else fails.push(['MISS@1', c.q, 'got ' + (ids[0] || 'none'), 'want ' + c.expected.join('|'), 'rank ' + (rank < 0 ? '-' : rank + 1)]);
  if (rank >= 0 && rank < 3) r3++;
  if (rank >= 0) mrr += 1 / (rank + 1);
  if (top) { answered++; if (rank !== 0) { wrongTop++; if (!top.nCrit) wrongNoWarn++; } }
}
lat.sort((a, b) => a - b);
const pct = (a, b) => (b ? (100 * a / b).toFixed(1) + '%' : 'n/a');
console.log(`bank entries: ${eng.size()}   held-out cases: ${cases.length} (${n} scored retrieval, ${traps} traps, ${unrelated} unrelated)`);
console.log(`Recall@1: ${pct(r1, n)} (${r1}/${n})   Recall@3: ${pct(r3, n)}   MRR: ${(mrr / n).toFixed(3)}`);
console.log(`Incorrect top match (answered but wrong): ${pct(wrongTop, answered)} (${wrongTop}/${answered})`);
console.log(`  of which with NO critical-constraint warning: ${wrongNoWarn}`);
console.log(`  (info) strict misses whose top entry has the identical verified result set as an expected entry: ${sameRes}`);
console.log(`Trap cases (similar wording, different requirement) handled (no match or critical warning): ${trapOk}/${traps}; silent wrong: ${trapSilent}`);
console.log(`Unrelated questions wrongly answered: ${unrelatedFP}/${unrelated}`);
console.log(`Latency ms: mean ${(lat.reduce((a, b) => a + b, 0) / lat.length).toFixed(2)}  p95 ${lat[Math.floor(lat.length * 0.95)].toFixed(2)}  max ${lat[lat.length - 1].toFixed(2)}`);
console.log('Per category Recall@1:', Object.entries(byCat).filter(([, v]) => v.n).map(([k, v]) => `${k} ${v.r1}/${v.n}`).join(' | '));
if (verbose || fails.length) { console.log('\nFailures:'); fails.forEach((f) => console.log(' ', f.join(' | '))); }
