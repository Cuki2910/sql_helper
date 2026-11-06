"""Independent CLI reexecution; no builder imports. Exit nonzero on stale evidence."""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess


def execute(sql):
    completed = subprocess.run(
        [os.environ.get('MYSQL_BIN', 'mysql'), '--user=root',
         '--socket=' + os.environ['MYSQL_SOCK'], '--batch', '--skip-column-names',
         '--default-character-set=utf8mb4', 'northwind'],
        input=sql, text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip())
    return completed.stdout.removesuffix('\n').split('\n') if completed.stdout else []


def digest(rows, comparison='set'):
    payload = rows if comparison == 'ordered' else sorted(rows)
    return hashlib.new('sha1', '\n'.join(payload).encode('utf-8')).hexdigest()[:10]


def audit(bank):
    failures, empty, checked, additional = [], [], 0, 0
    statuses = Counter()
    for entry in bank['entries']:
        if entry['kind'] != 'sql':
            continue
        checked += 1
        metadata = entry['verification']
        statuses[metadata['status']] += 1
        try:
            parts = entry['answer'].split('\n\n-- also asked / related:\n')
            if metadata.get('mode'):  # DML/DDL: run script + state check; DML is rolled back, DDL is cleaned up
                def state(body):
                    if metadata['mode'] == 'rollback':
                        return execute('START TRANSACTION; ' + body + ' ' + metadata['check'] + ' ROLLBACK;')
                    if metadata['cleanup']:
                        try: execute(metadata['cleanup'])
                        except RuntimeError: pass  # object may not exist yet
                    try: return execute(body + ' ' + metadata['check'])
                    finally:
                        if metadata['cleanup']:
                            try: execute(metadata['cleanup'])
                            except RuntimeError: pass
                main, alternative = state(parts[0]), state(entry['alternative'])
            else:
                main = execute(parts[0])
                alternative = execute(entry['alternative'])
            comparison = metadata['comparison']
            if comparison not in ('set', 'ordered'):
                raise ValueError('unknown comparison: ' + comparison)
            expected = dict(rows=len(main), hash=digest(main, comparison), empty=not main)
            for key, value in expected.items():
                if metadata.get(key) != value:
                    raise ValueError('%s stored=%r recomputed=%r' % (key, metadata.get(key), value))
            equal = main == alternative if comparison == 'ordered' else sorted(main) == sorted(alternative)
            if not equal:
                raise ValueError('answer/alternative multiset or sequence mismatch')
            if len(alternative) != metadata['rows'] or digest(alternative, comparison) != metadata['hash']:
                raise ValueError('alternative does not reproduce stored rows/hash')
            if metadata['status'] != 'execution-verified':
                raise ValueError('SQL entry not pair-verified')
            extras = metadata.get('additionalResults', [])
            if len(parts)-1 != len(extras):
                raise ValueError('untracked additional answer statements')
            for query, stored in zip(parts[1:], extras):
                rows = execute(query)
                additional += 1
                if stored != dict(rows=len(rows), hash=digest(rows)):
                    raise ValueError('additional answer result mismatch')
            if not main:
                empty.append(entry['id'])
        except (RuntimeError, KeyError, ValueError) as error:
            failures.append((entry['id'], str(error)))
    print('Independent MySQL CLI audit')
    print('SQL entries:', checked, 'statuses:', dict(statuses))
    print('Main/alternative executions:', checked * 2, 'additional answer executions:', additional)
    print('Empty primary results:', len(empty), ', '.join(empty))
    print('Mismatches:', len(failures))
    for entry_id, message in failures:
        print('MISMATCH', entry_id, message)
    return bool(failures)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, default=Path('data/bank.json'))
    arguments = parser.parse_args()
    raise SystemExit(audit(json.loads(arguments.bank.read_text())))
