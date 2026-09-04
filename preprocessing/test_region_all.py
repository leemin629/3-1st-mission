from data_loader import DataLoader

loader = DataLoader()

print("=" * 60)
print("전체 연도 지역별 방문자 로드 테스트")
print("=" * 60)

results = {}   # 성공한 데이터 저장

for year in loader.years:          # self.years 재사용 (2018~2025)
    df = loader.load_region_visitor(year)
    if df is not None:
        results[year] = df

# ===== 요약 =====
print("\n" + "=" * 60)
print("📊 최종 요약")
print("=" * 60)
for year in loader.years:
    if year in results:
        print(f"✅ {year}년 | {results[year].shape}")
    else:
        print(f"❌ {year}년 | 로드 실패")

print(f"\n성공: {len(results)}/{len(loader.years)}개 연도")