'use strict';
const fs = require('fs');
const vm = require('vm');
const path = require('path');
const { createEngine } = require('../js/search.js');

if (process.argv.includes('--original') || process.argv.includes('--baseline')) {
  const originalFs = Object.create(fs);
  originalFs.readFileSync = (filename, ...options) => {
    if (process.argv.includes('--original') && String(filename).endsWith('/tests/heldout.json')) filename = path.resolve('tools/validation/baseline/heldout.json');
    if (process.argv.includes('--baseline') && String(filename).endsWith('/data/bank.json')) filename = path.resolve('tools/validation/baseline/bank.json');
    return fs.readFileSync(filename, ...options);
  };
  vm.runInNewContext(fs.readFileSync('tests/eval.js', 'utf8'), {
    require: (name) => name === 'fs' ? originalFs : name === '../js/search.js' ? require(process.argv.includes('--baseline') ? './validation/baseline/search.js.txt' : '../js/search.js') : require(name),
    __dirname: path.resolve('tests'), process, console, performance
  }, { filename: 'tests/eval.js' });
} else {
  const entries = JSON.parse(fs.readFileSync('data/bank.json', 'utf8')).entries;
  const schema = JSON.parse(fs.readFileSync('data/schema.json', 'utf8'));
  const cases = JSON.parse(fs.readFileSync('tests/heldout.json', 'utf8'));
  const scale = process.argv.includes('--scale');
  const indexed = scale ? [0, 1, 2].flatMap((copy) => entries.map((entry) => ({ ...entry, id: entry.id + ':' + copy }))) : entries;
  const started = performance.now();
  const engine = createEngine({ entries: indexed, schema });
  console.log('Bank:', indexed.length, 'index ms:', (performance.now() - started).toFixed(2));
  const latencies = [];
  for (let pass = 0; pass < 3; pass++) for (const test of cases) {
    const result = engine.search(test.q, { limit: 5 });
    latencies.push(result.ms);
  }
  latencies.sort((first, second) => first - second);
  console.log('Measured searches:', latencies.length, 'mean ms:', (latencies.reduce((sum, value) => sum + value, 0) / latencies.length).toFixed(2),
    'p95 ms:', latencies[Math.floor(latencies.length * 0.95)].toFixed(2), 'max ms:', latencies.at(-1).toFixed(2));
  console.log('Scale:', scale ? 'three copies with distinct IDs; questions unchanged' : 'one copy');
  if (!scale) {
    let returned = 0, warned = 0;
    for (const test of cases.filter((test) => test.trap)) {
      const top = engine.search(test.q, { limit: 1 }).results[0];
      if (top) returned++;
      if (top && top.nCrit) warned++;
      console.log('TRAP TOP', JSON.stringify(test.q), top ? top.id : 'none', 'critical warnings:', top ? top.nCrit : 0,
        'listed avoid:', top ? (test.avoid || []).includes(top.id) : false);
    }
    console.log('Stricter safety view: returned trap tops:', returned, 'with critical warnings:', warned,
      '(not an accuracy metric; unlisted alternatives are not assumed correct)');
  }
}
