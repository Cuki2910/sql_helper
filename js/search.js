/* Deterministic offline retrieval engine. No AI, no network. Works in browser (window.NWSearch) and Node (module.exports).
   Layers: A exact/normalized, B BM25, C fuzzy (edit distance + token similarity), D SQL pattern rules,
   E schema-aware matching, F constraint recognition (mismatch => warning + score penalty). */
(function (root) {
  'use strict';

  const DEFAULT_WEIGHTS = { bm25: 0.38, fuzzy: 0.20, phrase: 0.14, pattern: 0.10, schema: 0.08, constraint: 0.10,
                            critPenalty: 0.55, minorPenalty: 0.85, minScore: 0.22, minCoverage: 0.45, k1: 1.4, b: 0.75 };

  const STOP = new Set(('the a an of in to for from is are be been was were that which who whom whose with and or on at as it its this these those ' +
    'their his her you your need want should also must can may will do does did have has had there then them they both ' +
    'retrieve retrieves return returns list show display find get give write using use please northwind database sql statement ' +
    'consider following would could like some info information explain explanation versus vs difference differ differs between').split(' '));

  const NUMWORDS = { one: 1, two: 2, three: 3, four: 4, five: 5, six: 6, seven: 7, eight: 8, nine: 9, ten: 10 };
  const ORD = { first: 1, second: 2, third: 3, fourth: 4, fifth: 5, sixth: 6, seventh: 7, eighth: 8, ninth: 9, tenth: 10 };

  // multi-word canonicalisation (order matters)
  const PHRASES = [
    // domain synonyms: bank/schema vocabulary is canonical, applied to both stored questions and queries
    [/\bclient(s?)\b/g, ' customer$1 '],
    [/\bstaff( members?)?\b/g, ' employees '],
    [/\bvendor(s?)\b/g, ' supplier$1 '],
    [/\bprocurement\b/g, ' purchase order '],
    [/\bcarriers?\b/g, ' shipper '],
    [/\bpermissions?\b|\bauthori[sz]ations?\b|\baccess rights?\b/g, ' privilege '],
    [/\b(workflow |approval |allocation |processing )?(stages?|states?)\b/g, ' status '],
    [/\bsales ?(people|person|reps?|representatives?)\b|\bsalesm[ae]n\b/g, ' employees '],
    [/\btown(s?)\b/g, ' city '],
    [/\bpriciest\b/g, ' highest price '],
    [/\btypical\b/g, ' avg '],
    [/\b(tally|tallies|tallying)\b/g, ' count '],
    [/\bzero orders\b/g, ' no orders '],
    [/\b(rolling|running|cumulative)( sum| total| count| revenue)?\b/g, ' cumulative '],
    [/\b(successive|adjacent|neighbou?ring)\b/g, ' consecutive '],
    [/\barrived\b/g, ' received '],
    [/\bundispatched\b|\bnot (yet )?dispatched\b/g, ' not shipped '],
    [/\bdispatch(ed)?\b/g, ' shipped '],
    [/\b(catalogue|catalog) price\b/g, ' list price '],
    [/\bshipping charge\b/g, ' shipping fee '],
    [/\btheir respective categories\b/g, ' their own category '],
    [/\babsent from\b/g, ' not in '],
    [/\bwithout (?:imposing )?any price restriction\b/g, ' regardless of price '],
    [/\b(?:from )?(?:smallest to largest|lowest to highest)\b/g, ' ascending '],
    [/\b(?:from )?(?:largest to smallest|highest to lowest)\b/g, ' descending '],
    [/\b(least expensive|lowest[- ]priced)\b/g, ' lowest price '],
    [/(?<!line )\bitem(s?)\b/g, ' product$1 '],
    [/(?:over|above|greater|more|higher|larger) (?:than )?or equal(?: to)?|\bgte\b|(?<=\d)(?: [a-z]+)? (?:minimum|min)\b|greater than or equal to|larger or equal to|equal to or (greater|larger|more) than|no less than|not less than|>=|>\s*=|≥|or more\b|or higher\b|or above\b|or greater\b|or larger\b|or over\b|no fewer than|not fewer than|(?:a |at )?min(?:imum)? (?:of )?(?=\d)|(?<=\d)\+(?=\s|$)/g, ' at least '],
    [/(?:under|below|less|fewer|lower|smaller) (?:than )?or equal(?: to)?|\blte\b|\bat the most\b(?=\s*(?:\d|$|[,.;]|and\b|with\b|per\b|in\b))|\btops\b|(?<=\d)(?: [a-z]+)? (?:maximum|max)\b|less than or equal to|smaller or equal to|equal to or (less|smaller|fewer) than|no more than|not more than|<=|<\s*=|≤|or less\b|or fewer\b|or below\b|or lower\b|or smaller\b|up to\b|not exceed(?:s|ing)?\b|(?:a |at )?max(?:imum)? (?:of )?(?=\d)/g, ' at most '],
    [/higher than|greater than|larger than|bigger than|more than|exceeds?|exceeding|over\b|above\b|(?<![-<=])>(?!=)/g, ' more than '],
    [/lower than|smaller than|less than|fewer than|below\b|under\b|(?<![-])<(?!=)/g, ' fewer than '],
    [/(more|higher|greater|larger|bigger) than (all|every)\b/g, ' gtall '],
    [/(more|higher|greater|larger|bigger) than (any|some|at least 1)\b/g, ' gtany '],
    [/\b(includes?|including) (all|every)\b|\ball the\b|\bevery\b/g, ' every '],
    [/\b(handled|handles|handle|handling|processed|processes|processing|process)\b/g, ' process '],
    [/\b(?:bought|purchase[sd]?|ordered) together\b/g, ' ordered together '],
    [/\bbought\b/g, ' purchased '],
    [/\bexpensive\b/g, ' high price '],
    [/\b(recent|newest|last)\b/g, ' latest '],
    [/\b(keep|keeping|with|and) ties\b/g, ' include ties '],
    [/\b(fewest|(?<!at )least) (orders|products|customers|items|sales|lines)\b/g, ' lowest number $2 '],
    [/\b(?<!at )most (orders|products|customers|items|sales|lines)\b/g, ' highest number $1 '],
    [/\bseft\b/g, ' self '],
    [/\bself[- ]?join\b/g, ' self join '],
    [/\bsub[- ]?quer(y|ies)\b/g, ' subquery '],
    [/(\d+)\s*%/g, ' $1 percent '],
    [/(\d+)(st|nd|rd|th)\b/g, ' $1 '],
    [/\bhow many\b/g, ' count number '],
    [/\bnumber of\b/g, ' count number '],
    [/\baverage\b|\bavg\b|\bmean\b/g, ' avg '],
    [/\btotal\b|\bsum of\b|\bsum\b/g, ' sum '],
    [/\bsorted?\b|\bsorting\b/g, ' sort '],
    [/\bmost expensive\b/g, ' highest price '],
    [/\bcheapest\b/g, ' lowest price '],
    [/\bgrouped by\b/g, ' group by '],
    [/\bfewest\b|\bsmallest\b|\bminimum\b/g, ' lowest '],
    [/\blargest\b|\bgreatest\b|\bbiggest\b|\bmaximum\b/g, ' highest '],
  ];

  // uncertain synonym guesses: shown as a minor warning (no score effect) when the query used them
  const SYN_NOTES = [
    [/\bclients?\b/i, "'client' read as Customers table."],
    [/\bstaff\b/i, "'staff' read as Employees (could be Privileges/users in another schema)."],
    [/\bvendors?\b/i, "'vendor' read as Suppliers table."],
    [/\bcarriers?\b/i, "'carrier' read as Shippers table."],
    [/\bsales ?(people|person|reps?)\b|\bsalesm[ae]n\b/i, "'salesperson' read as Employees."],
    [/\bprocurement\b/i, "'procurement' read as Purchase Orders."],
    [/\b(un)?dispatch(ed)?\b|\bnot (yet )?dispatched\b/i, "'dispatched' read as shipped (Shipped Date / order status); check the exact condition."],
    [/\b(catalogue|catalog) price\b/i, "'catalogue price' read as Products.List Price (not Standard Cost)."],
    [/\b(least expensive|lowest[- ]priced)\b/i, "'least expensive' read as lowest List Price (could mean Standard Cost)."],
    [/(?<!line )\bitems?\b/i, "'item' read as Product (not an order-detail line); check which is meant."],
  ];

  function norm(s) {
    s = String(s == null ? '' : s).toLowerCase().replace(/[’‘]/g, "'").replace(/\b(have|has|had|do|does|did|is|are|was|were)n't\b/g, '$1 not').replace(/\bcan't\b/g, 'cannot').replace(/\bwon't\b/g, 'will not').replace(/[“”„]/g, '"').replace(/[‘’`]/g, ' ').replace(/_/g, ' ');
    // column names 'First Name' / 'Last Name' must not become ordinal '1' / 'latest'
    s = s.replace(/\bfirst name\b/g, ' firstname ').replace(/\blast name\b/g, ' lastname ');
    s = s.replace(/\bone-(half|quarter|fifth|tenth)\b/g, (_, part) => ({ half: 50, quarter: 25, fifth: 20, tenth: 10 })[part] + ' percent');
    s = s.replace(/\b(one|two|three|four|five|six|seven|eight|nine|ten)\b/g, (m) => NUMWORDS[m]);
    s = s.replace(/\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\b/g, (m) => ORD[m]);
    for (const [re, rep] of PHRASES) s = s.replace(re, rep).replace(/\s+/g, ' ');
    return s.replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  }

  // Characters norm() throws away but that change meaning: unary minus, comparison operators, LIKE wildcards.
  const sigOf = (s) => String(s == null ? '' : s).replace(/[’‘`]/g, "'").match(/(?<![\w)])-\s*\$?\d|!=|<>|>=|<=|[<>=%]|(?<=\w)_(?=\w)|\bnot\s+like\b|'[^']*'/gi) || [];
  const sameSig = (a, b) => { const x = sigOf(a).map((m) => m.toLowerCase()).sort().join('\u0001'), y = sigOf(b).map((m) => m.toLowerCase()).sort().join('\u0001'); return x === y; };

  function stem(w) {
    if (w.length > 4 && w.endsWith('ies')) return w.slice(0, -3) + 'y';
    if (w.length > 4 && w.endsWith('sses')) return w.slice(0, -2);
    if (w.length > 3 && w.endsWith('s') && !w.endsWith('ss') && !w.endsWith('us')) w = w.slice(0, -1);
    if (w.length > 5 && w.endsWith('ing')) return w.slice(0, -3);
    if (w.length > 4 && w.endsWith('ed')) return w.slice(0, -2);
    return w;
  }
  const terms = (s) => norm(String(s == null ? '' : s).replace(/([a-z0-9])([A-Z])/g, '$1 $2')).split(' ').filter((w) => w && !STOP.has(w)).map(stem);

  function lev(a, b, max) {
    if (a === b) return 0;
    const la = a.length, lb = b.length;
    if (Math.abs(la - lb) > max) return max + 1;
    let prev = new Array(lb + 1), cur = new Array(lb + 1);
    for (let j = 0; j <= lb; j++) prev[j] = j;
    for (let i = 1; i <= la; i++) {
      cur[0] = i; let rowMin = i;
      for (let j = 1; j <= lb; j++) {
        const c = a.charCodeAt(i - 1) === b.charCodeAt(j - 1) ? 0 : 1;
        cur[j] = Math.min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + c);
        if (cur[j] < rowMin) rowMin = cur[j];
      }
      if (rowMin > max) return max + 1;
      [prev, cur] = [cur, prev];
    }
    return prev[lb];
  }

  // ---------- Layer D: SQL pattern rules ----------
  const PATTERN_RULES = [
    ['select_filter', /\bwhere\b|\bfilter/],
    ['order_limit', /order by|\blimit\b|\bsort\b|\bascending\b|\bdescending\b|\basc\b|\bdesc\b/],
    ['distinct', /\bdistinct\b|\bunique\b|\bduplicates?\b/],
    ['aggregate', /\b(count|sum|avg|min|max|lowest|highest)\b|\bcount\b/],
    ['group_having', /group by|\bhaving\b|\bper\b|\beach\b|for every|\bby each\b/],
    ['inner_join', /\bjoin\b/],
    ['left_join', /left (outer )?join|including those without|even if|with no orders|zero orders/],
    ['subquery', /\(\s*select|subquery|nested|derived table/],
    ['exists', /\bexists\b|at least 1 |at least one/],
    ['not_exists', /not exists|\bnever\b|\bwithout\b|\bno orders\b|\bnone\b|have not|has not|did not|does not have/],
    ['in_notin', /\bin \(|\bnot in\b/],
    ['correlated', /correlated|own category|own group|same (category|city|country)/],
    ['self_join', /self join|\bpairs?\b|together|same (city|category|country)/],
    ['cond_agg', /case when|conditional|pivot|separate columns?|two columns|shipped and not shipped/],
    ['date', /\b(year|month|date|quarter|week|day|monthly)\b|\b20\d\d\b|date format/],
    ['topn_rank', /\btop\b|\bnth\b|\boffset\b|\bhighest\b|\blowest\b|\brank\b|dense rank|row number|\b\d+ (highest|lowest)\b|\bmost (frequently|orders)\b/],
    ['optimization', /efficien|optimi[sz]|\bindex|inefficient|performance|\bfaster\b|which query is better|explain (plan|select)/],
    ['null_handling', /\bnull\b|\bmissing\b|not yet|is null|coalesce/],
    ['division', /\b(every|for all|all of the)\b|relational division/],
    ['computed', /\bratio\b|\bpercent\b|\bmargin\b|\bround\b|computed/],
    ['all_any', /\ball \(|\bany \(|more than all|more than any/],
    ['set_ops', /\bunion\b|combine/],
  ];
  function detectPatterns(text, tableCount) {
    const t = ' ' + norm(text) + ' ';
    const raw = String(text).toLowerCase();
    const out = new Set();
    for (const [id, re] of PATTERN_RULES) if (re.test(t) || re.test(raw)) out.add(id);
    if ((tableCount || 0) >= 3 && out.has('aggregate')) out.add('multi_agg');
    return out;
  }

  // ---------- Layer F: constraint recognition ----------
  function constraints(text) {
    // ', not a three-day average' is a clarification of the metric, not a negated condition
    // technique instructions ('without using INTERSECT', 'not with LIMIT') and ', not a ...' clarifications do not negate the data condition
    const scoped = String(text).replace(/\(\s*not\s+(?:\w+\.)?[`"]?ship city[`"]?\s*\)/gi, ' ').replace(/,\s*not\s+(?:distinct\s+)?(?:customers?|orders?|products?|cities|categories|(?:detail )?(?:lines?|rows?))(?=\s*[.;?]|$)/gi, ' ').replace(/,\s*not an?\s[^.;?]*/gi, ' ').replace(/\b(without|not|no)\s+(using|use|with|via)\s+\w+(\s+(or|and)\s+\w+)?/gi, ' ');
    const t = ' ' + norm(scoped) + ' ';
    const c = {};
    const cmp = new Set();
    if (/\bat least (?!1\b|one\b)/.test(t)) cmp.add('>=');
    if (/\bat most\b/.test(t)) cmp.add('<=');
    if (/\bmore than\b/.test(t)) cmp.add('>');
    if (/\bfewer than\b/.test(t)) cmp.add('<');
    if (/\bexactly\b|\bonly 1\b|\bequal to\b/.test(t)) cmp.add('=');
    c.cmp = cmp;
    const ex = new Set();
    const tt = t.replace(/\bat (least|most)\b/g, ' ');
    if (/\b(lowest|bottom|least|smallest|worst)\b/.test(tt)) ex.add('min');
    if (/\b(highest|most|largest|best|greatest)\b/.test(tt) || (/\btop\b/.test(tt) && !ex.size)) ex.add('max');
    c.status = new Set(t.match(/\b(sold|purchased|waste|on hold)\b/g) || []);
    c.extreme = ex;
    c.gtAll = /\bgtall\b/.test(t); c.gtAny = /\bgtany\b/.test(t);
    const negated = norm(scoped.replace(/\b(?:must|should) not (?:increase|inflate|multiply)\b[^.;?]*/gi, ' ').replace(/\b(exclude|excluding|ignore|ignoring)\b[^.;?]*\bNULL\b/gi,
      (clause) => /\b(never|not|without|except|none|neither|nor|who|orders?|transactions?)\b/i.test(clause) ? clause : ' ')).replace(/\bnot only\b/g, '');
    c.neg = /\b(never|not|without|except|exclude|excluding|none|neither|nor)\b|\bno (?!more|less)/.test(negated);
    c.tiesIncl = /\b(include|including|with) ties\b|\bties included\b|\btied\b/.test(t);
    c.tiesExcl = /\bexactly \d+ (rows|results|records|products|orders|customers)\b|\bbreak(?:ing)? (?:\w+ )?ties\b|\bwithout ties\b|\bno ties\b/.test(t);
    c.distinct = /\bdistinct\b|\bunique\b|\bdifferent\b/.test(t);
    c.nullIncl = /\b(include|including) null|\bwith null|\bnull values? included/.test(t);
    c.nullExcl = /\b(exclude|excluding|ignore|ignoring|without) null|\bnot null\b|\bnon null\b/.test(t);
    c.nullMention = /\bnull\b|\bmissing\b|\bnot yet shipped\b|\bnot shipped\b/.test(t);
    c.asc = /\b(ascending|asc|alphabetical|alphabetically)\b/.test(t);
    c.desc = /\b(descending|desc)\b/.test(t);
    const quantified = t.replace(/\bfor every (?:product categor\w*|customers?|employees?|shippers?|suppliers?|products?|orders?)\b/g, ' ').replace(/\b(include|return|list|show|report|display|find|identify|retrieve|get) every\b/g, '$1');
    c.every = /\b(every|for all|all of the)\s+(?!(?:\w+\s+){0,2}tied\b)(?:\w+\s+){0,3}(?:product categor\w*|products?|customers?|employees?|suppliers?|shippers?|orders?|categor\w*|countries|regions?|cities|privileges?)\b/.test(quantified);
    c.any = /\b(any|some|at least 1|at least one)\b/.test(t) && !c.every;
    c.perMonth = /\b(per month|each month|monthly|by month|for each month|every month)\b/.test(t);
    c.combined = /\b(combined|overall|in total|across all|all months)\b/.test(t);
    const agg = new Set();
    if (/\bavg\b/.test(t)) agg.add('avg');
    if (/\bsum\b/.test(t)) agg.add('sum');
    if (/\bcount\b/.test(t) && !(/\bcount number (days?|hours?|minutes?|seconds?|weeks?|months?|years?|rows?|decimals?|characters?|digits?)\b/.test(t) && !/\bcount (?!number)/.test(t))) agg.add('count');
    c.agg = agg;
    // ponytail: lexical intent, not SQL parsing; unqualified functions and negated DDL remain ambiguous. Upgrade to statement-aware classification when needed.
    const writeText = t.replace(/\b(?:built in|window|aggregate) functions?\b/g, ' ');
    const schemaWrite = /\badd(?:s|ed|ing)?\b[^.;?!]*\b(constraints?|checks?|index(?:es)?|indices|keys?)\b|\badd(?:s|ed|ing)?\b(?![^.;?!]*\b(?:computed|calculated|output|results?|reports?|ratios?|percent(?:age)?)\b)[^.;?!]*\bcolumns?\b|\badd(?:s|ed|ing)?\b[^.;?!]*\b(rows?|records?)\b[^.;?!]*\b(?:to|into)\b|\bremov(?:es|ed|ing)\b[^.;?!]*\b(rows?|records?|fields?|columns?|constraints?|checks?|index(?:es)?|indices|keys?)\b/i.test(scoped);
    c.write = schemaWrite || /\b(delet(?:e[sd]?|ing)|remove|insert(?:s|ed|ing)?|updat(?:e[sd]?|ing)|upsert(?:s|ed|ing)?|replac(?:e[sd]?|ing)|truncat(?:e[sd]?|ing)|alter(?:s|ed|ing)?|drop(?:s|ped|ping)?|rais(?:e[sd]?|ing)|commit(?:s|ted|ting)?|roll(?:back| back|ed back|ing back))\b|\bstart (a )?transaction\b|\bcreate\b.*\b(tables?|view|index|function|procedure|trigger)\b|\badd(?:s|ed|ing)? (a |an |the )?new (rows?|shippers?)\b|\b(triggers?|functions?|procedures?|cursors?|savepoints?)\b|\btransfer(?:s|red|ring)?\b.*\btransactions?\b|\bon duplicate key\b/.test(writeText);
    c.perCat = /\b(?:in|within|per|for) (?:each|every) (?:product )?categor|\bper (?:product )?categor|\bwithin (?:its|their|the same) (?:product )?categor/.test(t);
    c.allocEq = /\b(equal|equally|evenly)\b/.test(t);
    c.allocProp = /\bproportion\w*|\bpro rata\b|\bprorata\b|\bvalue share\b|\bshare of\b/.test(t);
    c.nums = new Set((t.match(/\b\d+\b/g) || []).filter((n) => !/^(19|20)\d\d$/.test(n)));
    c.years = new Set(t.match(/\b(19|20)\d\d\b/g) || []);
    const NOUN = '(product categor\\w*|customers?|employees?|shippers?|suppliers?|products?|orders?|cit(?:y|ies)|states?|categor\\w*)';
    const hm = t.match(new RegExp('\\b(?:find|list|show|return|retrieve|get|which|what|display|compute|calculate)\\s+(?:the |all |each |every |me )?(?:(?:top|\\d+|distinct|different|unique)\\s+)*' + NOUN + '\\b')) || t.match(new RegExp('\\b' + NOUN + '\\b'));
    c.head = hm ? hm[1].replace(/ies$/, 'y').replace(/s$/, '').replace(/^categor.*/, 'product category').replace(/^product categor.*/, 'product category') : '';
    const dm = t.match(/\b(?:different|distinct|unique)\s+(?:product\s+)?(categor\w*|products?|orders?|customers?|employees?|countr\w*|cit(?:y|ies)|shippers?|suppliers?|states?)/)
      || t.match(/\bcount (orders?|customers?|products?)\b/);
    c.distinctOf = dm ? dm[1].replace(/ies$/, 'y').replace(/s$/, '').replace(/^categor.*/, 'category').replace(/^countr.*/, 'country') : '';
    const mon = new Set(t.match(/\b(january|february|march|april|may|june|july|august|september|october|november|december)\b/g) || []);
    if (/\b(?:first|1) quarter\b|\bq1\b/.test(t)) mon.add('q1'); if (/\b(?:second|2) quarter\b|\bq2\b/.test(t)) mon.add('q2');
    c.months = mon;
    c.having = /\bhaving\b/.test(t); c.where = /\bwhere\b/.test(t);
    return c;
  }
  const setEq = (a, b) => a.size === b.size && [...a].every((x) => b.has(x));
  const fmt = (s) => [...s].join(', ');

  function compareConstraints(q, e, entry) {
    const w = []; // {sev, msg}
    const crit = (msg) => w.push({ sev: 'critical', msg });
    const minor = (msg) => w.push({ sev: 'minor', msg });
    if (q.cmp.size && e.cmp.size && !setEq(q.cmp, e.cmp))
      crit(`Comparison differs: your question uses [${fmt(q.cmp)}], the stored question uses [${fmt(e.cmp)}]. The HAVING/WHERE operator must change (more than = >, at least = >=).`);
    if ([...q.cmp].some((x) => x !== '=') && !e.cmp.size && q.nums.size) minor(`Your question has a threshold condition [${fmt(q.cmp)} ${fmt(q.nums)}]; the stored query has none: add a HAVING/WHERE condition.`);
    if (!q.cmp.size && [...e.cmp].some((x) => x !== '=') && e.nums.size) minor('The stored query has a threshold condition that your question does not mention: remove it.');
    if (q.extreme.size && e.extreme.size && !setEq(q.extreme, e.extreme))
      crit(`Direction differs: your question asks for ${fmt(q.extreme)}imum-side rows, the stored one ${fmt(e.extreme)}. Flip ORDER BY direction / MAX vs MIN.`.replace('maximum-side', 'highest').replace('minimum-side', 'lowest'));
    if (q.write !== e.write) crit(q.write ? 'Your question CHANGES data or structure (INSERT/UPDATE/DELETE/DDL), the stored query is a plain SELECT: it only retrieves rows.' : 'The stored answer CHANGES data or structure (INSERT/UPDATE/DELETE/DDL); your question only asks to retrieve rows: do not reuse it as is.');
    if (q.neg !== e.neg)
      crit(q.neg ? 'Your question is NEGATED (never/not/without/except), the stored question is not: use NOT EXISTS / anti-join, not the stored positive query.'
                 : 'The stored question is NEGATED (never/not/without), yours is not: do not reuse the anti-join as is.');
    if ((q.tiesIncl && (e.tiesExcl || (!e.tiesIncl && /\blimit\b|\brow_number\b/i.test(entry.answer || '')))) || (q.tiesExcl && e.tiesIncl))
      crit('Tie handling differs (exactly N rows vs including ties). LIMIT drops ties; use a MAX/threshold subquery or DENSE_RANK to keep them.');
    if (q.perCat !== e.perCat && q.extreme.size && e.extreme.size) crit(q.perCat ? 'Your question asks for the extreme PER CATEGORY (max per group); the stored one is over the whole table: group or correlate by category.' : 'The stored query is the extreme PER CATEGORY; your question is over the whole table: drop the grouping.');
    if (entry.kind === 'sql' && q.distinct && !/\bdistinct\b|\bgroup by\b/i.test(entry.answer || '')) minor('Your question asks for distinct/unique values; the stored SQL has no DISTINCT or GROUP BY: it may count duplicates.');
    if ((q.nullIncl && e.nullExcl) || (q.nullExcl && e.nullIncl)) crit('NULL handling differs (include vs exclude NULL values).');
    else if (q.nullMention !== e.nullMention) minor('One of the questions talks about NULL / missing values and the other does not: check NULL handling.');
    if ((q.asc && e.desc && !e.asc) || (q.desc && e.asc && !q.asc && !e.desc)) crit('Sort direction differs (ASC vs DESC).');
    if (q.status.size && e.status.size && !setEq(q.status, e.status)) crit(`Inventory transaction type differs: yours [${fmt(q.status)}], stored [${fmt(e.status)}] (filter on \`inventory transaction types\`.\`Type Name\`).`);
    if (q.gtAll !== e.gtAll || q.gtAny !== e.gtAny) crit('ALL vs ANY comparison differs (> ALL = above the maximum, > ANY = above the minimum).');
    if (q.every !== e.every && (q.every || e.every)) crit('Quantifier differs: "every/all" (relational division) vs a plain existence condition.');
    if ((q.perMonth && e.combined) || (q.combined && e.perMonth)) crit('Time grain differs: per month vs all months combined.');
    if ((q.allocEq && e.allocProp && !e.allocEq) || (q.allocProp && e.allocEq && !q.allocEq)) crit('Allocation rule differs: equal split vs proportional-to-value split.');
    // 'sum' next to 'avg' is usually the noun "total" (e.g. "average of line totals"), not a second aggregate
    const qa = new Set(q.agg), ea = new Set(e.agg);
    if (qa.has('avg') || ea.has('avg')) { qa.delete('sum'); ea.delete('sum'); }
    if (qa.size && ea.size && !setEq(qa, ea)) crit(`Aggregate differs: yours [${fmt(qa)}], stored [${fmt(ea)}].`);
    if (q.nums.size && e.nums.size && !setEq(q.nums, e.nums)) minor(`Number differs: yours [${fmt(q.nums)}], stored [${fmt(e.nums)}]: adjust LIMIT/OFFSET/threshold constants.`);
    if (q.years.size && e.years.size && !setEq(q.years, e.years)) minor(`Year/date range differs: yours [${fmt(q.years)}], stored [${fmt(e.years)}].`);
    if (q.years.size && !e.years.size) crit(`Your question limits the data to year(s) [${fmt(q.years)}]; the stored question has no year filter: add the date range.`);
    if (!q.years.size && e.years.size) crit(`The stored question is limited to year(s) [${fmt(e.years)}]; your question has no year filter: do not reuse that date restriction.`);
    if (!setEq(q.months, e.months)) crit(q.months.size && !e.months.size ? `Your question limits the data to [${fmt(q.months)}], the stored query has NO date filter: add a date range condition.`
      : !q.months.size ? `The stored query is limited to [${fmt(e.months)}]; your question has no such date window: remove its date filter.` : `Time window differs: yours [${fmt(q.months)}], stored [${fmt(e.months)}].`);
    if (q.distinctOf && e.distinctOf && q.distinctOf !== e.distinctOf) crit(`Counted/distinct item differs: yours counts different "${q.distinctOf}", the stored one counts different "${e.distinctOf}".`);
    if (q.head && e.head && q.head !== e.head && ![q.head, e.head].every((h) => /^product( category)?$/.test(h))) crit(`The result subject differs: yours is about "${q.head}", the stored one about "${e.head}".`);
    if (q.having !== e.having && (q.having || e.having)) minor('HAVING (group condition) vs WHERE (row condition) mentioned in only one question.');
    return w;
  }

  // ---------- Layer E: schema detection ----------
  function buildSchemaIndex(schema) {
    const tables = [], cols = [];
    if (!schema) return { tables, cols };
    const sing = (n) => n.replace(/ies$/, 'y').replace(/s$/, '');
    for (const t of schema.tables) {
      const base = norm(t.name);
      const names = new Set([base, norm(sing(t.name)), base.replace(/ /g, '')]);
      tables.push({ id: t.name, names: [...names].filter(Boolean) });
      for (const c of t.columns) {
        const n = norm(c.name);
        if (n.length < 4 || ['notes', 'address', 'company', 'attachments', 'quantity', 'default', 'display', 'title', 'description'].includes(n)) continue;
        cols.push({ id: t.name + '.' + c.name, table: t.name, re: n });
      }
    }
    return { tables, cols };
  }
  function detectSchema(text, idx) {
    const t = ' ' + norm(text).replace(/\b(ascending|descending|alphabetical|sorting|sort|in) order\b/g, ' $1 ') + ' ';
    const tabs = new Set(), cols = new Set();
    for (const tb of idx.tables) for (const n of tb.names) if (t.includes(' ' + n + ' ') || t.includes(' ' + n + 's ') || (n.endsWith('y') && t.includes(' ' + n.slice(0, -1) + 'ies '))) { tabs.add(tb.id); break; }
    for (const c of idx.cols) if (t.includes(' ' + c.re + ' ')) cols.add(c.id);
    // domain words implying tables
    if (/\bcategor/.test(t)) tabs.add('products');
    if (/\b(shipping fee|ship country|shipped|shipping)\b/.test(t)) tabs.add('orders');
    if (/\bdiscount\b/.test(t)) tabs.add('order details');
    if (/\b(sold|purchased|waste|inventory)\b/.test(t)) tabs.add('inventory transactions');
    return { tabs, cols };
  }

  // ---------- Engine ----------
  function createEngine(opts) {
    opts = opts || {};
    const W = Object.assign({}, DEFAULT_WEIGHTS, opts.weights || {});
    const schemaIdx = buildSchemaIndex(opts.schema);
    const docs = new Map();        // id -> doc
    const postings = new Map();    // term -> Set(id)
    const df = new Map();          // term -> n docs
    const surface = new Map();     // stemmed -> a readable surface form
    let totalLen = 0;

    function indexText(entry) {
      const tf = new Map();
      const add = (arr, wgt) => { for (const t of arr) tf.set(t, (tf.get(t) || 0) + wgt); };
      add(terms(entry.question), 2);
      add([...new Set((entry.aliases || []).flatMap((alias) => terms(alias)))], 0.8);
      add(terms((entry.tags || []).join(' ')), 1.2);
      add(terms(entry.pattern || ''), 0.8);
      if (entry.kind === 'theory') { add(terms(entry.answer || ''), 0.35); }
      else { add(terms((entry.tables || []).join(' ')), 0.5); add(terms((entry.columns || []).join(' ')), 0.5); }
      return tf;
    }
    function makeDoc(entry) {
      const qn = norm(entry.question);
      const qt = terms(entry.question);
      const sch = detectSchema(entry.question, schemaIdx);
      const used = new Set(entry.tables || []);
      const doc = { entry, tf: indexText(entry), len: 0, qn, qt, qset: new Set(qt),
        bigrams: [bigrams(qt), ...(entry.aliases || []).map((alias) => bigrams(terms(alias)))], cons: constraints(entry.question), sch, tablesAll: new Set([...used, ...sch.tabs]),
        patterns: new Set([...detectPatterns(entry.question, used.size), entry.pattern].filter(Boolean)) };
      if (entry.kind !== 'theory') for (const p of detectPatterns(entry.answer || '', used.size)) if (['inner_join','left_join','group_having','not_exists','exists','distinct','subquery','set_ops','cond_agg','self_join','order_limit'].includes(p)) doc.patterns.add(p);
      for (const v of doc.tf.values()) doc.len += v;
      return doc;
    }
    function bigrams(arr) { const s = new Set(); for (let i = 0; i < arr.length - 1; i++) s.add(arr[i] + ' ' + arr[i + 1]); return s; }

    function add(entry) {
      if (docs.has(entry.id)) remove(entry.id);
      const d = makeDoc(entry);
      docs.set(entry.id, d); totalLen += d.len;
      for (const t of d.tf.keys()) { df.set(t, (df.get(t) || 0) + 1); if (!postings.has(t)) postings.set(t, new Set()); postings.get(t).add(entry.id); }
      for (const raw of norm(entry.question).split(' ')) if (raw && !STOP.has(raw) && !surface.has(stem(raw))) surface.set(stem(raw), raw);
    }
    function remove(id) {
      const d = docs.get(id); if (!d) return;
      totalLen -= d.len; docs.delete(id);
      for (const t of d.tf.keys()) { const n = df.get(t) - 1; if (n <= 0) { df.delete(t); postings.delete(t); } else { df.set(t, n); postings.get(t).delete(id); } }
    }
    (opts.entries || []).forEach(add);

    const N = () => docs.size || 1;
    const idf = (t) => Math.log(1 + (N() - (df.get(t) || 0) + 0.5) / ((df.get(t) || 0) + 0.5));
    const maxIdf = () => Math.log(1 + (N() + 0.5) / 1.5);

    // Layer C: map out-of-vocabulary tokens to nearest vocabulary term
    function correct(tokens) {
      const fixes = [], out = [];
      let vocab = null;
      for (const t of tokens) {
        if (df.has(t) || t.length < 6 || /^\d+$/.test(t)) { out.push(t); continue; }
        vocab = vocab || [...df.keys()];
        const lim = t.length <= 8 ? 1 : 2;
        let best = null, bd = lim + 1;
        for (const v of vocab) {
          if (v.length < 4) continue;
          const d = lev(t, v, lim);
          if (d < bd || (d === bd && best && df.get(v) > df.get(best))) { bd = d; best = v; }
        }
        if (best && bd <= lim && /^(un|non)/.test(t) && !/^(un|non)/.test(best)) best = null; // 'undelivered' is not a typo of 'delivered'
        if (best && bd <= lim) { out.push(best); fixes.push([surface.get(t) || t, surface.get(best) || best]); } else out.push(t);
      }
      return { tokens: out, fixes };
    }

    function tokSim(a, b) {
      if (a === b) return 1;
      if (a.length < 4 || b.length < 4) return 0;
      const m = Math.max(a.length, b.length), d = lev(a, b, 2);
      return d <= 2 ? 1 - d / m : 0;
    }

    function search(query, o) {
      o = o || {};
      const t0 = (typeof performance !== 'undefined' ? performance : Date).now();
      const kind = o.kind || 'all', limit = o.limit || 5;
      const qn = norm(query);
      // ponytail: lexical score uses only the requirement sentences; output-format sentences (Return/Sort/Round/Include...) add words no stored question shares, so they sank the coverage of exact-topic matches. Constraints/schema/patterns still read the full text. Upgrade: weight output sentences instead of dropping them.
      const sents = query.split(/(?<=[.!?])\s+(?=[A-Z])/), OUT = /^\s*(return|display|sort|order|arrange|round|include|exclude|show|list only|present|keep|retain|repeated)\b/i;
      const coreQ = sents.length > 1 ? sents.filter((x, i) => i === 0 || !OUT.test(x)).join(' ') : query;
      const rawTokens = terms(coreQ);
      const { tokens: qt, fixes } = correct(rawTokens);
      const qset = [...new Set(qt)];
      const qBig = bigrams(qt);
      const fixMap = new Map(fixes.map((f) => [f[0], f[1]]));
      const fixedText = fixes.length ? qn.split(' ').map((w) => fixMap.get(stem(w)) || w).join(' ') : query;
      const qCons = constraints(fixedText);
      const taskCue = /^\s*(find|identify|show|list|return|retrieve|get|compute|count|display|give|calculate|produce|build|write)\b/i.test(query) || /\b(report|pivot|directory)\b/i.test(query);
      const theoryCue = /\b(difference|differ|differs|vs|versus|why|what is|what are|which is better|which one|explain)\b/i.test(query);
      const qSch = detectSchema(fixedText, schemaIdx);
      const qPat = detectPatterns(fixedText, qSch.tabs.size);
      const avgdl = totalLen / N();
      const idfAll = qset.map((t) => (df.has(t) ? idf(t) : maxIdf()));
      const idfSum = idfAll.reduce((a, b) => a + b, 0) || 1;
      const idfIn = qset.reduce((a, t) => a + (df.has(t) ? idf(t) : 0), 0);
      const selfMax = qset.reduce((a, t) => a + (df.has(t) ? idf(t) * (W.k1 + 1) : 0), 0) || 1;

      const cand = new Set();
      for (const t of qset) { const p = postings.get(t); if (p) for (const id of p) cand.add(id); }
      if (!cand.size && qn) for (const [id, d] of docs) cand.add(id); // fuzzy-only fallback

      const res = [];
      for (const id of cand) {
        const d = docs.get(id), e = d.entry;
        if (kind !== 'all' && e.kind !== kind) continue;
        // B: BM25
        let bm = 0;
        for (const t of qset) { const f = d.tf.get(t); if (!f) continue; bm += idf(t) * (f * (W.k1 + 1)) / (f + W.k1 * (1 - W.b + W.b * d.len / avgdl)); }
        const bm25 = Math.min(1, bm / selfMax) * (idfIn / idfSum);
        // C: fuzzy token similarity (order-insensitive) weighted by idf + coverage
        let fz = 0, cov = 0; const matched = [];
        qset.forEach((t, i) => {
          let best = 0;
          if (d.qset.has(t) || d.tf.has(t)) best = 1; else for (const x of d.qset) { const s = tokSim(t, x); if (s > best) best = s; if (best === 1) break; }
          fz += best * idfAll[i]; if (best >= 0.7) { cov += idfAll[i]; matched.push(surface.get(t) || t); }
        });
        const fuzzy = fz / idfSum; const coverage = cov / idfSum;
        const dTerms = d.qset.size || 1; // reverse coverage keeps long entries from matching short queries trivially
        const revCov = Math.min(1, [...d.qset].filter((x) => qset.includes(x)).length / dTerms);
        // A: exact / phrase
        const exact = qn === d.qn && sameSig(query, e.question);
        let ph = 0;
        if (qBig.size) for (const [phraseIndex, phrase] of d.bigrams.entries()) {
          let inter = 0; for (const bigram of qBig) if (phrase.has(bigram)) inter++;
          ph = Math.max(ph, (2 * inter) / (qBig.size + phrase.size) * (phraseIndex ? 0.8 : 1));
        }
        // D patterns
        let pat = 0; if (qPat.size) { let k = 0; for (const p of qPat) if (d.patterns.has(p)) k++; pat = k / qPat.size; }
        // E schema
        let sch = 0.5; const missingTabs = [...qSch.tabs].filter((x) => !d.tablesAll.has(x) && !(x === 'orders' && d.tablesAll.has('order details') && !qSch.cols.size)); // ponytail: bare word 'orders' is often just the order-line rows; real orders-header use is caught via columns
        if (qSch.tabs.size || qSch.cols.size) {
          const shT = [...qSch.tabs].filter((x) => d.tablesAll.has(x)).length;
          const shC = [...qSch.cols].filter((x) => (e.columns || []).includes(x) || d.sch.cols.has(x)).length;
          sch = (shT + shC) / (qSch.tabs.size + qSch.cols.size);
        }
        // F constraints
        const warnings = e.kind === 'sql' ? compareConstraints(qCons, d.cons, e) : [];
        if (e.kind === 'sql' && missingTabs.length && qSch.tabs.size) warnings.push({ sev: 'critical', msg: `Your question mentions table(s) [${missingTabs.join(', ')}] that the stored solution does not use: target tables differ.` });
        const nCrit = warnings.filter((x) => x.sev === 'critical').length, nMin = warnings.filter((x) => x.sev === 'minor').length;
        const consScore = Math.max(0, 1 - 0.5 * nCrit - 0.2 * nMin);

        let score = W.bm25 * bm25 + W.fuzzy * fuzzy * (0.6 + 0.4 * revCov) + W.phrase * ph + W.pattern * pat + W.schema * sch + W.constraint * consScore;
        const wsum = W.bm25 + W.fuzzy + W.phrase + W.pattern + W.schema + W.constraint;
        score /= wsum;
        score *= Math.pow(W.critPenalty, nCrit) * Math.pow(W.minorPenalty, nMin);
        if (e.kind === 'sql' && qCons.write !== d.cons.write) score *= 0.75; // mutating vs retrieving is never a near-miss: rank below any retrieval answer
        if (exact) score = 1;
        if (theoryCue && e.kind === 'sql') score *= 0.9;
        if (taskCue && !theoryCue && e.kind === 'theory') score *= 0.65;
        if (e.source === 'original') score *= 1.02;
        if (/^COMBO-/.test(e.id)) score *= 0.96; // structural-rewrite verification is weaker than hand-written independent alternatives
        if (e.kind === 'sql' && e.verification && e.verification.status !== 'execution-verified') score *= 0.97;
        const notes = [];
        if (e.kind === 'sql' && qCons.extreme.size && /\blimit\b/i.test(e.answer || '') && !nCrit) notes.push('Reference uses LIMIT: tied rows at the cut-off are dropped. Check whether your question wants ties.');
        res.push({ id, entry: e, score, coverage, exact, warnings, notes, nCrit,
          parts: { bm25, fuzzy, phrase: ph, pattern: pat, schema: sch, constraint: consScore },
          why: { terms: [...new Set(matched)], patterns: [...qPat].filter((p) => d.patterns.has(p)), tables: [...qSch.tabs].filter((x) => d.tablesAll.has(x)), fixes } });
      }
      res.sort((a, b) => b.score - a.score || (a.id < b.id ? -1 : 1));
      const reliable = res.filter((r) => r.exact || (r.score >= W.minScore && r.coverage >= W.minCoverage));
      for (const r of reliable) r.label = r.exact ? 'identical after normalisation' : (r.score >= 0.7 && !r.nCrit ? 'very close wording' : (r.score >= 0.45 ? 'similar question' : 'related pattern only'));
      const ms = (typeof performance !== 'undefined' ? performance : Date).now() - t0;
      const synMsgs = SYN_NOTES.filter(([re]) => re.test(query)).map((x) => x[1]);
      if (synMsgs.length) for (const r of reliable.slice(0, limit)) for (const m of synMsgs) r.warnings.push({ sev: 'minor', msg: 'Wording assumption: ' + m });
      return { results: (o.filter ? reliable.filter(o.filter) : reliable).slice(0, limit), reliable: reliable.length > 0, ms, fixes, detected: { patterns: [...qPat], tables: [...qSch.tabs], constraints: qCons } };
    }

    return { add, remove, search, size: () => docs.size, weights: W, entry: (id) => docs.get(id) && docs.get(id).entry, entries: () => [...docs.values()].map((d) => d.entry) };
  }

  const api = { createEngine, DEFAULT_WEIGHTS, norm, terms, constraints, detectPatterns, lev };
  if (typeof module !== 'undefined' && module.exports) module.exports = api; else root.NWSearch = api;
})(typeof window !== 'undefined' ? window : globalThis);
