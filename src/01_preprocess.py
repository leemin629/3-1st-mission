import pandas as pd
import os
from glob import glob

print("=" * 70)
print("🔄 데이터 정제 시작 (연도 자동 부여)")
print("=" * 70)

def get_file_creation_time(filepath):
    """파일 생성 시간 가져오기"""
    return os.path.getctime(filepath)

def map_year_to_files(files, start_year=2018):
    """파일을 시간순으로 정렬하고 연도 매핑"""
    sorted_files = sorted(files, key=get_file_creation_time)
    
    wide_files = [f for f in sorted_files if '광역별' in f]
    basic_files = [f for f in sorted_files if '기초지자체별' in f]
    
    wide_year_map = {f: start_year + i for i, f in enumerate(wide_files)}
    basic_year_map = {f: start_year + i for i, f in enumerate(basic_files)}
    
    return wide_year_map, basic_year_map

# ============================================================
# 1️⃣ 월별 추이 데이터
# ============================================================
print("\n[1/3] 월별 추이 데이터 처리 중...")
trend_files = sorted(glob('data/raw/*월별*.csv'))

if trend_files:  # ← 파일이 있을 때만 처리
    all_trend = []
    for file in trend_files:
        df = pd.read_csv(file)
        all_trend.append(df)
        print(f"  ✅ {os.path.basename(file)}")
    
    df_trend = pd.concat(all_trend, ignore_index=True)
    df_trend = df_trend.drop_duplicates()
    df_trend = df_trend.sort_values(['기준년월', '광역지자체'])
    df_trend.to_csv('data/processed/01_trend_monthly.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 완료: {df_trend.shape[0]:,}행 저장")
else:
    print("⚠️  월별 파일을 찾을 수 없습니다. (스킵)")

# ============================================================
# 2️⃣ 광역별 데이터
# ============================================================
print("\n[2/3] 광역별 데이터 처리 중...")
all_raw_files = glob('data/raw/*.csv')
wide_year_map, basic_year_map = map_year_to_files(all_raw_files)

all_wide = []
for file in sorted(wide_year_map.keys()):
    year = wide_year_map[file]
    df = pd.read_csv(file)
    df['연도'] = year
    all_wide.append(df)
    print(f"  ✅ {os.path.basename(file)} → {year}년")

if all_wide:
    df_wide = pd.concat(all_wide, ignore_index=True)
    df_wide = df_wide.drop_duplicates()
    df_wide = df_wide.sort_values(['연도', '광역지자체명'])
    df_wide.to_csv('data/processed/02_regional_wide.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 완료: {df_wide.shape[0]:,}행 저장")
    print(f"   연도 범위: {df_wide['연도'].min()} ~ {df_wide['연도'].max()}")

# ============================================================
# 3️⃣ 기초지자체별 데이터
# ============================================================
print("\n[3/3] 기초지자체별 데이터 처리 중...")
all_basic = []

for file in sorted(basic_year_map.keys()):
    year = basic_year_map[file]
    df = pd.read_csv(file)
    df['연도'] = year
    all_basic.append(df)
    print(f"  ✅ {os.path.basename(file)} → {year}년")

if all_basic:
    df_basic = pd.concat(all_basic, ignore_index=True)
    df_basic = df_basic.drop_duplicates()
    df_basic = df_basic.sort_values(['연도', '광역지자체명', '기초지자체명'])
    df_basic.to_csv('data/processed/03_regional_basic.csv', index=False, encoding='utf-8-sig')
    print(f"✅ 완료: {df_basic.shape[0]:,}행 저장")
    print(f"   연도 범위: {df_basic['연도'].min()} ~ {df_basic['연도'].max()}")

# ============================================================
# 📊 최종 확인
# ============================================================
print("\n" + "=" * 70)
print("📊 정제 완료 요약")
print("=" * 70)
if trend_files:
    print(f"01_trend_monthly.csv:    {df_trend.shape[0]:,}행 × {df_trend.shape[1]}열")
print(f"02_regional_wide.csv:    {df_wide.shape[0]:,}행 × {df_wide.shape[1]}열")
print(f"03_regional_basic.csv:   {df_basic.shape[0]:,}행 × {df_basic.shape[1]}열")
print("=" * 70)