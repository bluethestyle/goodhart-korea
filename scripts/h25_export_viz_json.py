"""H25: 인터랙티브 시각화용 데이터 JSON export.

출력: docs/interactive/data/

  ministry_network.json   H5 부처 force network (51 nodes, 5 co-cluster)
  archetype_sankey.json   분야→사업원형→outcome 부호 (Sankey)
  rdd_scatter.json        H22 RDD 11~12월 일별 집행
  mapper_graph.json       H4 v3 Mapper 32 nodes / 38 edges
  cluster_outcome.json    4 cluster × 15 outcome corr_diff matrix
"""
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import pandas as pd
import duckdb

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'interactive', 'data')
os.makedirs(OUT, exist_ok=True)

# 1. 부처 network (H5 v2 11y)
print('1. ministry_network.json')
expo = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H5_ministry_exposure_11y.csv'))
expo.columns = ['ministry'] + list(expo.columns[1:])
co = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H5_cocluster_assignment_11y.csv'))
co_min = co[co['node_type']=='ministry'].set_index(co.columns[0])['label']

# 활동 임베딩에서 부처별 평균 12피처
emb = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H3_activity_embedding_11y.csv'))
feat_cols = ['amp_12m_norm','chooyeon_pct','direct_invest_pct','personnel_pct',
             'operating_pct','log_annual']
ofc_feat = emb.groupby('OFFC_NM')[feat_cols].mean()
ofc_size = emb.groupby('OFFC_NM').size()

nodes = []
for m in expo['ministry']:
    if m not in ofc_feat.index: continue
    n_actv = int(ofc_size.get(m, 0))
    if n_actv < 5: continue
    nodes.append({
        'id': m,
        'name': m,
        'category': int(co_min.get(m, 0)) if m in co_min.index else 0,
        'value': float(expo[expo['ministry']==m]['exposure_score'].iloc[0]),
        'symbolSize': 10 + n_actv ** 0.5 * 3,
        'n_activities': n_actv,
        'chooyeon_pct': float(ofc_feat.loc[m, 'chooyeon_pct']),
    })

# Edges: cosine similarity > 0.55 (H3 그래프와 동일)
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
node_names = [n['id'] for n in nodes]
sub_feat = ofc_feat.loc[node_names]
sub_z = (sub_feat - sub_feat.mean()) / sub_feat.std()
sim = cosine_similarity(sub_z.values)
np.fill_diagonal(sim, 0)
edges = []
for i in range(len(node_names)):
    for j in range(i+1, len(node_names)):
        if sim[i,j] > 0.55:
            edges.append({'source': node_names[i], 'target': node_names[j],
                          'value': float(sim[i,j])})

