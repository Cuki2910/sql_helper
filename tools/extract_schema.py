"""Parse Northwind dump -> data/schema.json + js/data_schema.js. Relationships are INFERRED (dump has no FK constraints)
and checked against real data via mysql CLI when MYSQL_SOCK env var is set.
Usage: MYSQL_SOCK=/path/s.sock python3 -I tools/extract_schema.py Northwind-1-1.sql"""
import sys, re, json, os, subprocess
dump = open(sys.argv[1], encoding='utf8').read()
tables = {}
def dump_rows(name):
    total = 0
    for insert in re.finditer(r'INSERT INTO `%s` VALUES(.*?);(?:\r?\n|$)' % re.escape(name), dump, re.S):
        depth = 0
        for token in re.findall(r"'(?:\\.|''|[^'\\])*'|[()]", insert.group(1), re.S):
            if token == '(':
                total += depth == 0
                depth += 1
            elif token == ')':
                depth -= 1
    return total

for m in re.finditer(r'CREATE TABLE `([^`]+)` \((.*?)\n\) ENGINE', dump, re.S):
    name, body = m.group(1), m.group(2)
    cols, pk, idx = [], [], []
    for line in body.split('\n'):
        line = line.strip().rstrip(',')
        c = re.match(r'`([^`]+)` (\S+(?: unsigned)?)(.*)', line)
        if c:
            typ = c.group(2)
            cols.append({'name': c.group(1), 'type': typ, 'nullable': 'NOT NULL' not in c.group(3)})
        elif line.startswith('PRIMARY KEY'):
            pk = re.findall(r'`([^`]+)`', line)
        elif line.startswith('KEY'):
            idx.append(re.findall(r'`([^`]+)`', line))
    for c in cols: c['pk'] = c['name'] in pk
    tables[name] = {'name': name, 'columns': cols, 'primaryKey': pk, 'indexes': idx,
                    'rows': dump_rows(name)}
R = lambda c, cc, p, pc, note='': dict(child=c, childCol=cc, parent=p, parentCol=pc, note=note)
rels = [
 R('orders','Customer ID','customers','ID'), R('orders','Employee ID','employees','ID'),
 R('orders','Shipper ID','shippers','ID'), R('orders','Status ID','orders status','Status ID'),
 R('orders','Tax Status','orders tax status','ID'),
 R('order details','Order ID','orders','Order ID','indexed as FK_Order_OrderDetails_idx but no constraint'),
 R('order details','Product ID','products','ID'), R('order details','Status ID','order details status','Status ID'),
 R('order details','Purchase Order ID','purchase orders','Purchase Order ID'),
 R('order details','Inventory ID','inventory transactions','Transaction ID'),
 R('inventory transactions','Transaction Type','inventory transaction types','ID','NO column named Status; use Transaction Type -> Type Name (Sold = 2)'),
 R('inventory transactions','Product ID','products','ID'),
 R('inventory transactions','Customer Order ID','orders','Order ID'),
 R('inventory transactions','Purchase Order ID','purchase orders','Purchase Order ID'),
 R('purchase order details','Purchase Order ID','purchase orders','Purchase Order ID'),
 R('purchase order details','Product ID','products','ID'),
 R('purchase order details','Inventory ID','inventory transactions','Transaction ID'),
 R('purchase orders','Supplier ID','suppliers','ID'), R('purchase orders','Created By','employees','ID'),
 R('purchase orders','Approved By','employees','ID'), R('purchase orders','Submitted By','employees','ID'),
 R('purchase orders','Status ID','purchase order status','Status ID'),
 R('invoices','Order ID','orders','Order ID'),
 R('employee privileges','Employee ID','employees','ID'), R('employee privileges','Privilege ID','privileges','Privilege ID'),
]
sock = os.environ.get('MYSQL_SOCK')
def q(sql):
    r = subprocess.run(['mysql', '-uroot', '-S' + sock, '-N', '-B', 'northwind', '-e', sql], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return r.stdout.strip()
for r in rels:
    c, cc, p, pc = r['child'], r['childCol'], r['parent'], r['parentCol']
    pj = f"JOIN `{p}` pp ON pp.`{pc}` = cc.`{cc}`"
    r['example'] = f"SELECT *\nFROM `{c}` AS c\nJOIN `{p}` AS p ON c.`{cc}` = p.`{pc}`;".replace('FROM `%s` AS c' % c, 'FROM `%s` AS c' % c)
    if sock:
        tot = int(q(f"SELECT COUNT(*) FROM `{c}` WHERE `{cc}` IS NOT NULL"))
        orphan = int(q(f"SELECT COUNT(*) FROM `{c}` cc WHERE cc.`{cc}` IS NOT NULL AND NOT EXISTS (SELECT 1 FROM `{p}` pp WHERE pp.`{pc}` = cc.`{cc}`)"))
        dup = int(q(f"SELECT COUNT(*) FROM (SELECT `{pc}` FROM `{p}` GROUP BY `{pc}` HAVING COUNT(*)>1) t"))
        r['check'] = {'childNonNull': tot, 'orphans': orphan, 'parentKeyDuplicates': dup}
        r['dataVerified'] = tot > 0 and orphan == 0 and dup == 0
        q(r['example'].rstrip(';') + ' LIMIT 1')  # example must run
    else:
        r['dataVerified'] = None
out = {'database': 'northwind', 'source': os.path.basename(sys.argv[1]), 'tables': list(tables.values()), 'relationships': rels,
       'notes': ['The dump declares NO foreign-key constraints; relationships are inferred from names and checked against the data (see check/dataVerified).',
                 'Identifiers contain spaces, "/" and "-": always quote with backticks in MySQL.',
                 '`products`.`Supplier IDs` is a text list, not a clean foreign key.',
                 '`orders status` and `orders tax status` have no primary key.']}
json.dump(out, open('data/schema.json', 'w'), indent=1)
open('js/data_schema.js', 'w').write('window.NW_SCHEMA = ' + json.dumps(out) + ';\n')
bad = [r for r in rels if r['dataVerified'] is False]
print(len(tables), 'tables', len(rels), 'relationships;', 'not data-verified:', [(r['child'], r['childCol']) for r in bad])
