"""Combinatorial question generator: subject x measure x form x date window.
Every candidate gets a main query and a structurally different alternative (derived table / window function /
anti-join rewrite). build_bank.py executes both; candidates that fail, differ, return nothing, or filter nothing are dropped
and listed in data/combo_report.txt. Thresholds come from the real value distribution so results are informative.
NOTE: for list/HAVING forms the alternative is a structural rewrite (derived table), weaker evidence than a hand-written
independent formulation: documented in README."""

BASE = "FROM orders o\nJOIN `order details` od ON od.`Order ID` = o.`Order ID`\nJOIN products p ON p.ID = od.`Product ID`"

SUBJECTS = {
 'customer': dict(sing='customer', plur='customers', join="\nJOIN customers c ON c.ID = o.`Customer ID`", keys=['c.ID', 'c.Company'], tie='ID',
                  outer="customers c", corr="o.`Customer ID` = c.ID", verb='placed no orders', verb_pos='placed at least one order'),
 'employee': dict(sing='employee', plur='employees', join="\nJOIN employees e ON e.ID = o.`Employee ID`", keys=['e.ID', 'e.`Last Name`'], tie='ID',
                  outer="employees e", corr="o.`Employee ID` = e.ID", verb='processed no orders', verb_pos='processed at least one order'),
 'shipper': dict(sing='shipper', plur='shippers', join="\nJOIN shippers s ON s.ID = o.`Shipper ID`", keys=['s.ID', 's.Company'], tie='ID',
                 outer="shippers s", corr="o.`Shipper ID` = s.ID", verb='shipped no orders', verb_pos='shipped at least one order'),
 'ship city': dict(sing='ship city', plur='ship cities', join="", keys=['o.`Ship City`'], tie='city name', outer=None, corr=None, verb=None, verb_pos=None),
 'product': dict(sing='product', plur='products', join="", keys=['p.ID', 'p.`Product Name`'], tie='ID',
                 outer="products p", corr="od.`Product ID` = p.ID", verb='were not ordered', verb_pos='were ordered at least once'),
 'category': dict(sing='product category', plur='product categories', join="", keys=['p.Category'], tie='category name', outer=None, corr=None, verb=None, verb_pos=None),
}
SALES = "ROUND(SUM(od.Quantity * od.`Unit Price` * (1 - od.Discount)), 2)"
MEASURES = {
 'orders':     dict(expr="COUNT(DISTINCT o.`Order ID`)", phrase='number of orders', tags=['count distinct', 'orders'], skip={}),
 'quantity':   dict(expr="SUM(od.Quantity)", phrase='total quantity ordered', tags=['sum', 'quantity'], skip={}),
 'sales':      dict(expr=SALES, phrase='total sales value', tags=['sum', 'sales value'], skip={}),
 'products':   dict(expr="COUNT(DISTINCT od.`Product ID`)", phrase='number of different products ordered', tags=['count distinct', 'products'], skip={'product'}),
 'categories': dict(expr="COUNT(DISTINCT p.Category)", phrase='number of different product categories ordered', tags=['count distinct', 'categories'], skip={'product', 'category'}),
 'customers':  dict(expr="COUNT(DISTINCT o.`Customer ID`)", phrase='number of different customers served', tags=['count distinct', 'customers'], skip={'customer'}),
}
OPS = [('more than', '>'), ('at least', '>='), ('fewer than', '<'), ('at most', '<='), ('exactly', '=')]
WINDOWS = [  # key, phrase, SQL condition
 ('all', '', None),
 ('mar', 'in March 2006', "o.`Order Date` >= '2006-03-01' AND o.`Order Date` < '2006-04-01'"),
 ('apr', 'in April 2006', "o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-05-01'"),
 ('q1', 'in the first quarter of 2006 (January to March)', "o.`Order Date` >= '2006-01-01' AND o.`Order Date` < '2006-04-01'"),
 ('q2', 'in the second quarter of 2006 (April to June)', "o.`Order Date` >= '2006-04-01' AND o.`Order Date` < '2006-07-01'"),
]

