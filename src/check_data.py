import pandas as pd

print("=" * 70)
print("📊 데이터 구조 확인")
print("=" * 70)

# 1. 월별 추이
print("\n[1/3] 01_trend_monthly.csv")
print("-" * 70)
df1 = pd.read_csv('data/processed/01_trend_monthly.csv')
print(f"✅ 형태: {df1.shape} (행, 열)")
print(f"✅ 열 이름: {list(df1.columns)}")
print(f"✅ 데이터 타입:\n{df1.dtypes}")
print("\n📋 처음 5행:")
print(df1.head())
print("\n📊 통계:")
print(df1.describe())

# 2. 광역별
print("\n" + "=" * 70)
print("[2/3] 02_regional_wide.csv")
print("-" * 70)
df2 = pd.read_csv('data/processed/02_regional_wide.csv')
print(f"✅ 형태: {df2.shape} (행, 열)")
print(f"✅ 열 이름: {list(df2.columns)}")
print(f"✅ 데이터 타입:\n{df2.dtypes}")
print("\n📋 처음 5행:")
print(df2.head())
print("\n📊 통계:")
print(df2.describe())

# 3. 기초별
print("\n" + "=" * 70)
print("[3/3] 03_regional_basic.csv")
print("-" * 70)
df3 = pd.read_csv('data/processed/03_regional_basic.csv')
print(f"✅ 형태: {df3.shape} (행, 열)")
print(f"✅ 열 이름: {list(df3.columns)}")
print(f"✅ 데이터 타입:\n{df3.dtypes}")
print("\n📋 처음 5행:")
print(df3.head())
print("\n📊 통계:")
print(df3.describe())

# 4. 결측치 확인
print("\n" + "=" * 70)
print("🔍 결측치(NaN) 확인")
print("-" * 70)
print(f"01_trend_monthly.csv: {df1.isnull().sum().sum()} 개")
print(f"02_regional_wide.csv: {df2.isnull().sum().sum()} 개")
print(f"03_regional_basic.csv: {df3.isnull().sum().sum()} 개")

print("\n" + "=" * 70)
print("✅ 데이터 구조 확인 완료!")
print("=" * 70)