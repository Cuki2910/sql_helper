"""Extract 'Qn. text' paragraphs verbatim from the lab docx -> JSON. Usage: python3 -I tools/extract_lab_docx.py in.docx out.json"""
import sys, re, json, zipfile, html
x = zipfile.ZipFile(sys.argv[1]).read('word/document.xml').decode('utf8')
qs = []
for p in re.findall(r'<w:p[ >].*?</w:p>', x, flags=re.S):
    t = html.unescape(''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, flags=re.S))).strip()
    m = re.match(r'Q(\d+)\.\s*(.*)', t, re.S)
    if m: qs.append({'no': int(m.group(1)), 'text': m.group(2)})
json.dump({'source': sys.argv[1].split('/')[-1], 'questions': qs}, open(sys.argv[2], 'w'), indent=1, ensure_ascii=False)
print(len(qs), 'lab questions')
