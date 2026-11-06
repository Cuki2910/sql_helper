"""Alias coverage, deterministic generation and preservation of protected requirements."""
import copy
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from bank_aliases_auto import PROTECTED, combo_aliases, enrich_aliases, rewrite

bank = json.loads((ROOT / 'data/bank.json').read_text())
variants = []
total = 0
for entry in bank['entries']:
    aliases = entry.get('aliases', [])
    assert len(aliases) >= 2, entry['id']
    normalized = [' '.join(alias.lower().split()) for alias in aliases]
    assert len(set(normalized)) == len(normalized), entry['id']
    assert ' '.join(entry['question'].lower().split()) not in normalized, entry['id']
    total += len(aliases)
    snapshot = copy.deepcopy(entry)
    assert enrich_aliases(entry) == enrich_aliases(entry), entry['id']
    assert entry == snapshot, entry['id']
    generated = [rewrite(entry['question'], style) for style in range(2)]
    if entry['id'].startswith('COMBO-'):
        generated += combo_aliases(entry['question'])
    protected = PROTECTED.findall(entry['question'])
    numbers = re.findall(r'\d+(?:\.\d+)?', entry['question'])
    operators = re.findall(r'<>|!=|>=|<=|[<>=%]', entry['question'])
    for alias in generated:
        assert all(text in alias for text in protected), (entry['id'], alias)
        assert re.findall(r'\d+(?:\.\d+)?', alias) == numbers, (entry['id'], alias)
        assert re.findall(r'<>|!=|>=|<=|[<>=%]', alias) == operators, (entry['id'], alias)
    variants.append({'id': entry['id'], 'question': entry['question'], 'variants': generated})

script = r"""
const assert = require('assert/strict');
const { constraints } = require('./js/search');
const variants = JSON.parse(require('fs').readFileSync(0, 'utf8'));
const fields = ['cmp', 'extreme', 'neg', 'tiesIncl', 'tiesExcl', 'gtAll', 'gtAny', 'every',
  'perMonth', 'years', 'months', 'nums', 'write', 'perCat', 'status',
  'nullIncl', 'nullExcl', 'nullMention', 'asc', 'desc'];
const serial = (value) => value instanceof Set ? [...value].sort() : value;
for (const entry of variants) {
  const original = constraints(entry.question);
  for (const alias of entry.variants) {
    const actual = constraints(alias);
    for (const field of fields) {
      assert.deepEqual(serial(actual[field]), serial(original[field]), `${entry.id}: ${field}: ${alias}`);
    }
  }
}
console.log('PASS generated paraphrases preserve recognized conditions');
"""
subprocess.run(['node', '-e', script], input=json.dumps(variants), text=True, cwd=ROOT, check=True)
print('PASS %d entries, %d aliases, protected SQL/literals/numbers/operators unchanged' % (len(variants), total))
