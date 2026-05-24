"""Slide 28 우측 scaleogram 다운샘플 — 슬라이드 친화 사이즈로 (1280px 친화).

pywt 환경 호환 문제로 raw CWT 재생성 불가. 기존 paper/figures/h28_scaleogram.png
(1900×1090)을 1280→1500px 사이로 다운샘플만 적용.

archetype color border / 분석 대상·비교군 라벨은 피그마에서 후처리 권장
(matplotlib subplot 좌표 정밀 추정이 위험 부담).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
src = ROOT / 'paper' / 'figures' / 'h28_scaleogram.png'

im = Image.open(src).convert('RGB')
W, H = im.size
print(f'원본: {W}x{H}')

target_w = 1500
if W > target_w:
    new_h = H * target_w // W
    im = im.resize((target_w, new_h), Image.LANCZOS)
    W, H = im.size

im.save(src, optimize=True)
print(f'저장: {src} | {W}x{H}')
