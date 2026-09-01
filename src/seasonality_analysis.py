from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# 0. 한글 폰트 설정 (Windows)
# -----------------------------
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

# -----------------------------
# 1. 경로 및 변수 설정
# -----------------------------
INPUT_PATH = Path("data/processed/monthly_tourism_variables.csv")
OUTPUT_DIR = Path("output/seasonality")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 분석 변수: 메인 4개 + 보조 1개
VARS = [
    "전체방문자수",
    "관광총소비_천원",
    "숙박업소비_천원",
    "식음료업소비_천원",
    "쇼핑소비_천원"
]

# 그래프용 라벨
VAR_LABELS = {
    "전체방문자수": "방문자수",
    "관광총소비_천원": "관광총소비",
    "숙박업소비_천원": "숙박업 소비",
    "식음료업소비_천원": "식음료업 소비",
    "쇼핑소비_천원": "쇼핑 소비"
}

# 기간 구분
PERIODS = {
    "overall_2018_2025": None,
    "pre_covid_2018_2019": ("2018-01-01", "2019-12-31"),
    "covid_2020_2021": ("2020-01-01", "2021-12-31"),
    "recovery_2022_2025": ("2022-01-01", "2025-12-31")
}

PERIOD_TITLES = {
    "overall_2018_2025": "전체기간(2018~2025)",
    "pre_covid_2018_2019": "코로나 이전(2018~2019)",
    "covid_2020_2021": "코로나 영향기(2020~2021)",
    "recovery_2022_2025": "회복기(2022~2025)"
}


# -----------------------------
# 2. 데이터 불러오기 및 전처리
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
# 3. 기간 필터링
# -----------------------------
def subset_period(df: pd.DataFrame, period):
    if period is None:
        return df.copy()

    start, end = period
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)

    return df[(df["기준년월"] >= start) & (df["기준년월"] <= end)].copy()


# -----------------------------
# 4. 월평균 계산
# -----------------------------
def calc_monthly_mean(df: pd.DataFrame) -> pd.DataFrame:
    monthly_mean = df.groupby("월")[VARS].mean()
    monthly_mean = monthly_mean.reindex(range(1, 13))
    return monthly_mean


# -----------------------------
# 5. 계절지수 계산
#    계절지수 = (해당 월 평균 / 전체 평균) * 100
# -----------------------------
def calc_seasonal_index(df: pd.DataFrame) -> pd.DataFrame:
    monthly_mean = calc_monthly_mean(df)
    overall_mean = df[VARS].mean()

    seasonal_index = monthly_mean.divide(overall_mean, axis=1) * 100
    seasonal_index = seasonal_index.reindex(range(1, 13))
    return seasonal_index.round(1)


# -----------------------------
# 6. 표 저장
# -----------------------------
def save_tables(df: pd.DataFrame, period_key: str):
    monthly_mean = calc_monthly_mean(df)
    seasonal_index = calc_seasonal_index(df)

    monthly_mean_path = OUTPUT_DIR / f"monthly_mean_{period_key}.csv"
    seasonal_index_path = OUTPUT_DIR / f"seasonal_index_{period_key}.csv"

    monthly_mean.to_csv(monthly_mean_path, encoding="utf-8-sig")
    seasonal_index.to_csv(seasonal_index_path, encoding="utf-8-sig")

    return monthly_mean, seasonal_index, monthly_mean_path, seasonal_index_path


# -----------------------------
# 7. 전체 시계열 추이 그래프
# -----------------------------
def plot_time_series(df: pd.DataFrame):
    fig, axes = plt.subplots(len(VARS), 1, figsize=(14, 16), sharex=True)

    for ax, col in zip(axes, VARS):
        ax.plot(df["기준년월"], df[col], marker="o", linewidth=1.5)
        ax.set_title(f"{VAR_LABELS[col]} 월별 추이")
        ax.set_ylabel(VAR_LABELS[col])
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel("기준년월")
    plt.suptitle("관광 주요 변수 월별 시계열 추이", fontsize=16, y=0.995)
    plt.tight_layout()

    out_path = OUTPUT_DIR / "time_series_main_variables.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    return out_path


