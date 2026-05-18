"""
기관별 산출물 패키지 빌드

deliverables/
  audit_board/  — 감사원 (extreme_50 이미 h29에서 생성됨)
  npbo/         — 국회 예산정책처: 부처 4분면 + 51 부처 진단표
  moef/         — 기획재정부: 출연금형 cycle 지표
  moi/          — 행정안전부: dashboard 사양
  kfi/          — 한국재정정보원: KODAS 카탈로그 통계

각 폴더: Parquet 정본 + CSV 핸드오프본
"""
from pathlib import Path
import shutil
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "data" / "results"
DEL = ROOT / "deliverables"


def _dual_write(df: pd.DataFrame, base: Path) -> tuple[int, int]:
    base.parent.mkdir(parents=True, exist_ok=True)
    pq = base.with_suffix(".parquet")
    cs = base.with_suffix(".csv")
    df.to_parquet(pq, index=False, compression="snappy")
    df.to_csv(cs, index=False, encoding="utf-8-sig")
    return pq.stat().st_size, cs.stat().st_size


def build_npbo() -> None:
    quad = pd.read_csv(RES / "H14_ministry_outcome_combined.csv")
    quad_out = quad.rename(columns={
        "OFFC_NM": "ministry",
        "w_corr_diff": "gaming_outcome_corr",
        "exposure_score": "exposure_score",
        "co_cluster": "co_cluster_id",
        "pct_chooyeon": "pct_grant_program",
        "pct_sub05": "pct_extreme_gaming",
        "pct_sub01": "pct_mild_gaming",
        "quadrant": "quadrant",
        "outcomes": "matched_outcomes",
    })
    _dual_write(quad_out, DEL / "npbo" / "ministry_quadrant")

    diag = pd.read_csv(RES / "H5_ministry_exposure.csv")
    diag_out = diag.rename(columns={
        "OFFC_NM": "ministry",
        "n_actv": "n_activities",
        "exposure_score": "exposure_score",
        "exposure_budget": "exposure_budget_weighted",
        "co_cluster": "co_cluster_id",
        "pct_chooyeon": "pct_grant_program",
        "pct_sub05": "pct_extreme_gaming",
        "pct_sub01": "pct_mild_gaming",
    }).sort_values("exposure_score", ascending=False)
    _dual_write(diag_out, DEL / "npbo" / "ministry_diagnosis")


def build_moef() -> None:
    psd = pd.read_csv(RES / "H27_psd_archetype_avg.csv")
    coh = pd.read_csv(RES / "H27_coherence_intra_archetype.csv")
    wav = pd.read_csv(RES / "H28_v2_period_split.csv")
    trans = pd.read_csv(RES / "H28_v2_transitions.csv")

    arch_map = {0: "인건비형", 1: "자산취득형", 2: "출연금형", 3: "정상사업"}
    for d in (psd, coh, wav, trans):
        if "archetype" in d.columns and pd.api.types.is_integer_dtype(d["archetype"]):
            d["archetype_name"] = d["archetype"].map(arch_map)

    psd_out = psd[psd.get("archetype_name", psd["archetype"]).isin(
        ["출연금형", 2]) | (psd["archetype"] == 2)] if "archetype_name" in psd else psd
    _dual_write(psd, DEL / "moef" / "archetype_psd")
    _dual_write(coh, DEL / "moef" / "archetype_coherence")
    _dual_write(wav, DEL / "moef" / "wavelet_period_split")
    _dual_write(trans, DEL / "moef" / "wavelet_transitions")


def build_kfi() -> None:
    con = duckdb.connect((ROOT / "data" / "warehouse.duckdb").as_posix(),
                         read_only=True)
    cat_summary = con.execute("""
        SELECT instNm AS institution,
               dsHgNm AS dataset_group,
               COUNT(*) AS n_datasets
        FROM kodas_catalog
        WHERE instNm IS NOT NULL
        GROUP BY instNm, dsHgNm
        ORDER BY n_datasets DESC
    """).fetchdf()
    _dual_write(cat_summary, DEL / "kfi" / "kodas_catalog_summary")

    field_summary = con.execute("""
        SELECT dsHgNm AS field,
               COUNT(*) AS n_datasets,
               COUNT(DISTINCT instNm) AS n_institutions
        FROM kodas_catalog
        WHERE dsHgNm IS NOT NULL
        GROUP BY dsHgNm
        ORDER BY n_datasets DESC
    """).fetchdf()
    _dual_write(field_summary, DEL / "kfi" / "kodas_field_summary")
    con.close()


def copy_dashboard() -> None:
    src = ROOT / "paper" / "figures" / "dashboard_mockup.png"
    dst = DEL / "moi" / "dashboard_mockup.png"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst)


def main() -> None:
    build_npbo()
    build_moef()
    build_kfi()
    copy_dashboard()

    print("[OK] deliverables/ built")
    for sub in ("audit_board", "npbo", "moef", "moi", "kfi"):
        d = DEL / sub
        if d.exists():
            files = sorted(d.iterdir())
            print(f"  {sub}/  ({len(files)} files)")
            for f in files:
                kb = f.stat().st_size / 1024
                print(f"    {f.name:40s} {kb:8.1f} KB")


if __name__ == "__main__":
    main()