categories = [
    {'name': 'CC0 행정형'},
    {'name': 'CC1 사업형'},
    {'name': 'CC2 분기말집중'},
    {'name': 'CC3 직접투자'},
    {'name': 'CC4 출연금전담'},
]
json.dump({'nodes': nodes, 'links': edges, 'categories': categories},
          open(os.path.join(OUT, 'ministry_network.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'   nodes={len(nodes)}, edges={len(edges)}')

# 2. archetype Sankey: 분야 → 원형 → outcome 부호
print('2. archetype_sankey.json')
arch_oc = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H8_archetype_outcome_v3.csv'))
sankey_nodes = []
sankey_links = []

flds = sorted(arch_oc['fld'].unique())
arches = ['chooyeon', 'direct_invest', 'extreme_gaming', 'normal', 'personnel']
for f in flds:
    sankey_nodes.append({'name': f})
for a in arches:
    sankey_nodes.append({'name': f'A_{a}'})
sankey_nodes.append({'name': 'outcome ↑ (양상관)'})
sankey_nodes.append({'name': 'outcome ↓ (음상관)'})

for _, r in arch_oc.iterrows():
    if pd.isna(r['corr_diff']): continue
    val = abs(float(r['corr_diff']))
    if val < 0.1: continue   # 약한 신호 노이즈 제거
    # 분야 → 원형
    sankey_links.append({
        'source': r['fld'],
        'target': f'A_{r["arch_grp"]}',
        'value': val,
    })
    # 원형 → outcome 부호
    target = 'outcome ↑ (양상관)' if r['corr_diff'] > 0 else 'outcome ↓ (음상관)'
    sankey_links.append({
        'source': f'A_{r["arch_grp"]}',
        'target': target,
        'value': val,
    })

json.dump({'nodes': sankey_nodes, 'links': sankey_links},
          open(os.path.join(OUT, 'archetype_sankey.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'   nodes={len(sankey_nodes)}, links={len(sankey_links)}')

# 3. RDD scatter: 11월·12월 일별 집행 (분야×활동 평균)
print('3. rdd_scatter.json')
con = duckdb.connect(os.path.join(ROOT, 'data', 'warehouse.duckdb'), read_only=True)
df = con.execute("""
    SELECT FSCL_YY AS year, EXE_M AS month, FLD_NM AS fld,
           AVG(EP_AMT) AS avg_exp, COUNT(*) AS n_obs
    FROM monthly_exec
    WHERE FSCL_YY BETWEEN 2015 AND 2024
      AND EXE_M IN (10, 11, 12)
      AND EP_AMT > 0
    GROUP BY 1,2,3
""").fetchdf()
con.close()

# 분야별 월별 평균 (10/11/12)
sub = df.groupby(['fld', 'month'])['avg_exp'].mean().reset_index()
# 비율: 12월 / 11월
piv = sub.pivot(index='fld', columns='month', values='avg_exp').reset_index()
piv.columns = ['fld', 'oct', 'nov', 'dec']
piv['jump_dec_nov'] = piv['dec'] / piv['nov']
piv = piv.sort_values('jump_dec_nov', ascending=False)

scatter = []
for _, r in piv.iterrows():
    scatter.append({
        'fld': r['fld'],
        'oct': float(r['oct']),
        'nov': float(r['nov']),
        'dec': float(r['dec']),
        'jump': float(r['jump_dec_nov']),
    })
json.dump(scatter, open(os.path.join(OUT, 'rdd_scatter.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'   {len(scatter)} 분야')

# 4. Mapper graph (H4 v3)
print('4. mapper_graph.json')
nodes_m = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H4_mapper_nodes_11y.csv'))
mnodes = []
for _, r in nodes_m.iterrows():
    mnodes.append({
        'id': str(r['node_id']),
        'name': r.get('top_field', ''),
        'value': float(r['size']),
        'symbolSize': 5 + (float(r['size']) ** 0.5) * 2,
        'amp_12m': float(r['mean_amp_12m']),
        'chooyeon': float(r['mean_chooyeon']),
        'cluster': int(r['cluster_dom']),
    })
# Mapper edges는 csv에 없음 — 그래프 위상 H4에 정의됨. 단순화
mlinks = []  # 별도 export 필요시 추가
json.dump({'nodes': mnodes, 'links': mlinks},
          open(os.path.join(OUT, 'mapper_graph.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'   nodes={len(mnodes)}')

# 5. cluster × outcome heatmap (H4 v3)
print('5. cluster_outcome.json')
co = pd.read_csv(os.path.join(ROOT, 'data', 'results', 'H4_cluster_outcome_corr_11y_v3.csv'))
cells = []
for _, r in co.iterrows():
    cells.append({
        'cluster': int(r['cluster']),
        'outcome': r['metric'],
        'corr_diff': float(r['corr_diff']),
        'corr_levels': float(r['corr_levels']) if 'corr_levels' in r and not pd.isna(r['corr_levels']) else None,
        'n': int(r['n_year']),
    })
json.dump(cells, open(os.path.join(OUT, 'cluster_outcome.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print(f'   cells={len(cells)}')

print(f'\n전체 export 완료: {OUT}')
