"""Find unescaped tildes in Typst source that likely should be \\~.

Typst treats a bare ~ as a non-breaking space (invisible). Authors using
~ as a range separator (e.g., 2015~2025) need \\~ to render an actual tilde.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

for fname, label in [('d:/workspace/재정자료분석/paper/main_v2.typ', 'KR'),
                     ('d:/workspace/재정자료분석/paper/main_v2_en.typ', 'EN')]:
    with open(fname, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f'\n=== {label} ({fname}) ===')
    found = 0
    for i, line in enumerate(lines, 1):
        if line.lstrip().startswith('//'):
            continue
        # Strip math regions $...$ (Typst inline math) — tildes inside are fine
        cleaned = re.sub(r'\$[^$\n]*\$', lambda m: ' ' * len(m.group(0)), line)
        # Strip cite/link URLs
        cleaned = re.sub(r'#link\("[^"]*"\)', lambda m: ' ' * len(m.group(0)), cleaned)
        cleaned = re.sub(r'#cite\([^)]*\)', lambda m: ' ' * len(m.group(0)), cleaned)
        # Find ~ not preceded by backslash
        for m in re.finditer(r'(?<!\\)~', cleaned):
            pos = m.start()
            ctx = line.rstrip('\n')[max(0, pos - 30):min(len(line), pos + 30)]
            print(f'L{i:5d} col{pos+1:3d}: {ctx}')
            found += 1
    print(f'  Total unescaped ~ found: {found}')
