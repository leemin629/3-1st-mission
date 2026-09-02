from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 0. Plot settings
#    NOTE: Use English text in charts due font limitations
# -----------------------------
plt.rcParams["axes.unicode_minus"] = False

# -----------------------------
# 1. Paths and variables
# -----------------------------
INPUT_PATH = Path("data/processed/monthly_tourism_variables.csv")
OUTPUT_DIR = Path("output/seasonality")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Analysis variables
VARS = [
    "전체방문자수",
    "관광총소비_천원",
    "숙박업소비_천원",
    "식음료업소비_천원",
    "쇼핑소비_천원"
]

# English labels for charts
VAR_LABELS = {
    "전체방문자수": "Visitors",
    "관광총소비_천원": "Total tourism spending",
    "숙박업소비_천원": "Accommodation spending",
    "식음료업소비_천원": "Food & beverage spending",
    "쇼핑소비_천원": "Shopping spending"
}

# Period definitions
PERIODS = {
    "overall_2018_2025": None,
    "pre_covid_2018_2019": ("2018-01-01", "2019-12-31"),
    "covid_2020_2021": ("2020-01-01", "2021-12-31"),
    "recovery_2022_2025": ("2022-01-01", "2025-12-31")
}

# Korean titles for console/report use
PERIOD_TITLES_KR = {
    "overall_2018_2025": "전체기간(2018~2025)",
    "pre_covid_2018_2019": "코로나 이전(2018~2019)",
    "covid_2020_2021": "코로나 영향기(2020~2021)",
    "recovery_2022_2025": "회복기(2022~2025)"
}

# English titles for charts
PERIOD_TITLES_EN = {
    "overall_2018_2025": "Overall period (2018-2025)",
    "pre_covid_2018_2019": "Pre-COVID (2018-2019)",
    "covid_2020_2021": "COVID period (2020-2021)",
    "recovery_2022_2025": "Recovery period (2022-2025)"
}


# -----------------------------
# 2. Load and preprocess data
# -----------------------------
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    required_cols = ["기준년월"] + VARS
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise ValueError(f"필수 컬럼이 없습니다: {missing_cols}\n현재 컬럼: {df.columns.tolist()}")

    # 기준년월 → datetime
    df["기준년월"] = pd.to_datetime(df["기준년월"].astype(str).str[:6], format="%Y%m")
    df = df.sort_values("기준년월").reset_index(drop=True)

    # 연도 / 월 분리
    df["연도"] = df["기준년월"].dt.year
    df["월"] = df["기준년월"].dt.month

    return df


# -----------------------------
# 3. Filter by period
# -----------------------------
def subset_period(df: pd.DataFrame, period):
    if period is None:
        return df.copy()

    start, end = period
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    return df[(df["기준년월"] >= start) & (df["기준년월"] <= end)].copy()


# -----------------------------
# 4. Calculate monthly mean
# -----------------------------
def calc_monthly_mean(df: pd.DataFrame) -> pd.DataFrame:
    monthly_mean = df.groupby("월")[VARS].mean()
    monthly_mean = monthly_mean.reindex(range(1, 13))
    return monthly_mean


# -----------------------------
# 5. Calculate monthly relative level
#    A 방식:
#    1) 월별 평균 계산
#    2) 12개월 평균 계산
#    3) 월별 평균 / 12개월 평균 * 100
#
#    Monthly Relative Level = (Monthly Mean / 12-Month Mean) * 100
# -----------------------------
def calc_monthly_relative_level(df: pd.DataFrame) -> pd.DataFrame:
    monthly_mean = calc_monthly_mean(df)
    annual_mean = monthly_mean.mean()   # A 방식의 핵심

    monthly_relative_level = monthly_mean.divide(annual_mean, axis=1) * 100
    monthly_relative_level = monthly_relative_level.reindex(range(1, 13))
    return monthly_relative_level.round(1)


# -----------------------------
# 6. Save tables
# -----------------------------
def save_tables(df: pd.DataFrame, period_key: str):
    monthly_mean = calc_monthly_mean(df)
    monthly_relative_level = calc_monthly_relative_level(df)

    monthly_mean_path = OUTPUT_DIR / f"monthly_mean_{period_key}.csv"
    relative_level_path = OUTPUT_DIR / f"monthly_relative_level_{period_key}.csv"

    monthly_mean.to_csv(monthly_mean_path, encoding="utf-8-sig")
    monthly_relative_level.to_csv(relative_level_path, encoding="utf-8-sig")

    return monthly_mean, monthly_relative_level, monthly_mean_path, relative_level_path


