import os
from pathlib import Path
import glob
import pandas as pd

class DataLoader:
    def __init__(self):
    # 이 파일(data_loader.py) 기준으로 프로젝트 루트를 찾음
        project_root = Path(__file__).resolve().parent.parent
        self.raw_path = project_root / 'data' / 'raw'
        self.years = ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
    # 내부 유틸: 패턴으로 파일 찾고 읽어서 concat 해서 반환
    def _find_and_read(self, pattern, encodings=("cp949", "utf-8-sig", "utf-8")):
        """
        glob 패턴으로 파일들을 찾고, 각 파일을 시도 가능한 인코딩으로 읽어 합쳐서 반환합니다.
        파일이 없으면 FileNotFoundError를 발생시킵니다.
        """
        files = sorted(glob.glob(pattern))
        if not files:
            raise FileNotFoundError(f"No files found for pattern: {pattern}")

        dfs = []
        for f in files:
            last_exc = None
            for enc in encodings:
                try:
                    df = pd.read_csv(f, encoding=enc)
                    dfs.append(df)
                    break
                except Exception as e:
                    last_exc = e
            else:
                # 모든 인코딩 시도 실패
                raise RuntimeError(f"Failed to read file {f}: {last_exc}")

        # 여러 파일이면 concat, 아니면 단일 df 반환
        if len(dfs) == 1:
            return dfs[0]
        return pd.concat(dfs, ignore_index=True)

    # ==================== 방문자 추이 ====================
    def load_visitor_trend(self, year='2018'):
        """방문자 추이 데이터 로드 (월별 데이터)"""
        try:
            # '방문자'와 '추이' 키워드 중심으로 유연하게 검색
            pattern = str(self.raw_path / f'{year}*방문자*추이*.csv')
            df = self._find_and_read(pattern)
            print(f"✅ {year}년 방문자추이 로드 성공: (파일 {len(glob.glob(pattern))}개)")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   첫 3행:\n{df.head(3)}\n")
            return df
        except FileNotFoundError:
            print(f"❌ {year}년 방문자 파일을 찾을 수 없습니다!")
            print(f"   패턴: {year}*방문자*추이*.csv")
            return None
        except Exception as e:
            print(f"❌ {year}년 방문자추이 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ==================== 지역별 방문자 ====================
    def load_region_visitor(self, year='2018'):
        """지역별 방문자 데이터 로드 (기초자치체별)"""
        try:
            # '지역' '방문자' '기초' 같은 키워드 중심으로 유연 검색
            pattern = str(self.raw_path / f'{year}*지역*방문자*기초*.csv')
            df = self._find_and_read(pattern)
            print(f"✅ {year}년 지역별방문자 로드 성공: (파일 {len(glob.glob(pattern))}개)")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   첫 3행:\n{df.head(3)}\n")
            return df
        except FileNotFoundError:
            print(f"❌ {year}년 지역별방문자 파일을 찾을 수 없습니다!")
            print(f"   패턴: {year}*지역*방문자*기초*.csv")
            return None
        except Exception as e:
            print(f"❌ {year}년 지역별방문자 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ==================== 관광 소비 ====================
    def load_tourism_spending(self, year='2018'):
        """관광 소비 데이터 로드 (월별 데이터)"""
        try:
            pattern = str(self.raw_path / f'{year}*관광소비*추이*.csv')
            df = self._find_and_read(pattern)
            print(f"✅ {year}년 관광소비 로드 성공: (파일 {len(glob.glob(pattern))}개)")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   첫 3행:\n{df.head(3)}\n")
            return df
        except FileNotFoundError:
            print(f"❌ {year}년 관광소비 파일을 찾을 수 없습니다!")
            print(f"   패턴: {year}*관광소비*추이*.csv")
            return None
        except Exception as e:
            print(f"❌ {year}년 관광소비 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ==================== 업종별 지출액 ====================
    def load_industry_spending(self, year='2018'):
        """업종별 지출액 데이터 로드"""
        try:
            pattern = str(self.raw_path / f'{year}*업종별*지출액*.csv')
            df = self._find_and_read(pattern)
            print(f"✅ {year}년 업종별지출 로드 성공: (파일 {len(glob.glob(pattern))}개)")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")
            print(f"   첫 3행:\n{df.head(3)}\n")
            return df
        except FileNotFoundError:
            print(f"❌ {year}년 업종별지출 파일을 찾을 수 없습니다!")
            print(f"   패턴: {year}*업종별*지출액*.csv")
            return None
        except Exception as e:
            print(f"❌ {year}년 업종별지출 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    # ==================== 전체 데이터 로드 ====================
    def load_all_years(self):
        """모든 연도의 모든 데이터 로드"""
        all_data = {}
        for year in self.years:
            print(f"\n{'='*60}")
            print(f"📅 {year}년 데이터 로드 중...")
            print(f"{'='*60}\n")
            all_data[year] = {
                'visitor_trend': self.load_visitor_trend(year),
                'region_visitor': self.load_region_visitor(year),
                'tourism_spending': self.load_tourism_spending(year),
                'industry_spending': self.load_industry_spending(year)
            }
        return all_data

    # ==================== 파일 목록 확인 ====================
    def list_raw_files(self):
        """data/raw 폴더의 모든 파일 목록 출력"""
        print("\n📂 data/raw 폴더의 모든 파일:")
        print("="*60)

        if not self.raw_path.exists():
            print(f"❌ {self.raw_path} 폴더가 없습니다!")
            return

        files = sorted(self.raw_path.glob('*.csv'))

        if not files:
            print("❌ CSV 파일이 없습니다!")
            return

        for i, file in enumerate(files, 1):
            size = file.stat().st_size / 1024  # KB 단위
            print(f"{i:2d}. {file.name} ({size:.1f} KB)")

        print(f"\n총 {len(files)}개 파일\n")


# ==================== 테스트 코드 (직접 실행 시) ====================
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Raw 데이터 로드 테스트")
    print("="*60 + "\n")

    loader = DataLoader()

    # 1️⃣ 파일 목록 확인
    loader.list_raw_files()

    # 2️⃣ 2018년 데이터만 로드 테스트
    print("\n" + "="*60)
    print("📊 2018년 데이터 로드 테스트")
    print("="*60 + "\n")

    visitor_trend = loader.load_visitor_trend('2018')
    region_visitor = loader.load_region_visitor('2018')
    tourism_spending = loader.load_tourism_spending('2018')
    industry_spending = loader.load_industry_spending('2018')

    # 3️⃣ 데이터 검증
    print("\n" + "="*60)
    print("✅ 데이터 검증")
    print("="*60 + "\n")

    if visitor_trend is not None:
        print(f"✓ 방문자추이: {visitor_trend.shape}")
    else:
        print(f"✗ 방문자추이: 로드 실패")

    if region_visitor is not None:
        print(f"✓ 지역별방문자: {region_visitor.shape}")
    else:
        print(f"✗ 지역별방문자: 로드 실패")

    if tourism_spending is not None:
        print(f"✓ 관광소비: {tourism_spending.shape}")
    else:
        print(f"✗ 관광소비: 로드 실패")

    if industry_spending is not None:
        print(f"✓ 업종별지출: {industry_spending.shape}")
    else:
        print(f"✗ 업종별지출: 로드 실패")

    print("\n" + "="*60)
    print("✨ 테스트 완료!")
    print("="*60 + "\n")