"""차트 자산 다운샘플 (>1280px → 1280px). 발표 시 정상 노출 확보.

특수:
- h3_umap: 상단 (4 archetype) 만 crop 후 다운샘플
- 나머지: 단순 가로 1280 비율 유지
"""
from PIL import Image
from pathlib import Path

print('=== 다운샘플 시작 ===')

# h3_umap: 상단 crop (4 archetype 산점도만)
p = Path('paper/figures/h3_umap.png')
im = Image.open(p)
w, h = im.size
print(f'\n{p.name}: 원본 {w}x{h}')

# 상단 50% crop (4 archetype 부분)
top = im.crop((0, 0, w, h // 2))
new_h = (h // 2) * 1280 // w
top_small = top.resize((1280, new_h), Image.LANCZOS)
out = p.with_name(p.stem + '_top_small' + p.suffix)
top_small.save(out)
print(f'  상단 crop + 다운샘플: 1280x{new_h} -> {out.name}')

# 일반 다운샘플 자산
targets = [
    'paper/figures/h28_scaleogram.png',
    'paper/figures/h10_cpi_control.png',
    'paper/figures/h6_lag_amp.png',
    'paper/figures/h6_robustness.png',
]

for src in targets:
    p = Path(src)
    im = Image.open(p)
    w, h = im.size
    print(f'\n{p.name}: 원본 {w}x{h}')
    if w > 1280:
        new_h = h * 1280 // w
        im_s = im.resize((1280, new_h), Image.LANCZOS)
        out = p.with_name(p.stem + '_small' + p.suffix)
        im_s.save(out)
        print(f'  다운샘플: 1280x{new_h} -> {out.name}')
    else:
        print(f'  이미 작음, 스킵')

print('\n=== 다운샘플 완료 ===')
