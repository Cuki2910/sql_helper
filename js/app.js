(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const el = (tag, attrs, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs || {})) { if (k === 'class') n.className = v; else if (k.startsWith('on')) n.addEventListener(k.slice(2), v); else if (v !== false && v != null) n.setAttribute(k, v); }
    for (const c of kids.flat()) if (c != null) n.append(c.nodeType ? c : document.createTextNode(c));
    return n;
  };
  const BUILTIN = window.NW_BANK.entries, PATTERNS = new Map(window.NW_BANK.patterns.map((p) => [p.id, p]));
  const SCHEMA = window.NW_SCHEMA;
  const TABLE_GUIDE = {
    customers: ['Một dòng là một khách hàng, không phải một đơn hàng.', 'ID, Company, First Name, Last Name, City, Country/Region', 'Nối với orders để tìm lịch sử mua; LEFT JOIN nếu cần cả khách chưa có đơn.'],
    orders: ['Một dòng là một đơn bán hàng của khách.', 'Order ID, Customer ID, Employee ID, Order Date, Shipped Date, Shipper ID, Shipping Fee, Status ID', 'Một đơn có nhiều dòng order details. Đếm đơn bằng COUNT(DISTINCT Order ID) sau khi nối chi tiết.'],
    'order details': ['Một dòng là một mục sản phẩm trong đơn bán hàng.', 'ID, Order ID, Product ID, Quantity, Unit Price, Discount', 'ID là khóa dòng chi tiết; Order ID có thể lặp. Quantity là số lượng, Unit Price là giá bán tại dòng hàng.'],
    products: ['Một dòng là một sản phẩm trong danh mục.', 'ID, Product Code, Product Name, Category, Standard Cost, List Price, Discontinued, Supplier IDs', 'List Price là giá danh mục, không thay cho Unit Price của đơn. Supplier IDs là text, không phải khóa ngoại đơn.'],
    suppliers: ['Một dòng là một nhà cung cấp.', 'ID, Company, First Name, Last Name, City', 'Nối qua purchase orders để xem các đơn nhập hàng, không nối trực tiếp với chuỗi products.Supplier IDs.'],
    'purchase orders': ['Một dòng là một đơn mua hàng từ nhà cung cấp.', 'Purchase Order ID, Supplier ID, Created By, Submitted Date, Status ID, Approved By', 'Created By, Approved By, Submitted By là các vai trò khác nhau cùng nối employees; dùng alias riêng. Bảng không khai báo PRIMARY KEY.'],
    'purchase order details': ['Một dòng là một mục sản phẩm trong đơn mua hàng.', 'ID, Purchase Order ID, Product ID, Quantity, Unit Cost, Date Received, Inventory ID', 'Unit Cost là chi phí mua; không nhầm với Unit Price của order details. Bảng không khai báo PRIMARY KEY.'],
    employees: ['Một dòng là một nhân viên.', 'ID, First Name, Last Name, Job Title', 'Nhân viên phụ trách đơn bán và các vai trò trong đơn mua dùng các cột liên kết khác nhau.'],
    shippers: ['Một dòng là một đơn vị vận chuyển.', 'ID, Company, Business Phone', 'Nối orders.Shipper ID với shippers.ID; không nhầm Shipper ID với mã đơn.'],
    invoices: ['Một dòng là một hóa đơn gắn với đơn bán hàng.', 'Invoice ID, Order ID, Invoice Date, Due Date, Tax, Shipping, Amount Due', 'Invoice ID là khóa chính; Order ID không có ràng buộc UNIQUE. Không mặc định mỗi đơn chỉ có một hóa đơn.'],
    'inventory transactions': ['Một dòng là một giao dịch làm biến động tồn kho.', 'Transaction ID, Transaction Type, Product ID, Quantity, Transaction Created Date', 'Không có cột Status; nối Transaction Type với inventory transaction types.ID để đọc loại giao dịch. Transaction ID không được khai báo PRIMARY KEY.'],
    'inventory transaction types': ['Một dòng giải nghĩa một loại giao dịch kho.', 'ID, Type Name', 'Loại giao dịch khác với trạng thái đơn; xem Type Name thay vì tự đoán ý nghĩa mã.'],
    'orders status': ['Một dòng giải nghĩa một trạng thái đơn bán hàng.', 'Status ID, Status Name', 'Nối từ orders.Status ID. Bảng không khai báo PRIMARY KEY; cần kiểm tra tính duy nhất nếu dữ liệu thay đổi.'],
    'orders tax status': ['Một dòng giải nghĩa một trạng thái thuế của đơn.', 'ID, Tax Status Name', 'Nối từ orders.Tax Status. Bảng không khai báo PRIMARY KEY; liên kết chưa được xác nhận trên giá trị khác NULL.'],
    'order details status': ['Một dòng giải nghĩa một trạng thái dòng chi tiết đơn bán.', 'Status ID, Status Name', 'Nối từ order details.Status ID, không phải orders.Status ID.'],
    'purchase order status': ['Một dòng giải nghĩa một trạng thái đơn mua hàng.', 'Status ID, Status', 'Nối từ purchase orders.Status ID. Cột tên trạng thái là Status; bảng không khai báo PRIMARY KEY.'],
    'employee privileges': ['Một dòng là một cặp nhân viên và quyền được cấp.', 'Employee ID, Privilege ID', 'Khóa chính ghép gồm cả hai cột. Đây là bảng nối quan hệ nhiều–nhiều giữa employees và privileges.'],
    privileges: ['Một dòng định nghĩa một quyền.', 'Privilege ID, Privilege Name', 'Muốn biết nhân viên nào có quyền, nối qua employee privileges.'],
    'sales reports': ['Một dòng là một cấu hình báo cáo bán hàng.', 'Group By, Display, Title, Filter Row Source, Default', 'Đây là cấu hình báo cáo, không phải dữ liệu giao dịch hay tổng doanh thu đã tính sẵn. Bảng không khai báo PRIMARY KEY.'],
    strings: ['Một dòng là một chuỗi văn bản tra cứu của ứng dụng mẫu.', 'String ID, String Data', 'Không phải bảng đơn hàng; không có liên kết nghiệp vụ được khai báo trong danh sách suy luận.']
  };
  const TODAY = new Date().toISOString().slice(0, 10);
  let userEntries = [], engine, lastQuery = '', lastOut = null;

  // ---------- helpers ----------
  function toast(msg) { const t = $('#toast'); t.textContent = msg; t.hidden = false; clearTimeout(toast.h); toast.h = setTimeout(() => (t.hidden = true), 2200); }
  async function copy(text) {
    try { await navigator.clipboard.writeText(text); } catch (e) {
      const ta = el('textarea', {}); ta.value = text; document.body.append(ta); ta.select(); document.execCommand('copy'); ta.remove();
    }
    toast('Copied');
  }
  function download(name, text, type) {
    if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.save) { window.webkit.messageHandlers.save.postMessage({ name, text }); return; }
    const a = el('a', { href: URL.createObjectURL(new Blob([text], { type: type || 'application/json' })), download: name });
    document.body.append(a); a.click(); a.remove();
  }
  const KW = new Set('select from where group by having order limit offset join inner left right outer on as and or not in exists is null like between case when then else end distinct union all any some with over partition window desc asc create index drop table explain insert update delete values using cross full interval'.split(' '));
  const FN = new Set('count sum avg min max round concat concat_ws date_format date year month day datediff timestampdiff date_add date_sub str_to_date trim lower upper substring length char_length cast lpad coalesce row_number rank dense_rank ifnull nullif now curdate'.split(' '));
  function highlight(sql) {
    const frag = document.createDocumentFragment();
    const re = /(--[^\n]*)|('(?:[^'\\]|\\.)*')|(`[^`]*`)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_][A-Za-z_0-9]*)|([\s\S])/g;
    let m;
    const span = (c, t) => frag.append(c ? el('span', { class: c }, t) : document.createTextNode(t));
    while ((m = re.exec(sql))) {
      if (m[1]) span('c', m[1]); else if (m[2]) span('s', m[2]); else if (m[3]) span('i', m[3]); else if (m[4]) span('n', m[4]);
      else if (m[5]) { const l = m[5].toLowerCase(); span(KW.has(l) ? 'k' : FN.has(l) ? 'f' : '', m[5]); } else span('', m[6]);
    }
    return frag;
  }
  const codeBlock = (sql) => el('div', {}, el('pre', {}, highlight(sql)), el('button', { onclick: () => copy(sql) }, 'Copy SQL'));
  function vBadge(e) {
    const s = (e.verification || {}).status || 'unverified';
    const map = { 'execution-verified': ['ok', 'execution-verified'], 'executed-single': ['amb', 'ran OK, single formulation'], 'reference-text': ['amb', 'reference text'], 'user-confirmed': ['amb', 'user-confirmed'], unverified: ['bad', 'UNVERIFIED'] };
    const [c, t] = map[s] || ['bad', s];
    return el('span', { class: 'b ' + c, title: (e.verification && e.verification.note) || '' }, t);
  }
  const srcBadge = (e) => el('span', { class: 'b' }, { original: 'original exam', generated: 'generated variation', authored: 'authored', user: 'user entry' }[e.source] || e.source);

  // ---------- engine ----------
  function allEntries() { return BUILTIN.concat(userEntries); }
  async function boot() {
    await window.NWStore.init();
    userEntries = await window.NWStore.all();
    engine = window.NWSearch.createEngine({ entries: allEntries(), schema: SCHEMA });
    const w = await window.NWStore.getSetting('weights');
    if (w) Object.assign(engine.weights, w);
    renderWeights(); renderTheory(); renderSchema(); renderSQLReference(); renderBank(); updateInfo();
    $('#stat').textContent = engine.size() + ' entries · storage: ' + (window.NWStore.persistent ? 'IndexedDB' : 'memory only (IndexedDB unavailable: use Backup)');
  }
  function updateInfo() {
    const c = {}; allEntries().forEach((e) => { const s = (e.verification || {}).status; c[s] = (c[s] || 0) + 1; });
    $('#bInfo').textContent = `${allEntries().length} entries (${BUILTIN.length} built-in, ${userEntries.length} yours). ` + Object.entries(c).map(([k, v]) => `${k}: ${v}`).join(' · ') +
      '. "execution-verified" = main and an independent formulation both ran on the Northwind dump and returned the same result (MySQL 9.7 at build time; the exam DB is 8.0.28). Built-in rows were verified in tools/build_bank.py; your entries never are.';
  }

  // ---------- search ----------
  function doSearch() {
    const q = $('#q').value.trim(); lastQuery = q;
    const box = $('#results'); box.replaceChildren();
    if (!q) { $('#detected').textContent = ''; return; }
    const ver = $('#onlyVerified').checked;
    let out = engine.search(q, { limit: 5, filter: ver ? (r) => r.entry.verification && r.entry.verification.status === 'execution-verified' : null });
    lastOut = out;
    const d = out.detected;
    $('#detected').textContent = `${out.ms.toFixed(1)} ms · detected patterns: ${d.patterns.join(', ') || 'none'} · tables: ${d.tables.join(', ') || 'none'}` + (out.fixes.length ? ` · typo-corrected: ${out.fixes.map((f) => f[0] + '→' + f[1]).join(', ')}` : '');
    if (!out.results.length) {
      box.append(el('div', { class: 'nores' }, el('b', {}, 'No reliable match found. '), 'Nothing in the bank is close enough to this question. No query is invented. Try the pattern hints above, the Northwind section, or rephrase with table/column names.'));
      return;
    }
    box.append(el('p', { class: 'muted' }, 'Scores below are TEXT SIMILARITY only. They say nothing about whether the stored SQL answers your question: read the warnings and compare requirements.'));
    out.results.forEach((r, i) => box.append(resultCard(r, i)));
  }
  function resultCard(r, i) {
    const e = r.entry, p = PATTERNS.get(e.pattern);
    const card = el('div', { class: 'card' },
      el('h3', {}, `#${i + 1}  ${e.id}`),
      el('div', { class: 'badges' }, srcBadge(e), vBadge(e), el('span', { class: 'b' }, e.kind === 'theory' ? 'theory' : 'SQL'), p && el('span', { class: 'b' }, p.name),
        el('span', { class: 'b' }, `text similarity ${(r.score * 100).toFixed(0)}% · ${r.label}`)),
      el('div', { class: 'q' }, e.question));
    r.warnings.forEach((w) => card.append(el('div', { class: 'warn' + (w.sev === 'minor' ? ' minor' : '') }, (w.sev === 'critical' ? 'Requirement differs: ' : 'Check: ') + w.msg)));
    r.notes.forEach((n) => card.append(el('div', { class: 'note' }, n)));
    card.append(el('div', { class: 'note' }, 'Why matched: ' + [r.why.terms.length && 'terms [' + r.why.terms.join(', ') + ']', r.why.patterns.length && 'patterns [' + r.why.patterns.join(', ') + ']', r.why.tables.length && 'tables [' + r.why.tables.join(', ') + ']'].filter(Boolean).join(' · ') + `  (bm25 ${r.parts.bm25.toFixed(2)}, fuzzy ${r.parts.fuzzy.toFixed(2)}, phrase ${r.parts.phrase.toFixed(2)}, pattern ${r.parts.pattern.toFixed(2)}, schema ${r.parts.schema.toFixed(2)}, constraints ${r.parts.constraint.toFixed(2)})`));
    if (e.kind === 'sql') card.append(codeBlock(e.answer)); else card.append(el('p', {}, e.answer));
    card.append(el('div', { class: 'note' }, 'Source: ' + e.sourceRef + ' · updated ' + e.lastUpdated), el('button', { onclick: () => showDetail(e, r) }, 'Open detail view'));
    return card;
  }

  // ---------- detail ----------
  function colInfo(full) {
    const [t, ...rest] = full.split('.'), c = rest.join('.'), tb = SCHEMA.tables.find((x) => x.name === t), col = tb && tb.columns.find((x) => x.name === c);
    return col ? `\`${t}\`.\`${c}\`  ${col.type}${col.pk ? '  PK' : ''}` : full;
  }
  function showDetail(e, r) {
    const b = $('#modalBody'); b.replaceChildren(el('button', { class: 'x', onclick: closeModal }, 'Close'));
    const sec = (t, ...c) => b.append(el('h4', {}, t), ...c);
    b.append(el('h3', {}, e.id), el('div', { class: 'badges' }, srcBadge(e), vBadge(e), el('span', { class: 'b' }, 'difficulty ' + e.difficulty)));
    sec('1 · Original reference question', el('div', { class: 'q card' }, e.question));
    if (e.kind === 'sql') {
      sec('2 · SQL solution', codeBlock(e.answer));
      if (e.alternative) sec('Independent alternative formulation (used for verification)', codeBlock(e.alternative));
    } else {
      sec('2 · Answer', el('p', {}, e.answer));
      (e.examples || []).forEach((x) => b.append(codeBlock(x)));
    }
    sec('3 · Explanation', el('p', {}, e.explanation || '(none)'));
    if (e.verification) b.append(el('p', { class: 'note' }, 'Verification: ' + e.verification.status + (e.verification.note ? ' – ' + e.verification.note : '') + (e.verification.rows != null ? ` · result rows at build time: ${e.verification.rows}` : '') + (e.verification.empty ? ' (EMPTY result on this dump: logic checked, output not informative)' : '')));
    sec('4 · Relevant tables and columns', el('ul', {}, (e.tables || []).map((t) => el('li', {}, '`' + t + '`')), (e.columns || []).map((c) => el('li', {}, colInfo(c)))));
    if (r) {
      sec('5 · Critical conditions compared with your question', el('div', { class: 'q card' }, 'Yours: ' + lastQuery));
      if (!r.warnings.length) b.append(el('p', { class: 'note' }, 'No automatic difference detected. Rule-based checks cover comparison operators, highest/lowest, negation, ties, NULL, sort direction, ALL/ANY, every, per-month vs combined, aggregates, numbers, years, tables. Still read both questions yourself.'));
      r.warnings.forEach((w) => b.append(el('div', { class: 'warn' + (w.sev === 'minor' ? ' minor' : '') }, w.msg)));
    } else sec('5 · Critical conditions', el('p', { class: 'note' }, 'Open this entry from a search result to compare it with your question.'));
    sec('6 · Common mistakes', el('ul', {}, (e.mistakes || []).concat((PATTERNS.get(e.pattern) || {}).mistakes || []).map((m) => el('li', {}, m))));
    const p = PATTERNS.get(e.pattern);
    sec('7 · Related SQL patterns', p ? el('div', {}, el('b', {}, p.name), el('p', {}, p.explanation), codeBlock(p.template), el('p', { class: 'note' }, 'Not when: ' + (p.notWhen.join(' ') || '–'))) : el('p', {}, '–'));
    const rel = (e.related || []).map((id) => allEntries().find((x) => x.id === id)).filter(Boolean);
    if (rel.length) sec('Related questions', el('ul', {}, rel.map((x) => el('li', {}, el('a', { href: '#', onclick: (ev) => { ev.preventDefault(); showDetail(x); } }, x.id), ' ' + x.question.slice(0, 120)))));
    $('#modal').hidden = false; $('#modal').scrollTop = 0;
  }
  function closeModal() { $('#modal').hidden = true; }

  // ---------- theory ----------
  function renderTheory() {
    const q = $('#tq').value.trim(), box = $('#tlist'); box.replaceChildren();
    let items = allEntries().filter((e) => e.kind === 'theory');
    if (q) { const o = engine.search(q, { kind: 'theory', limit: 30 }); const byId = new Map(o.results.map((r) => [r.id, r])); items = o.results.map((r) => r.entry); if (!items.length) box.append(el('div', { class: 'nores' }, 'No reliable match found.')); }
    items.forEach((e) => box.append(el('div', { class: 'card' }, el('h3', {}, e.question), el('div', { class: 'badges' }, srcBadge(e), vBadge(e)), el('p', {}, e.answer),
      (e.examples || []).map((x) => codeBlock(x)), (e.mistakes || []).length ? el('p', { class: 'note' }, 'Common mistakes: ' + e.mistakes.join(' · ')) : null)));
  }

  function renderSQLReference() {
    const normalize = (text) => text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/đ/g, 'd').replace(/[_\s]+/g, ' ').trim();
    const query = normalize($('#sql-ref-q').value), box = $('#sql-ref-list');
    box.replaceChildren();
    let total = 0, shown = 0;
    window.NW_SQL_REFERENCE.forEach((group) => {
      total += group.entries.length;
      const entries = group.entries.filter((entry) => !query || normalize([entry.title, entry.place, entry.explanation, entry.sql, entry.note].join(' ')).includes(query));
      if (!entries.length) return;
      shown += entries.length;
      box.append(el('details', { class: 'card sql-ref-group', open: Boolean(query) },
        el('summary', {}, group.title, el('span', { class: 'muted' }, ` · ${entries.length} mục`)),
        el('p', { class: 'note' }, entries.map((entry) => entry.title).join(' · ')),
        entries.map((entry) => el('article', { class: 'sql-ref-entry' },
          el('h4', {}, entry.title), el('p', { class: 'note' }, 'Vị trí: ' + entry.place),
          el('p', {}, entry.explanation), codeBlock(entry.sql), el('p', { class: 'note' }, entry.note)))));
    });
    $('#sql-ref-stat').textContent = `${shown} / ${total} mục · 20 cặp so sánh từ cheat sheet, thêm các mẫu truy vấn và hàm · mở nhóm để xem ví dụ`;
    if (!shown) box.append(el('p', { class: 'nores' }, 'Không tìm thấy mục phù hợp. Thử từ khóa như OFFSET, DATE_FORMAT, NULL hoặc EXISTS.'));
  }

  // ---------- schema ----------
  function renderSchema() {
    const q = $('#sq').value.trim().toLowerCase(), box = $('#slist'); box.replaceChildren();
    $('#schema-stat').textContent = `${SCHEMA.tables.length} bảng · ${SCHEMA.tables.reduce((total, table) => total + table.columns.length, 0)} cột · ${SCHEMA.tables.reduce((total, table) => total + table.rows, 0)} dòng trong dump · ${SCHEMA.relationships.length} liên kết suy luận`;
    SCHEMA.tables.forEach((t) => {
      const guide = TABLE_GUIDE[t.name] || [], joins = SCHEMA.relationships.filter((relation) => relation.child === t.name);
      const matchesTable = (t.name + ' ' + guide.join(' ')).toLowerCase().includes(q);
      const cols = t.columns.filter((c) => !q || matchesTable || c.name.toLowerCase().includes(q));
      if (q && !cols.length) return;
      const d = el('details', { class: 'card tbl' }); if (q) d.open = true;
      d.append(el('summary', {}, t.name, el('span', { class: 'muted' }, `${t.columns.length} cột · ${t.rows} dòng · PK: ${t.primaryKey.join(' + ') || 'không khai báo'}`)),
        guide[0] ? el('p', {}, guide[0]) : null,
        guide[1] ? el('p', {}, el('strong', {}, 'Cột thường dùng: '), guide[1]) : null,
        guide[2] ? el('p', { class: 'note' }, guide[2]) : null,
        el('div', { class: 'table-scroll', role: 'region', 'aria-label': 'Các cột của ' + t.name, tabindex: '0' },
          el('table', {}, el('thead', {}, el('tr', {}, ['Cột (dùng backtick trong MySQL)', 'Kiểu', 'Vai trò khóa', 'Cho phép NULL'].map((h) => el('th', { scope: 'col' }, h)))),
            el('tbody', {}, cols.map((c) => el('tr', {}, el('td', {}, '`' + c.name + '`'), el('td', {}, c.type),
              el('td', {}, [c.pk ? 'PK' : '', joins.some((relation) => relation.childCol === c.name) ? 'Cột nối (suy luận)' : ''].filter(Boolean).join(' · ')), el('td', {}, c.nullable ? 'có' : 'không')))))),
        joins.length ? el('div', {}, el('h4', {}, 'Nối từ bảng này'), el('ul', {}, joins.map((relation) => el('li', {}, el('code', {}, `\`${relation.childCol}\` = \`${relation.parent}\`.\`${relation.parentCol}\``))))) : null);
      box.append(d);
    });
    if (!box.children.length) box.append(el('p', { class: 'nores' }, 'Không tìm thấy bảng hoặc cột phù hợp.'));
    const rb = $('#rels'); rb.replaceChildren();
    SCHEMA.relationships.filter((r) => !q || [r.child, r.childCol, r.parent, r.parentCol, ...(TABLE_GUIDE[r.child] || []), ...(TABLE_GUIDE[r.parent] || [])].join(' ').toLowerCase().includes(q)).forEach((r) => {
      const ok = r.dataVerified;
      const parent = SCHEMA.tables.find((table) => table.name === r.parent);
      rb.append(el('details', { class: 'card' }, el('summary', {}, `\`${r.child}\`.\`${r.childCol}\` = \`${r.parent}\`.\`${r.parentCol}\``),
        el('p', {}, el('span', { class: 'b ' + (ok ? 'ok' : 'amb') }, ok ? 'Đã kiểm tra dữ liệu: 0 giá trị mồ côi' : 'Chưa xác nhận trên dữ liệu (' + (r.check ? r.check.childNonNull + ' giá trị khác NULL' : 'chưa có thống kê') + ')')),
        el('p', { class: 'note' }, 'Nhiều–một theo mô hình: nhiều dòng bảng con có thể tham chiếu một dòng bảng cha. Không có ràng buộc FOREIGN KEY.'),
        parent && !(parent.primaryKey.length === 1 && parent.primaryKey[0] === r.parentCol) ? el('p', { class: 'note' }, 'Cột đích không được khai báo là khóa chính đơn; kiểm tra tính duy nhất trước khi giả định JOIN chỉ ghép một dòng cha.') : null,
        r.note ? el('div', { class: 'note' }, r.note) : null, codeBlock(r.example)));
    });
    if (!rb.children.length) rb.append(el('p', { class: 'muted' }, 'Không có liên kết phù hợp với bộ lọc.'));
  }

  // ---------- bank ----------
  function renderBank() {
    const q = $('#bq').value.trim().toLowerCase(), st = $('#bStatus').value, so = $('#bSource').value, box = $('#blist'); box.replaceChildren();
    const items = allEntries().filter((e) => (!st || (e.verification || {}).status === st) && (!so || e.source === so) &&
      (!q || (e.id + ' ' + e.question + ' ' + e.pattern + ' ' + (e.tags || []).join(' ')).toLowerCase().includes(q)));
    $('#bq').title = items.length + ' shown';
    items.slice(0, 200).forEach((e) => box.append(el('div', { class: 'card' }, el('div', { class: 'badges' }, el('b', {}, e.id), srcBadge(e), vBadge(e), el('span', { class: 'b' }, e.pattern || '-')),
      el('div', { class: 'q' }, e.question.length > 220 ? e.question.slice(0, 220) + '…' : e.question),
      el('button', { onclick: () => showDetail(e) }, 'Inspect'), e.source === 'user' ? [el('button', { onclick: () => editForm(e) }, 'Edit'), el('button', { class: 'danger', onclick: () => delEntry(e.id) }, 'Delete')] : null)));
    if (items.length > 200) box.append(el('p', { class: 'muted' }, `Showing 200 of ${items.length}: refine the filter.`));
  }
  async function saveUser(list) {
    await window.NWStore.putMany(list);
    list.forEach((e) => { const i = userEntries.findIndex((x) => x.id === e.id); if (i >= 0) userEntries[i] = e; else userEntries.push(e); engine.add(e); });
    renderBank(); renderTheory(); updateInfo(); $('#stat').textContent = engine.size() + ' entries';
  }
  async function delEntry(id) {
    if (!confirm('Delete entry ' + id + '?')) return;
    await window.NWStore.del(id); userEntries = userEntries.filter((e) => e.id !== id); engine.remove(id); renderBank(); renderTheory(); updateInfo();
  }
  function editForm(old) {
    const b = $('#modalBody'); b.replaceChildren(el('button', { class: 'x', onclick: closeModal }, 'Close'), el('h3', {}, old ? 'Edit ' + old.id : 'Add entry'));
    const f = (label, node) => el('label', {}, label, node);
    const kind = el('select', {}, el('option', { value: 'sql' }, 'SQL'), el('option', { value: 'theory' }, 'Theory'));
    const question = el('textarea', { rows: 3 }), answer = el('textarea', { rows: 7 }), expl = el('textarea', { rows: 2 });
    const pattern = el('select', {}, el('option', { value: '' }, '(none)'), [...PATTERNS.values()].map((p) => el('option', { value: p.id }, p.name)));
    const tags = el('input', { type: 'text', placeholder: 'comma separated' }), tables = el('input', { type: 'text', placeholder: 'comma separated table names' });
    const ver = el('select', {}, el('option', { value: 'unverified' }, 'unverified'), el('option', { value: 'user-confirmed' }, 'user-confirmed (I ran it myself)'));
    if (old) { kind.value = old.kind; question.value = old.question; answer.value = old.answer; expl.value = old.explanation || ''; pattern.value = old.pattern || ''; tags.value = (old.tags || []).join(', '); tables.value = (old.tables || []).join(', '); ver.value = old.verification.status; }
    b.append(el('div', { class: 'form' }, f('Type', kind), f('Question', question), f('SQL answer / theory answer', answer), f('Explanation', expl), f('Pattern', pattern), f('Tags', tags), f('Tables', tables), f('Verification', ver),
      el('p', { class: 'note' }, 'The app cannot execute SQL, so it never marks anything "execution-verified".'),
      el('button', { class: 'primary', onclick: async () => {
        if (!question.value.trim() || !answer.value.trim()) return toast('Question and answer are required');
        const split = (s) => s.split(',').map((x) => x.trim()).filter(Boolean);
        await saveUser([{ id: old ? old.id : 'U-' + Date.now().toString(36), kind: kind.value, source: 'user', sourceRef: 'added in app', question: question.value.trim(), difficulty: 2, pattern: pattern.value,
          tags: split(tags.value), tables: split(tables.value), columns: [], answer: answer.value.trim(), explanation: expl.value.trim(), mistakes: old ? old.mistakes : [], related: [], examples: [],
          verification: { status: ver.value, note: 'entered by user' }, lastUpdated: TODAY }]);
        closeModal(); toast('Saved');
      } }, 'Save')));
    $('#modal').hidden = false;
  }
  function parseCSV(t) {
    const rows = []; let r = [], c = '', q = false;
    for (let i = 0; i < t.length; i++) {
      const ch = t[i];
      if (q) { if (ch === '"') { if (t[i + 1] === '"') { c += '"'; i++; } else q = false; } else c += ch; }
      else if (ch === '"') q = true; else if (ch === ',') { r.push(c); c = ''; } else if (ch === '\n' || ch === '\r') { if (ch === '\r' && t[i + 1] === '\n') i++; r.push(c); c = ''; if (r.some((x) => x !== '')) rows.push(r); r = []; } else c += ch;
    }
    r.push(c); if (r.some((x) => x !== '')) rows.push(r);
    const h = rows.shift().map((x) => x.trim().toLowerCase());
    return rows.map((row) => Object.fromEntries(h.map((k, i) => [k, row[i] || ''])));
  }
  function normalizeImport(o) {
    const list = (s) => (Array.isArray(s) ? s : String(s || '').split(/[;,]/)).map((x) => String(x).trim()).filter(Boolean);
    const q = String(o.question || '').trim(), a = String(o.answer || o.sql || '').trim();
    if (!q || !a) return null;
    let id = String(o.id || '').trim();
    if (!id || BUILTIN.some((e) => e.id === id)) id = 'U-' + Math.random().toString(36).slice(2, 9);
    const kind = o.kind === 'theory' ? 'theory' : 'sql';
    const keep = o.verification && o.verification.status === 'reference-text' && kind === 'theory';
    return { id, kind, source: 'user', sourceRef: 'imported' + (o.sourceRef ? ': ' + o.sourceRef : ''), question: q, difficulty: +o.difficulty || 2, pattern: PATTERNS.has(o.pattern) ? o.pattern : '',
      tags: list(o.tags), tables: list(o.tables), columns: list(o.columns), answer: a, explanation: String(o.explanation || ''), mistakes: list(o.mistakes), related: [], examples: Array.isArray(o.examples) ? o.examples : [],
      verification: { status: keep ? 'reference-text' : 'unverified', note: 'imported; not re-verified here' }, lastUpdated: TODAY };
  }
  async function importFile(file) {
    const text = await file.text(); let rows;
    try { rows = file.name.toLowerCase().endsWith('.csv') ? parseCSV(text) : (() => { const j = JSON.parse(text); return Array.isArray(j) ? j : j.entries; })(); }
    catch (e) { return toast('Cannot parse file: ' + e.message); }
    const ok = (rows || []).map(normalizeImport).filter(Boolean);
    await saveUser(ok); toast(`Imported ${ok.length} of ${(rows || []).length} rows (all marked unverified)`);
  }

  // ---------- weights ----------
  function renderWeights() {
    const box = $('#weights'); box.replaceChildren();
    ['bm25', 'fuzzy', 'phrase', 'pattern', 'schema', 'constraint', 'critPenalty', 'minorPenalty', 'minScore', 'minCoverage'].forEach((k) => {
      box.append(el('label', { class: 'w' }, k, el('input', { type: 'number', step: '0.01', min: '0', max: '2', value: engine.weights[k], onchange: async (ev) => { engine.weights[k] = +ev.target.value; await window.NWStore.setSetting('weights', engine.weights); if (lastQuery) doSearch(); } })));
    });
  }

  // ---------- wiring ----------
  document.addEventListener('DOMContentLoaded', async () => {
    document.querySelectorAll('#tabs button').forEach((b) => b.addEventListener('click', () => {
      document.querySelectorAll('#tabs button').forEach((x) => {
        x.classList.toggle('on', x === b);
        if (x === b) x.setAttribute('aria-current', 'page'); else x.removeAttribute('aria-current');
      });
      document.querySelectorAll('main > section').forEach((section) => (section.hidden = section.id !== 'tab-' + b.dataset.tab));
    }));
    $('#bStatus').append(el('option', {}, 'user-confirmed'));
    $('#go').addEventListener('click', doSearch);
    $('#clear').addEventListener('click', () => { $('#q').value = ''; $('#results').replaceChildren(); $('#detected').textContent = ''; $('#q').focus(); });
    $('#q').addEventListener('keydown', (e) => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); doSearch(); } });
    $('#onlyVerified').addEventListener('change', () => lastQuery && doSearch());
    $('#tq').addEventListener('input', renderTheory); $('#sq').addEventListener('input', renderSchema);
    $('#sql-ref-q').addEventListener('input', renderSQLReference);
    ['#bq', '#bStatus', '#bSource'].forEach((s) => $(s).addEventListener('input', renderBank));
    $('#bAdd').addEventListener('click', () => editForm(null));
    $('#bExport').addEventListener('click', () => download('question-bank-' + TODAY + '.json', JSON.stringify({ version: 1, patterns: window.NW_BANK.patterns, entries: allEntries() }, null, 1)));
    $('#bBackup').addEventListener('click', () => download('sql-finder-backup-' + TODAY + '.json', JSON.stringify({ type: 'nw-backup', version: 1, entries: userEntries, weights: engine.weights }, null, 1)));
    $('#bImport').addEventListener('change', async (e) => { if (e.target.files[0]) await importFile(e.target.files[0]); e.target.value = ''; });
    $('#bRestore').addEventListener('change', async (e) => {
      const f = e.target.files[0]; if (!f) return; e.target.value = '';
      try {
        const j = JSON.parse(await f.text()); if (j.type !== 'nw-backup') throw new Error('not a backup file');
        for (const old of userEntries) engine.remove(old.id);
        await window.NWStore.clear(); userEntries = [];
        await saveUser(j.entries || []);
        if (j.weights) { Object.assign(engine.weights, j.weights); await window.NWStore.setSetting('weights', engine.weights); renderWeights(); }
        toast('Restored ' + (j.entries || []).length + ' entries');
      } catch (err) { toast('Restore failed: ' + err.message); }
    });
    $('#bReset').addEventListener('click', async () => { if (!confirm('Delete all ' + userEntries.length + ' of your entries? Built-in entries stay.')) return; userEntries.forEach((e) => engine.remove(e.id)); userEntries = []; await window.NWStore.clear(); renderBank(); renderTheory(); updateInfo(); });
    $('#wReset').addEventListener('click', async () => { Object.assign(engine.weights, window.NWSearch.DEFAULT_WEIGHTS); await window.NWStore.setSetting('weights', engine.weights); renderWeights(); });
    $('#modal').addEventListener('click', (e) => { if (e.target.id === 'modal') closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });
    await boot();
  });
})();
