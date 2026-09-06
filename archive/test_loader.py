"""테스트용 파일"""
from preprocessing.data_loader import DataLoader

print("=" * 50)
print("🔍 Raw 데이터 로드 테스트")
print("=" * 50)

loader = DataLoader()

try:
    visitor_trend = loader.load_visitor_trend()
    print(f"\n✅ 방문자추이: {visitor_trend.shape}")
    print(visitor_trend.head(2))
except Exception as e:
    print(f"❌ 방문자추이 오류: {e}")

try:
    region_visitor = loader.load_region_visitor()
    print(f"\n✅ 지역별방문자: {region_visitor.shape}")
    print(region_visitor.head(2))
except Exception as e:
    print(f"❌ 지역별방문자 오류: {e}")

print("\n" + "=" * 50)