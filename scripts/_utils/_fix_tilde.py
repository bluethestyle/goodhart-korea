"""Escape unescaped tildes in main_v2.typ (KR)."""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = 'd:/workspace/재정자료분석/paper/main_v2.typ'

with open(TARGET, 'r', encoding='utf-8') as f:
    lines = f.readlines()

changed_lines = []
out = []
for i, line in enumerate(lines, 1):
    if line.lstrip().startswith('//'):
        out.append(line)
        continue
    masks = []
    def mask(pat, s):
        def _r(m):
            masks.append(m.group(0))
            return f'\x00{len(masks)-1}\x00'
        return re.sub(pat, _r, s)
    masked = line
    masked = mask(r'\$[^$\n]*\$', masked)
    masked = mask(r'#link\("[^"]*"\)', masked)
    masked = mask(r'#cite\([^)]*\)', masked)

    new = re.sub(r'(?<!\\)~', r'\\~', masked)
    new = re.sub(r'\x00(\d+)\x00', lambda m: masks[int(m.group(1))], new)

    if new != line:
        changed_lines.append((i, line.rstrip(), new.rstrip()))
    out.append(new)

# Write back FIRST, then print (so even if print fails the write succeeds)
with open(TARGET, 'w', encoding='utf-8') as f:
    f.writelines(out)

print(f'Changed lines: {len(changed_lines)}')
for i, old, new in changed_lines:
    print(f'L{i}:')
    print(f'  -: {old}')
    print(f'  +: {new}')
