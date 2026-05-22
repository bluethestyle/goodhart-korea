"""다크 카드 영역 안에 다크 텍스트가 있는지 점검."""
import os, re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r'd:\workspace\재정자료분석')

for fn in ['slide-04', 'slide-13', 'slide-18', 'slide-23', 'slide-25', 'slide-26', 'slide-27']:
    full = f'paper/재정데이터 분석 ppt/figma-wireframes/{fn}.svg'
    with open(full, encoding='utf-8') as f:
        t = f.read()

    # 다크 카드 영역 추출 (x, y, width, height)
    rect_m = re.findall(r'<rect[^>]*x="(\d+)"[^>]*y="(\d+)"[^>]*width="(\d+)"[^>]*height="(\d+)"[^>]*fill="#191f28"[^>]*>', t)
    print(f'\n=== {fn} — dark cards: {len(rect_m)}')
    for x, y, w, h in rect_m:
        x, y, w, h = int(x), int(y), int(w), int(h)
        print(f'  card: x={x} y={y} w={w} h={h} → area ({x}~{x+w}, {y}~{y+h})')

    # 모든 text의 x, y, fill 추출
    txt_m = re.findall(r'<text[^>]*x="(\d+)"[^>]*y="(\d+)"[^>]*fill="(#[a-fA-F0-9]{6})"[^>]*>([^<]+)', t)
    risky = []
    for tx, ty, fill, content in txt_m:
        tx, ty = int(tx), int(ty)
        # 다크 카드 영역 안에 있는지
        for x, y, w, h in rect_m:
            x, y, w, h = int(x), int(y), int(w), int(h)
            if x <= tx <= x+w and y <= ty <= y+h:
                # 어두운 텍스트 fill (#191f28, #4e5968)이면 가독성 문제
                if fill.lower() in ('#191f28', '#4e5968'):
                    risky.append((tx, ty, fill, content[:30]))
                break
    if risky:
        print(f'  ⚠️ risky text on dark card: {len(risky)}')
        for r in risky:
            print(f'    @{r[0]},{r[1]} fill={r[2]}: {r[3]}')
    else:
        print(f'  ✓ no readability issue')
