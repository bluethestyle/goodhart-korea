import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
os.chdir(r'd:\workspace\재정자료분석')
files = sorted(glob.glob('paper/*/figma-wireframes/slide-*.svg'))
print(f'files: {len(files)}')
for i, fn in enumerate(files, 1):
    with open(fn, encoding='utf-8') as f:
        text = f.read()
    part = re.findall(r'(PART [^<]+|CLOSING|FISCAL DATA[^<]*)', text)
    titles = re.findall(r'font-size="(?:96|56|48|40|36|32|28|24|22)"[^>]*>([^<]+)', text)
    no = re.findall(r'(\d{2}\s*/\s*27)', text)
    print(f'\n### {i:02d}  {part[0] if part else "(no part)"}  [{no[0] if no else "--"}]')
    seen = set()
    for t in titles[:6]:
        t = t.replace('&#34;', '"').replace('\\n', ' / ').strip()
        if t and t not in seen:
            print(f'   - {t}')
            seen.add(t)
