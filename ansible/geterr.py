import json
import re
from pathlib import Path

text = Path("err").read_text()

m = re.search(r'=>\s*(\{.*\})', text, re.S)
if m:
    data = json.loads(m.group(1))
    for k,v in data.items():
        print(k,v,sep=':')

