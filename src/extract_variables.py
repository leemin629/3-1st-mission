# src/extract_variables.py

import pandas as pd
from pathlib import Path

# ── 경로 설정 ──────────────────────────────────────────
RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── 중분류 필터 정의 ───────────────────────────────────
ACCOMMODATION = ["호텔", "캠핑장/펜션", "기타숙박", "콘도"]
FOOD          = ["일반외식업", "제과음료업"]
SHOPPING      = ["기타관광쇼핑", "대형쇼핑몰", "레저용품쇼핑", "면세점"]

# ── 파일명 패턴 정의 ───────────────────────────────────
SPENDING_PATTERN = "_관광소비 추이.csv"
VISITOR_PATTERN  = "_방문자 수 추이.csv"

# ── 결과 저장용 리스트 ─────────────────────────────────
all_records = []

# ── 연도별 파일 순회 ───────────────────────────────────
years = range(2018, 2026)  # 2018 ~ 2025

for year in years:
    prefix = f"{year}01-{year}12"

    spending_file = RAW_DIR / f"{prefix}{SPENDING_PATTERN}"
    visitor_file  = RAW_DIR / f"{prefix}{VISITOR_PATTERN}"

    # 파일 존재 확인
    if not spending_file.exists():
        print(f"[SKIP] 없음: {spending_file.name}")
        continue
    if not visitor_file.exists():
        print(f"[SKIP] 없음: {visitor_file.name}")
        continue

    print(f"[PROCESS] {year}년...")

    # ── 관광소비 추이 로드 ─────────────────────────────
    df_sp = pd.read_csv(spending_file, encoding="utf-8-sig")
    df_sp.columns = df_sp.columns.str.strip()

    # 전국 데이터만 사용
    df_sp = df_sp[df_sp["광역지자체"] == "전국"].copy()
    df_sp["기준년월"] = df_sp["기준년월"].astype(str)

    # 관광총소비
    total = (
        df_sp[df_sp["중분류"] == "관광총소비"]
        .groupby("기준년월")["지출액(천원)"]
        .sum()
        .rename("관광총소비_천원")
    )

    # 숙박업 소비
    accom = (
        df_sp[df_sp["중분류"].isin(ACCOMMODATION)]
        .groupby("기준년월")["지출액(천원)"]
        .sum()
        .rename("숙박업소비_천원")
    )

    # 식음료업 소비
    food = (
        df_sp[df_sp["중분류"].isin(FOOD)]
        .groupby("기준년월")["지출액(천원)"]
        .sum()
        .rename("식음료업소비_천원")
    )

    # 쇼핑 소비 (보조)
    shop = (
        df_sp[df_sp["중분류"].isin(SHOPPING)]
        .groupby("기준년월")["지출액(천원)"]
        .sum()
        .rename("쇼핑소비_천원")
    )

    # ── 방문자 수 추이 로드 ────────────────────────────
    df_vi = pd.read_csv(visitor_file, encoding="utf-8-sig")
    df_vi.columns = df_vi.columns.str.strip()

    df_vi = df_vi[df_vi["광역지자체"] == "전국"].copy()
    df_vi["기준년월"] = df_vi["기준년월"].astype(str)

    # 전체방문자만 추출
    visitor = (
        df_vi[df_vi["방문자 구분"] == "전체방문자(a+b)"]
        .groupby("기준년월")["방문자 수"]
        .sum()
        .rename("전체방문자수")
    )

    # ── 월별로 합치기 ──────────────────────────────────
    df_year = pd.concat([visitor, total, accom, food, shop], axis=1)
    df_year = df_year.reset_index()  # 기준년월을 컬럼으로

    all_records.append(df_year)
    print(f"  → {len(df_year)}개월 추출 완료")

# ── 전체 연도 합치기 ───────────────────────────────────
df_final = pd.concat(all_records, ignore_index=True)
df_final = df_final.sort_values("기준년월").reset_index(drop=True)

# ── 파생 컬럼 추가 ─────────────────────────────────────
df_final["연도"] = df_final["기준년월"].str[:4].astype(int)
df_final["월"]   = df_final["기준년월"].str[4:].astype(int)

# ── 저장 ───────────────────────────────────────────────
out_path = OUT_DIR / "monthly_tourism_variables.csv"
df_final.to_csv(out_path, index=False, encoding="utf-8-sig")

print("\n" + "="*60)
print("추출 완료!")
print(f"shape: {df_final.shape}")
print(f"기간: {df_final['기준년월'].min()} ~ {df_final['기준년월'].max()}")
print(f"저장: {out_path}")
print("="*60)
print(df_final.head(3).to_string())