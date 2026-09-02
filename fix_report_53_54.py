import re
import shutil
from pathlib import Path

import pandas as pd


REPORT_CANDIDATES = ["REPORT.md", "report.md"]
SEASONAL_INDEX_FILE = Path(r"output\seasonality\seasonal_index_overall_2018_2025.csv")

MONTH_CANDIDATES = ["month", "Month", "월", "mon", "MONTH"]

LODGING_KEYWORDS = ["숙박", "lodging", "accommodation", "hotel", "stay"]
FOOD_KEYWORDS = ["식음료", "음식", "식당", "restaurant", "food", "beverage", "dining", "fnb"]


def find_report():
    for name in REPORT_CANDIDATES:
        p = Path(name)
        if p.exists():
            return p
    raise FileNotFoundError("REPORT.md 파일을 찾지 못했습니다.")


def read_csv_flexible(path):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_error = e
    raise last_error


def normalize_text(s):
    return str(s).strip().lower().replace(" ", "").replace("_", "")


def find_month_col(df):
    for c in df.columns:
        if str(c).strip() in MONTH_CANDIDATES:
            return c

    for c in df.columns:
        vals = pd.to_numeric(df[c], errors="coerce")
        if vals.notna().sum() >= 12:
            uniq = sorted(set(vals.dropna().astype(int).tolist()))
            if all(1 <= v <= 12 for v in uniq):
                return c

    raise ValueError(f"월 컬럼을 찾지 못했습니다. columns={list(df.columns)}")


def find_value_col(df, keywords):
    cols = list(df.columns)
    scored = []

    for c in cols:
        c_norm = normalize_text(c)
        score = 0
        for kw in keywords:
            if normalize_text(kw) in c_norm:
                score += 1
        if score > 0:
            scored.append((score, c))

    if scored:
        scored.sort(key=lambda x: (-x[0], len(str(x[1]))))
        return scored[0][1]

    raise ValueError(f"대상 컬럼을 찾지 못했습니다. columns={list(df.columns)}")


def normalize_month(v):
    try:
        return f"{int(float(v))}월"
    except Exception:
        return str(v)


def build_section(section_title, df, value_col):
    month_col = find_month_col(df)

    work = df[[month_col, value_col]].copy()
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna(subset=[value_col]).copy()

    peak = work.loc[work[value_col].idxmax()]
    trough = work.loc[work[value_col].idxmin()]

    peak_month = normalize_month(peak[month_col])
    trough_month = normalize_month(trough[month_col])
    peak_value = float(peak[value_col])
    trough_value = float(trough[value_col])
    amplitude = peak_value - trough_value

    if "숙박" in section_title:
        analysis = (
            f"숙박업소비는 **{peak_month}**에 계절지수가 가장 높고 "
            f"**{trough_month}**에 가장 낮게 나타났다. "
            f"최고 지수는 **{peak_value:.2f}**, 최저 지수는 **{trough_value:.2f}**이며, "
            f"변동 폭은 **{amplitude:.2f}**이다. "
            f"이는 숙박 소비가 특정 성수기에 집중되는 계절성이 비교적 뚜렷함을 보여준다."
        )
    else:
        analysis = (
            f"식음료업소비는 **{peak_month}**에 계절지수가 가장 높고 "
            f"**{trough_month}**에 가장 낮게 나타났다. "
            f"최고 지수는 **{peak_value:.2f}**, 최저 지수는 **{trough_value:.2f}**이며, "
            f"변동 폭은 **{amplitude:.2f}**이다. "
            f"이는 식음료 소비 역시 계절적 영향을 받지만, 숙박업소비와 비교해 변동성의 크기를 함께 해석할 필요가 있음을 시사한다."
        )

    return f"""### {section_title}

| 항목 | 값 |
|---|---:|
| 계절성 최고 월 | {peak_month} |
| 최고 계절지수 | {peak_value:.2f} |
| 계절성 최저 월 | {trough_month} |
| 최저 계절지수 | {trough_value:.2f} |
| 변동 폭 | {amplitude:.2f} |

{analysis}
"""


def replace_section(text, section_number, new_block):
    pattern = rf'^##{{1,6}}\s*{re.escape(section_number)}[^\n]*\n.*?(?=^##{{1,6}}\s*\d+(?:\.\d+)*\b|\Z)'
    m = re.search(pattern, text, flags=re.M | re.S)
    if not m:
        raise ValueError(f"{section_number} 섹션을 REPORT.md에서 찾지 못했습니다.")
    return text[:m.start()] + new_block.strip() + "\n\n" + text[m.end():]


def main():
    report_path = find_report()

    if not SEASONAL_INDEX_FILE.exists():
        raise FileNotFoundError(f"계절지수 파일을 찾지 못했습니다: {SEASONAL_INDEX_FILE}")

    df = read_csv_flexible(SEASONAL_INDEX_FILE)

    print("[사용 파일]")
    print(SEASONAL_INDEX_FILE)
    print("\n[컬럼 목록]")
    for c in df.columns:
        print("-", c)

    lodging_col = find_value_col(df, LODGING_KEYWORDS)
    food_col = find_value_col(df, FOOD_KEYWORDS)

    print(f"\n[선택된 숙박 컬럼] {lodging_col}")
    print(f"[선택된 식음료 컬럼] {food_col}")

    section_53 = build_section("5.3 숙박업소비 계절성 분석", df, lodging_col)
    section_54 = build_section("5.4 식음료업소비 계절성 분석", df, food_col)

    original = report_path.read_text(encoding="utf-8")
    backup_path = report_path.with_suffix(".backup.md")
    shutil.copy(report_path, backup_path)

    updated = original
    updated = replace_section(updated, "5.3", section_53)
    updated = replace_section(updated, "5.4", section_54)

    report_path.write_text(updated, encoding="utf-8")

    print(f"\n[백업 완료] {backup_path}")
    print("[복구 완료] REPORT.md의 5.3 / 5.4를 갱신했습니다.\n")

    print("----- 5.3 미리보기 -----")
    print(section_53)
    print("----- 5.4 미리보기 -----")
    print(section_54)


if __name__ == "__main__":
    main()