def _parts(sub, mea, cond):
    S = SUBJECTS[sub]; M = MEASURES[mea]['expr']
    where = f"\nWHERE {cond}" if cond else ""
    keys = ', '.join(S['keys'])
    base = BASE + S['join'] + where
    inner = f"SELECT {', '.join(f'{k} AS k{i+1}' for i, k in enumerate(S['keys']))}, {M} AS m\n{base}\nGROUP BY {keys}"
    kn = ', '.join(f'k{i+1}' for i in range(len(S['keys'])))
    return S, M, base, keys, inner, kn

def _suffix(w):
    return f" Consider only orders placed {w[1]}." if w[1] else ""

def _quantile_thresholds(vals, mea):
    vs = sorted(set(vals))
    if len(vs) < 3: return []
    picks = [vs[len(vs) // 3], vs[(2 * len(vs)) // 3]]
    out = []
    for v in picks:
        v = float(v)
        if mea == 'sales': v = max(100, round(v / 100) * 100)
        elif mea == 'quantity': v = max(10, round(v / 10) * 10)
        else: v = int(v)
        if v not in out: out.append(v)
    return out

def generate(run):
    out = []
    def add(**kw): out.append(kw)
    for sub in SUBJECTS:
        S = SUBJECTS[sub]
        for mea, Mm in MEASURES.items():
            if sub in Mm['skip']: continue
            ph = Mm['phrase']
            for w in WINDOWS:
                cond = w[2]
                S_, M, base, keys, inner, kn = _parts(sub, mea, cond)
                sfx = _suffix(w)
                tag_w = ['date', 'range'] if cond else []
                # distribution for thresholds
                rows, err = run(f"SELECT m FROM ({inner}) t")
                vals = [float(x) for x in (rows or [])]
                ths = _quantile_thresholds(vals, mea)
                # 1. per-subject list
                add(q=f"For each {S['sing']}, calculate the {ph}.{sfx}",
                    sql=f"SELECT {keys}, {M} AS m\n{base}\nGROUP BY {keys};", alt=f"SELECT {kn}, m FROM (\n{inner}) t;",
                    cmp='set', pattern='multi_agg', diff=3, tags=['group by', 'join', S['sing'], *Mm['tags'], *tag_w], allow_all=True,
                    why=f"Join chain orders -> order details -> products{' -> ' + sub if S['join'] else ''}; aggregate per {S['sing']}.", form='list', sub=sub, mea=mea, w=w[0])
                # 2. HAVING with every comparison operator
                for n in ths:
                    for opw, op in OPS:
                        nn = f"{n:g}" if isinstance(n, float) else str(n)
                        add(q=f"Find the {S['plur']} whose {ph} is {opw} {nn}.{sfx}",
                            sql=f"SELECT {keys}, {M} AS m\n{base}\nGROUP BY {keys}\nHAVING {M} {op} {nn};",
                            alt=f"SELECT {kn}, m FROM (\n{inner}) t\nWHERE m {op} {nn};",
                            cmp='set', pattern='group_having', diff=4, tags=['having', opw, S['sing'], *Mm['tags'], *tag_w],
                            why=f"HAVING on the aggregate with '{opw}' => {op} {nn}. Same skeleton, different operator/threshold changes the result.", form='having', sub=sub, mea=mea, w=w[0])
                # 3. top 3 exact (no date variants except all/apr to bound size)
                if w[0] in ('all', 'apr'):
                    for word, d in (('highest', 'DESC'), ('lowest', 'ASC')):
                        add(q=f"Return the top 3 {S['plur']} with the {word} {ph} (exactly 3 rows, break ties by {S['tie']}).{sfx}",
                            sql=f"SELECT {keys}, {M} AS m\n{base}\nGROUP BY {keys}\nORDER BY m {d}, {S['keys'][0]}\nLIMIT 3;",
                            alt=f"SELECT {kn}, m FROM (SELECT {kn}, m, ROW_NUMBER() OVER (ORDER BY m {d}, k1) AS rn FROM (\n{inner}) t) x\nWHERE rn <= 3 ORDER BY rn;",
                            cmp='ordered', pattern='topn_rank', diff=4, tags=['top n', 'limit', 'exactly n', word, S['sing'], *Mm['tags'], *tag_w],
                            why=f"Exactly 3 rows ({word}); ties at the cut-off are broken by key.", form='top3', sub=sub, mea=mea, w=w[0])
                # 4. highest / lowest with ties
                for word, fn, d in (('highest', 'MAX', 'DESC'), ('lowest', 'MIN', 'ASC')):
                    add(q=f"Find the {S['sing']} with the {word} {ph} (include ties).{sfx}",
                        sql=f"SELECT {keys}, {M} AS m\n{base}\nGROUP BY {keys}\nHAVING {M} = (SELECT {fn}(u.m) FROM (\n{inner}) AS u);",
                        alt=f"SELECT {kn}, m FROM (SELECT {kn}, m, RANK() OVER (ORDER BY m {d}) AS rk FROM (\n{inner}) t) x\nWHERE rk = 1;",
                        cmp='set', pattern='topn_rank', diff=5, tags=['ties', word, fn.lower(), S['sing'], *Mm['tags'], *tag_w],
                        why=f"{word.capitalize()} value INCLUDING ties (compare with {fn} of the per-group values), unlike LIMIT 1.", form='ties', sub=sub, mea=mea, w=w[0])
    # 5. existence / anti-join over date windows (orders only; independent of measures)
    for sub in ('customer', 'employee', 'shipper', 'product'):
        S = SUBJECTS[sub]
        for w in WINDOWS:
            cond = w[2]; sfx = f" {w[1]}" if w[1] else ""
            keys = ', '.join(S['keys']).replace('c.', 'x.').replace('e.', 'x.').replace('s.', 'x.').replace('p.', 'x.')
            outer = S['outer'].rsplit(' ', 1)[0] + ' x'
            corr = S['corr'].replace('c.ID', 'x.ID').replace('e.ID', 'x.ID').replace('s.ID', 'x.ID').replace('p.ID', 'x.ID')
            dateand = f" AND {cond}" if cond else ""
            if sub == 'product':
                inner_from = "`order details` od JOIN orders o ON o.`Order ID` = od.`Order ID`"
                lj = f"LEFT JOIN `order details` od ON od.`Product ID` = x.ID\nLEFT JOIN orders o ON o.`Order ID` = od.`Order ID`{dateand}"
                inlist = f"SELECT od.`Product ID` FROM {inner_from}" + (f" WHERE {cond}" if cond else "")
                anti_alt_group = True
            else:
                inner_from = "orders o"
                lj = f"LEFT JOIN orders o ON {corr}{dateand}"
                inlist = f"SELECT o.`{ 'Customer ID' if sub == 'customer' else 'Employee ID' if sub == 'employee' else 'Shipper ID'}` FROM orders o" + (f" WHERE {cond}" if cond else "")
                anti_alt_group = True
            kx = ', '.join(k.replace('c.', 'x.').replace('e.', 'x.').replace('s.', 'x.').replace('p.', 'x.') for k in S['keys'])
            add(q=f"Find the {S['plur']} that {S['verb']}{sfx}.".replace('  ', ' '),
                sql=f"SELECT {kx}\nFROM {outer}\nWHERE NOT EXISTS (SELECT 1 FROM {inner_from} WHERE {corr}{dateand});",
                alt=f"SELECT {kx}\nFROM {outer}\n{lj}\nGROUP BY {kx}\nHAVING COUNT(o.`Order ID`) = 0;",
                cmp='set', pattern='not_exists', diff=3, tags=['not exists', 'never', 'none', 'anti join', S['sing'], *(['date', 'range'] if cond else [])],
                why="Negative condition: anti-join (NOT EXISTS / LEFT JOIN ... COUNT = 0). Not the same as an inner join with <>.", form='never', sub=sub, mea='-', w=w[0])
            add(q=f"Find the {S['plur']} that {S['verb_pos']}{sfx}.".replace('  ', ' '),
                sql=f"SELECT {kx}\nFROM {outer}\nWHERE EXISTS (SELECT 1 FROM {inner_from} WHERE {corr}{dateand});",
                alt=f"SELECT {kx}\nFROM {outer}\nWHERE x.ID IN ({inlist});",
                cmp='set', pattern='exists', diff=2, tags=['exists', 'in', 'at least one', S['sing'], *(['date', 'range'] if cond else [])],
                why="Positive twin of the 'no orders' question (EXISTS vs IN).", form='exists', sub=sub, mea='-', w=w[0])
    return out