# -----------------------------
# 8. 계절지수 그래프
# -----------------------------
def plot_seasonal_index(seasonal_index: pd.DataFrame, title: str, out_path: Path):
    plt.figure(figsize=(12, 6))

    for col in VARS:
        plt.plot(
            seasonal_index.index,
            seasonal_index[col],
            marker="o",
            linewidth=2,
            label=VAR_LABELS[col]
        )

    plt.axhline(100, color="gray", linestyle="--", alpha=0.8)
    plt.xticks(range(1, 13))
    plt.xlabel("월")
    plt.ylabel("계절지수 (전체평균=100)")
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


# -----------------------------
# 9. 기간별 비교 그래프
#    변수 1개씩 period 비교
# -----------------------------
def plot_period_comparison(seasonal_results: dict, col: str):
    plt.figure(figsize=(12, 6))

    for period_key, seasonal_index in seasonal_results.items():
        if col in seasonal_index.columns:
            plt.plot(
                seasonal_index.index,
                seasonal_index[col],
                marker="o",
                linewidth=2,
                label=PERIOD_TITLES[period_key]
            )

    plt.axhline(100, color="gray", linestyle="--", alpha=0.8)
    plt.xticks(range(1, 13))
    plt.xlabel("월")
    plt.ylabel("계절지수 (전체평균=100)")
    plt.title(f"{VAR_LABELS[col]} 기간별 월 계절성 비교")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    out_path = OUTPUT_DIR / f"compare_periods_{col}.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()

    return out_path


# -----------------------------
# 10. 실행
# -----------------------------
def main():
    print("=" * 70)
    print("월별 계절성 분석 시작")
    print("=" * 70)

    df = load_data(INPUT_PATH)

    print(f"[1] 데이터 로드 완료: {INPUT_PATH}")
    print(f"    shape: {df.shape}")
    print(f"    기간: {df['기준년월'].min().strftime('%Y-%m')} ~ {df['기준년월'].max().strftime('%Y-%m')}")

    # 전체 시계열 그래프 저장
    ts_path = plot_time_series(df)
    print(f"[2] 전체 시계열 그래프 저장: {ts_path}")

    seasonal_results = {}

    # 기간별 분석
    for period_key, period_range in PERIODS.items():
        sub = subset_period(df, period_range)

        if sub.empty:
            print(f"[SKIP] {period_key}: 데이터 없음")
            continue

        print(f"\n[3] 분석 중: {PERIOD_TITLES[period_key]}")
        print(f"    기간: {sub['기준년월'].min().strftime('%Y-%m')} ~ {sub['기준년월'].max().strftime('%Y-%m')}")
        print(f"    행 수: {len(sub)}")

        monthly_mean, seasonal_index, mean_path, index_path = save_tables(sub, period_key)

        # 계절지수 그래프 저장
        plot_path = OUTPUT_DIR / f"seasonal_index_{period_key}.png"
        plot_seasonal_index(
            seasonal_index,
            f"월별 계절지수 - {PERIOD_TITLES[period_key]}",
            plot_path
        )

        seasonal_results[period_key] = seasonal_index

        print(f"    - 월평균 저장: {mean_path}")
        print(f"    - 계절지수 저장: {index_path}")
        print(f"    - 그래프 저장 : {plot_path}")

    # 변수별 기간 비교 그래프
    print("\n[4] 변수별 기간 비교 그래프 저장")
    for col in VARS:
        compare_path = plot_period_comparison(seasonal_results, col)
        print(f"    - {VAR_LABELS[col]}: {compare_path}")

    print("\n[5] 분석 완료")
    print("=" * 70)
    print(f"결과 폴더: {OUTPUT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()