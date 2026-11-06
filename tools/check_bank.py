"""New-bank integrity, dedup candidates and structural-alternative review."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
from runpy import run_path


def words(text):
    return re.findall(r'[a-z0-9]+', text.lower())


def normalize(text):
    return ' '.join(words(text))


def features(sql):
    expressions = [r'\bSELECT\b', r'\bJOIN\b', r'\bCROSS JOIN\b', r'\bLEFT JOIN\b',
                   r'\bGROUP BY\b', r'\bHAVING\b', r'\bEXISTS\b', r'\bOVER\s*\(',
                   r'\bWITH\b', r'\bRECURSIVE\b', r'\bCASE\b', r'\bREGEXP\w*\b',
                   r'\bREPLACE\s*\(', r'\bJSON_TABLE\b', r'\bNULLIF\s*\(',
                   r'\bDATE_ADD\s*\(', r'\bTO_DAYS\s*\(', r'\bALL\s*\(', r'\bANY\s*\(']
    return tuple(len(re.findall(expression, sql, re.I)) for expression in expressions)


def check():
    bank = json.loads(Path('data/bank.json').read_text())['entries']
    baseline = json.loads(Path('tools/validation/baseline/bank.json').read_text())['entries']
    old = {entry['id']: entry for entry in baseline}
    new = [entry for entry in bank if entry['id'].startswith(('SQL3-', 'TH3-', 'SQL4-', 'TH4-', 'SQL5-', 'TH5-', 'SQL7-', 'TH6-', 'SQL8-'))]
    errors = []
    print('New entries:', len(new), dict(Counter(entry['kind'] for entry in new)))
    print('Statuses:', dict(Counter(entry['verification']['status'] for entry in new)))
    empty = [entry['id'] for entry in new if entry['verification'].get('empty')]
    print('New empty results:', len(empty), empty)
    assert len([x for x in new if x['id'].startswith(('SQL3-', 'TH3-'))]) == 160
    assert len([x for x in new if x['id'].startswith(('SQL4-', 'TH4-'))]) == 66
    assert len([x for x in new if x['id'].startswith(('SQL5-', 'TH5-'))]) == 67
    assert len([x for x in new if x['id'].startswith('TH6-')]) == 12
    assert len([x for x in new if x['id'].startswith('SQL7-')]) == len(run_path('tools/bank_sql7.py')['SQL7']) == 44
    assert len([x for x in new if x['id'].startswith('SQL8-')]) == len(run_path('tools/bank_sql8.py')['SQL8']) == 12
    assert len({entry['id'] for entry in bank}) == len(bank)
    for entry in new:
        assert entry['source'] == 'authored'
        assert entry['explanation'] if entry['kind'] == 'sql' else 2 <= len(re.split(r'(?<=[.!?])\s+(?=[A-Z])', entry['answer'])) <= 5
        if entry['kind'] == 'sql':
            assert len(entry['techniques']) == 2 and len(set(entry['techniques'])) == 2
            assert entry['verification']['status'] == 'execution-verified'
            if entry['id'].startswith('SQL7-'):
                assert len(entry.get('aliases', [])) >= 2
                assert not entry['verification']['empty']
        else:
            assert ('executed OK' if entry['examples'] else 'no runnable example') in entry['verification']['note']
    preserved = 0
    content_keys = ('kind','source','sourceRef','question','difficulty','pattern','tags','tables','columns','answer','alternative','examples','explanation','mistakes','related')
    for entry in bank:
        if entry['id'] in old:
            if any(entry.get(key) != old[entry['id']].get(key) for key in content_keys):
                errors.append(('existing-content-changed', entry['id']))
            preserved += 1
    print('Existing entry content preserved:', preserved, '/', len(baseline))
    assert preserved == len(baseline)
    original_cases = json.loads(Path('tools/validation/baseline/heldout.json').read_text())
    cases = json.loads(Path('tests/heldout.json').read_text())
    preregistered = json.loads(Path('tools/validation/heldout3_preregistered.json').read_text())
    assert cases == original_cases + preregistered
    print('Held-out prefix unchanged:', len(original_cases), '; preregistered additions unchanged:', len(preregistered))
    assert len([case for case in preregistered if not case.get('trap') and case['cat'] != 'unrelated']) >= (len([x for x in new if x['id'].startswith(('SQL3-', 'TH3-'))])+2)//3  # guard sized to the original 160; round-5 set is tests/heldout_blind2_questions.json
    assert len([case for case in preregistered if case.get('trap')]) >= 15
    assert len([case for case in preregistered if case['cat'] == 'unrelated']) >= 10
    grouped = defaultdict(list)
    for entry in bank:
        grouped[normalize(entry['question'])].append(entry['id'])
    new_ids = {entry['id'] for entry in new}
    duplicates = [group for group in grouped.values() if len(group)>1]
    new_duplicates = [group for group in duplicates if new_ids.intersection(group)]
    print('Normalized duplicate groups: existing', len(duplicates)-len(new_duplicates), 'involving new', len(new_duplicates))
    errors.extend(('new-duplicate', group) for group in new_duplicates)
    normalized = json.loads(subprocess.check_output(['node','-e',
        "const fs=require('fs'),search=require('./js/search');const bank=JSON.parse(fs.readFileSync('data/bank.json')); console.log(JSON.stringify(bank.entries.map(entry=>[entry.id,search.norm(entry.question)])));"], text=True))
    engine_groups = defaultdict(list)
    for entry_id, question in normalized:
        engine_groups[question].append(entry_id)
    engine_duplicates = [group for group in engine_groups.values() if len(group)>1 and new_ids.intersection(group)]
    print('Engine-normalized duplicate groups involving new:', engine_duplicates)
    errors.extend(('new-engine-duplicate', group) for group in engine_duplicates)
    print('Near-text candidates (token Jaccard >= 0.65; manual semantic review required):')
    stop = set('the a an of in to for from is are with and or on as its by show return each every all what how why does do can'.split())
    tokenized = {entry['id']: set(words(entry['question']))-stop for entry in bank}
    seen_pairs = set()
    for entry in new:
        for other in bank:
            if other['id'] == entry['id'] or (entry['kind'] != other['kind']):
                continue
            pair = tuple(sorted((entry['id'],other['id'])))
            if pair in seen_pairs:
                continue
            common = tokenized[entry['id']] & tokenized[other['id']]
            union = tokenized[entry['id']] | tokenized[other['id']]
            similarity = len(common)/len(union) if union else 0
            if similarity >= .65:
                seen_pairs.add(pair)
                print('NEAR', pair, '%.3f' % similarity)
    print('Same nonempty result-hash candidates involving new (intent must be reviewed):')
    hashes = defaultdict(list)
    for entry in bank:
        verification = entry['verification']
        if entry['kind']=='sql' and verification.get('rows',0)>0:
            hashes[verification.get('hash')].append(entry['id'])
    hash_candidates = [group for group in hashes.values() if len(group)>1 and new_ids.intersection(group)]
    for group in hash_candidates:
        print('HASH', group)
    print('Nonempty result-hash candidate groups:', len(hash_candidates))
    structural = [entry['id'] for entry in new if entry['kind']=='sql' and not entry['verification'].get('mode') and features(entry['answer']) == features(entry['alternative'])]  # DML/DDL scripts have no SELECT-shape signature
    print('Identical structural feature signatures:', structural)
    errors.extend(('same-structure-signature', entry_id) for entry_id in structural)
    manifest = json.loads(Path('tools/validation/baseline/files.json').read_text())
    source_paths = [name for name in manifest if name.startswith(('lab/','tools/bank_')) or name in ('tests/eval.js','Northwind-1-1.sql','data/schema.json','data/mock_questions.json','data/lab_questions.json') or name.endswith('.docx')]
    for name in source_paths:
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != manifest[name]:
            errors.append(('protected-file-changed',name))
    print('Protected file hashes checked:', len(source_paths))
    print('Errors:', len(errors))
    for error in errors:
        print('ERROR', error)
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(check())