# -----------------------------
# 7. Full time-series plot
# -----------------------------
def plot_time_series(df: pd.DataFrame):
    fig, axes = plt.subplots(len(VARS), 1, figsize=(14, 16), sharex=True)

    for ax, col in zip(axes, VARS):
        ax.plot(df["기준년월"], df[col], marker="o", linewidth=1.5)
        ax.set_title(f"Monthly trend: {VAR_LABELS[col]}")
        ax.set_ylabel(VAR_LABELS[col])
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("Month")
    plt.suptitle("Monthly time-series trends of major tourism variables", fontsize=16, y=0.995)
    plt.tight_layout()

    out_path = OUTPUT_DIR / "time_series_main_variables.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    return out_path


# -----------------------------
# 8. Monthly relative level plot
# -----------------------------
def plot_monthly_relative_level(monthly_relative_level: pd.DataFrame, title: str, out_path: Path):
    plt.figure(figsize=(12, 6))

    for col in VARS:
        plt.plot(
            monthly_relative_level.index,
            monthly_relative_level[col],
            marker="o",
            linewidth=2,
            label=VAR_LABELS[col]
        )

    plt.axhline(100, color="gray", linestyle="--", alpha=0.8)
    plt.xticks(range(1, 13))
    plt.xlabel("Month")
    plt.ylabel("Monthly relative level (12-month average = 100)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# -----------------------------
# 9. Period comparison plot
#    Compare one variable across periods
# -----------------------------
def plot_period_comparison(relative_level_results: dict, col: str):
    plt.figure(figsize=(12, 6))

    for period_key, monthly_relative_level in relative_level_results.items():
        if col in monthly_relative_level.columns:
            plt.plot(
                monthly_relative_level.index,
                monthly_relative_level[col],
                marker="o",
                linewidth=2,
                label=PERIOD_TITLES_EN[period_key]
            )

    plt.axhline(100, color="gray", linestyle="--", alpha=0.8)
    plt.xticks(range(1, 13))
    plt.xlabel("Month")
    plt.ylabel("Monthly relative level (12-month average = 100)")
    plt.title(f"Monthly pattern comparison by period: {VAR_LABELS[col]}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = OUTPUT_DIR / f"compare_periods_{col}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    return out_path


# -----------------------------
# 10. Main execution
# -----------------------------
def main():
    print("=" * 70)
    print("월별 상대수준 기반 연중 변동 패턴 분석 시작")
    print("=" * 70)

    df = load_data(INPUT_PATH)

    print(f"[1] 데이터 로드 완료: {INPUT_PATH}")
    print(f"    shape: {df.shape}")
    print(f"    기간: {df['기준년월'].min().strftime('%Y-%m')} ~ {df['기준년월'].max().strftime('%Y-%m')}")

    # Save full time-series plot
    ts_path = plot_time_series(df)
    print(f"[2] 전체 시계열 그래프 저장: {ts_path}")

    relative_level_results = {}

    # Period analysis
    for period_key, period_range in PERIODS.items():
        sub = subset_period(df, period_range)

        if sub.empty:
            print(f"[SKIP] {period_key}: 데이터 없음")
            continue

        print(f"\n[3] 분석 중: {PERIOD_TITLES_KR[period_key]}")
        print(f"    기간: {sub['기준년월'].min().strftime('%Y-%m')} ~ {sub['기준년월'].max().strftime('%Y-%m')}")
        print(f"    행 수: {len(sub)}")

        monthly_mean, monthly_relative_level, mean_path, relative_level_path = save_tables(sub, period_key)

        # Save monthly relative level plot
        plot_path = OUTPUT_DIR / f"monthly_relative_level_{period_key}.png"
        plot_monthly_relative_level(
            monthly_relative_level,
            f"Monthly relative level - {PERIOD_TITLES_EN[period_key]}",
            plot_path
        )

        relative_level_results[period_key] = monthly_relative_level

        print(f"    - 월평균 저장: {mean_path}")
        print(f"    - 월별 상대수준 저장: {relative_level_path}")
        print(f"    - 그래프 저장: {plot_path}")

    # Period comparison plots by variable
    print("\n[4] 변수별 기간 비교 그래프 저장")
    for col in VARS:
        compare_path = plot_period_comparison(relative_level_results, col)
        print(f"    - {VAR_LABELS[col]}: {compare_path}")

    print("\n[5] 분석 완료")
    print("=" * 70)
    print(f"결과 폴더: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()