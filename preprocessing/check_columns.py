from data_loader import DataLoader

loader = DataLoader()
years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']

print("=" * 60)
print("전체 연도 로드 테스트 시작")
print("=" * 60)

results = {}  # 결과 저장용

for year in years:
    try:
        df = loader.load_region_visitor(year)   # ← 이렇게 수정!   # ← 메서드명은 실제 것에 맞추세요
        results[year] = df
        print(f"✅ {year}년 | 행: {df.shape[0]:>4} | 열: {df.shape[1]} | 컬럼: {list(df.columns)[:2]}...")
    except Exception as e:
        print(f"❌ {year}년 실패 | 에러: {e}")

print("=" * 60)
print(f"성공: {len(results)}/{len(years)}개 연도")
print("=" * 60)