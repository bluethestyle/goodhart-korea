"""
H29: 극단 게임화 활동 TOP 50 산출

산출물:
  - data/results/extreme_50_activities.parquet  (정본, dtype 보존)
  - deliverables/audit_board/extreme_50_activities.csv  (감사원 핸드오프용)

알고리즘:
  exposure_score = amp_12m_norm * dec_pct
    · amp_12m_norm: FFT 12개월 진폭 (게임화 강도)
    · dec_pct: 12월 집행 비중 (회계연도 마감 쏠림)
    · 둘 다 큰 활동이 *측정 압력 반응성 + 12월 RDD 점프* 동시 충족
  Filter: dec_pct >= 0.25 (12월이 평균 8.33%의 3배 이상)
  Sort: exposure_score DESC, take TOP 50
"""
from pathlib import Path
import pandas as pd
import duckdb

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "results" / "H3_activity_embedding_11y.csv"
OUT_PARQUET = ROOT / "data" / "results" / "extreme_50_activities.parquet"
OUT_CSV = ROOT / "deliverables" / "audit_board" / "extreme_50_activities.csv"

ARCHETYPE = {
    0: "인건비형",
    1: "자산취득형",
    2: "출연금형",
    3: "정상사업",
}

DEC_FLAT = 1 / 12
DEC_THRESHOLD = DEC_FLAT * 3


def main() -> None:
    df = pd.read_csv(SRC)

    df["archetype"] = df["cluster"].map(ARCHETYPE)
    df["dec_jump_ratio"] = df["dec_pct"] / DEC_FLAT
    df["exposure_score"] = df["amp_12m_norm"] * df["dec_pct"]

    qualified = df[df["dec_pct"] >= DEC_THRESHOLD].copy()
    top50 = qualified.nlargest(50, "exposure_score").reset_index(drop=True)
    top50.insert(0, "rank", top50.index + 1)

    cols = [
        "rank",
        "FLD_NM",
        "OFFC_NM",
        "PGM_NM",
        "ACTV_NM",
        "archetype",
        "exposure_score",
        "amp_12m_norm",
        "dec_pct",
        "dec_jump_ratio",
        "chooyeon_pct",
        "direct_invest_pct",
        "personnel_pct",
        "total_budget",
        "year_n",
    ]
    out = top50[cols].rename(columns={
        "FLD_NM": "field",
        "OFFC_NM": "ministry",
        "PGM_NM": "program",
        "ACTV_NM": "activity",
    })

    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    out.to_parquet(OUT_PARQUET, index=False, compression="snappy")
    out.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")

    con = duckdb.connect(":memory:")
    verify = con.execute(
        f"SELECT COUNT(*) AS n, MIN(rank) AS min_r, MAX(rank) AS max_r "
        f"FROM read_parquet('{OUT_PARQUET.as_posix()}')"
    ).fetchone()
    assert verify == (50, 1, 50), f"verify failed: {verify}"

    parquet_kb = OUT_PARQUET.stat().st_size / 1024
    csv_kb = OUT_CSV.stat().st_size / 1024
    print(f"[OK] {len(out)} rows")
    print(f"  parquet: {OUT_PARQUET.relative_to(ROOT)} ({parquet_kb:.1f} KB)")
    print(f"  csv    : {OUT_CSV.relative_to(ROOT)} ({csv_kb:.1f} KB)")
    print(f"  compression ratio: {csv_kb/parquet_kb:.2f}x smaller as parquet")
    print()
    print("archetype distribution in TOP 50:")
    print(out["archetype"].value_counts().to_string())
    print()
    print("field distribution (top 8):")
    print(out["field"].value_counts().head(8).to_string())
    print()
    print("TOP 5 preview:")
    preview_cols = ["rank", "ministry", "activity", "archetype",
                    "exposure_score", "dec_jump_ratio"]
    print(out[preview_cols].head().to_string(index=False))


if __name__ == "__main__":
    main()
