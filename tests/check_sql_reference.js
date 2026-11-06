const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { execFileSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const context = { window: {} };
vm.runInNewContext(fs.readFileSync(path.join(root, 'js/sql_reference.js'), 'utf8'), context);
const groups = JSON.parse(JSON.stringify(context.window.NW_SQL_REFERENCE));
const entries = groups.flatMap(group => group.entries);
assert.equal(groups.length, 7);
assert.equal(entries.length, 40);
assert.equal(new Set(entries.map(entry => entry.title)).size, entries.length);
const comparisonNumbers = entries.map(entry => /^(\d+)\./.exec(entry.title)).filter(Boolean).map(match => Number(match[1])).sort((left, right) => left - right);
assert.deepEqual(comparisonNumbers, Array.from({ length: 20 }, (_, index) => index + 1));
for (const entry of entries) {
  for (const field of ['title', 'place', 'explanation', 'sql', 'note']) assert(entry[field]?.trim(), `${entry.title}: missing ${field}`);
  for (const statement of entry.sql.split(';').map(value => value.trim()).filter(Boolean)) assert.match(statement, /^(SELECT|WITH)\b/i);
}
for (const keyword of ['OFFSET', 'DATE_FORMAT', 'IS NULL', 'EXISTS', 'DENSE_RANK', 'ROW_NUMBER', 'PARTITION BY', 'STR_TO_DATE', 'UNION ALL', 'COALESCE']) {
  assert(entries.some(entry => entry.sql.includes(keyword)), `Missing ${keyword}`);
}
console.log('SQL reference: 7 groups, 40 examples, all 20 cheat-sheet comparisons present.');

if (process.env.MYSQL_SOCK) {
  const run = sql => execFileSync(process.env.MYSQL_BIN || 'mysql', ['-uroot', '-S', process.env.MYSQL_SOCK, '--default-character-set=utf8mb4', '-N', '-B', 'northwind', '-e', `START TRANSACTION READ ONLY;\n${sql}\nROLLBACK;`], { encoding: 'utf8' }).trim();
  for (const entry of entries) {
    try { run(entry.sql); } catch (error) { throw new Error(`${entry.title}: ${error.message}`); }
  }
  const positions = 'WITH numbers AS (SELECT 1 AS value UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8) SELECT value FROM numbers ORDER BY value';
  assert.equal(run(positions + ' LIMIT 3 OFFSET 5;'), '6\n7\n8');
  assert.equal(run(positions + ' LIMIT 5, 3;'), '6\n7\n8');
  assert.equal(run("SELECT DATE_FORMAT('2006-04-25 12:34:56', '%Y-%m'), DATE_FORMAT('2006-04-25 12:34:56', '%H:%i:%s');"), '2006-04\t12:34:56');
  assert.equal(run('WITH fees AS (SELECT 1 AS ID, 100 AS fee UNION ALL SELECT 2, 100 UNION ALL SELECT 3, 90) SELECT ROW_NUMBER() OVER (ORDER BY fee DESC, ID), RANK() OVER (ORDER BY fee DESC), DENSE_RANK() OVER (ORDER BY fee DESC) FROM fees ORDER BY ID;'), '1\t1\t1\n2\t1\t1\n3\t3\t2');
  assert.equal(run('SELECT 2 NOT IN (1, NULL), NOT EXISTS (SELECT 1 WHERE 1 = 2);'), 'NULL\t1');
  console.log('MySQL: all 40 examples execute read-only; pagination, dates, ranking ties and NULL semantics verified.');
}
