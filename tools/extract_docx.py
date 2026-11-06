"""Extract exam questions verbatim from the .docx -> data/mock_questions.json. Usage: python3 -I tools/extract_docx.py in.docx out.json"""
import sys, re, json, zipfile, html
src, out = sys.argv[1], sys.argv[2]
x = zipfile.ZipFile(src).read('word/document.xml').decode('utf8')
paras = []
for p in re.findall(r'<w:p[ >].*?</w:p>', x, flags=re.S):
    p = re.sub(r'<w:br\s*/>', '\n', p)
    t = html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, flags=re.S)))
    if t.strip(): paras.append(t.strip())
qs, cur = [], None
for t in paras[1:]:
    m = re.match(r'\((\d+)\s*points?\)\s*(.*)', t, re.S)
    if m:
        cur = {'no': len(qs) + 1, 'points': int(m.group(1)), 'lines': [m.group(2)]}
        qs.append(cur)
    elif cur: cur['lines'].append(t)
for q in qs: q['text'] = '\n'.join(q.pop('lines'))
json.dump({'intro': paras[0], 'questions': qs}, open(out, 'w'), indent=1, ensure_ascii=False)
print(len(qs), 'questions')
