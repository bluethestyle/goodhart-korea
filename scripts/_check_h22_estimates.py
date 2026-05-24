"""H22 RDD estimates CSV 전수 검사 — Slide 22 4 cutoff 수치의 sample 단위 확인."""
import pandas as pd
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

est = pd.read_csv('data/results/H22_rdd_estimates.csv')
print('=== H22_rdd_estimates.csv ===')
print('columns:', est.columns.tolist())
print('shape:', est.shape)
print()
print(est.to_string())
print()

fld = pd.read_csv('data/results/H22_field_rdd.csv')
print('=== H22_field_rdd.csv ===')
print('columns:', fld.columns.tolist())
print('shape:', fld.shape)
