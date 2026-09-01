import pandas as pd

files = {
    "코로나 이전": "output/seasonality/seasonal_index_pre_covid_2018_2019.csv",
    "코로나 영향기": "output/seasonality/seasonal_index_covid_2020_2021.csv",
    "회복기": "output/seasonality/seasonal_index_recovery_2022_2025.csv"
}

target_vars = ["전체방문자수", "관광총소비_천원", "쇼핑소비_천원"]

for period, path in files.items():
    df = pd.read_csv(path)

    # 월 컬럼 찾기
    month_col = None
    for c in df.columns:
        if "month" in c.lower() or "월" in c:
            month_col = c
            break
    if month_col is None:
        month_col = df.columns[0]

    print(f"\n[{period}]")

    for var in target_vars:
        s = df[[month_col, var]].copy()
        s = s.sort_values(var, ascending=False).reset_index(drop=True)

        top1_month = s.loc[0, month_col]
        top1_val = s.loc[0, var]

        top2_month = s.loc[1, month_col]
        top2_val = s.loc[1, var]

        bottom = df[[month_col, var]].sort_values(var, ascending=True).reset_index(drop=True)
        low_month = bottom.loc[0, month_col]
        low_val = bottom.loc[0, var]

        amp = round(top1_val - low_val, 1)

        print(f"{var}: 최고월={top1_month}({top1_val:.1f}), 차상위월={top2_month}({top2_val:.1f}), 최저월={low_month}({low_val:.1f}), 변동폭={amp}")