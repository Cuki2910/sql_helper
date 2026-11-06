import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as directory:
    work = Path(directory)
    (work / 'data').mkdir()
    (work / 'js').mkdir()
    source = work / 'fixture.sql'
    source.write_text("""CREATE TABLE `sample` (
  `ID` int NOT NULL,
  `value` varchar(100),
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB;
CREATE TABLE `empty` (
  `ID` int NOT NULL
) ENGINE=InnoDB;
INSERT INTO `sample` VALUES (1,'parentheses (inside)'),(2,'quote \\' ( inside');
INSERT INTO `sample` VALUES
(3,'doubled '' quote ) inside'),
(4,COALESCE(NULL,'nested function ( )'));""", encoding='utf8')
    environment = dict(os.environ)
    environment.pop('MYSQL_SOCK', None)
    subprocess.run([sys.executable, '-I', str(root / 'tools/extract_schema.py'), str(source)],
                   cwd=work, env=environment, check=True, capture_output=True, text=True)
    schema = json.loads((work / 'data/schema.json').read_text())
    assert {table['name']: table['rows'] for table in schema['tables']} == {'sample': 4, 'empty': 0}
    browser_data = (work / 'js/data_schema.js').read_text()
    assert json.loads(browser_data.removeprefix('window.NW_SCHEMA = ').rstrip(';\n')) == schema

print('Schema row counts: same-line tuples, multiple inserts, quoted parentheses, nested values, empty tables OK')
