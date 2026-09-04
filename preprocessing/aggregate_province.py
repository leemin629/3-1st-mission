import pandas as pd
from data_loader import DataLoader


def aggregate_by_province(df):
    """기초 단위 데이터를 광역 단위로 집계"""
    # 광역 관련 컬럼만 선택
    province = df[['광역지자체명', '광역지자체 방문자 수', '광역지자체 방문자 비율']]

    # 광역명 기준 중복 제거
    province = province.drop_duplicates(subset='광역지자체명').reset_index(drop=True)

    # 방문자 수 내림차순 정렬
    province = province.sort_values('광역지자체 방문자 수', ascending=False).reset_index(drop=True)

    # 인덱스를 1부터 시작하도록 변경
    province.index = province.index + 1


    return province


from data_loader import DataLoader  # 파일 맨 위에 추가!

def aggregate_all_years(start=2018, end=2025):
    """모든 연도를 집계해서 하나로 합치기"""
    loader = DataLoader()  # 로더 객체 생성 (한 번만!)
    all_data = []

    for year in range(start, end + 1):
        # 1. 로더로 지역별 방문자 데이터 로드 (year는 문자열로!)
        df = loader.load_region_visitor(str(year))

        # 로드 실패 시 건너뛰기
        if df is None:
            print(f"⚠️ {year}년 데이터 로드 실패, 건너뜀")
            continue

        # 2. 광역 단위로 집계
        province = aggregate_by_province(df)

        # 3. 연도 컬럼 추가
        province['연도'] = year

        all_data.append(province)

    # 4. 전부 세로로 합치기
    result = pd.concat(all_data, ignore_index=True)
    return result

# --- 테스트 실행 ---
if __name__ == "__main__":
    all_result = aggregate_all_years()

    print(f"\n✅ 전체 연도 합치기 완료")
    print(f"Shape: {all_result.shape}")   # (136, 4) 예상: 17광역 × 8년
    print(f"연도 종류: {sorted(all_result['연도'].unique())}")
    print(all_result.head())
    print("...")
    print(all_result.tail())

    # 저장 폴더 경로 (data/processed 폴더)
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
save_dir = project_root / 'data' / 'processed'
save_dir.mkdir(parents=True, exist_ok=True)  # 폴더 없으면 자동 생성

# CSV로 저장
save_path = save_dir / 'province_visitor_all_years.csv'
all_result.to_csv(save_path, index=False, encoding='utf-8-sig')

print(f"\n💾 저장 완료: {save_path}")
print(f"   Shape: {all_result.shape}")