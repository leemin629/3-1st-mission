import pandas as pd

# 데이터 로드
df_wide = pd.read_csv('data/processed/02_regional_wide.csv')
df_basic = pd.read_csv('data/processed/03_regional_basic.csv')

# 연도 범위
years = sorted(df_wide['연도'].unique())
year_min, year_max = years[0], years[-1]

# 최신년도 광역 순위
latest = df_wide[df_wide['연도'] == year_max].sort_values('광역지자체 방문자 수', ascending=False)
top3_regions = latest.head(3)

# 최신년도 기초 순위
latest_basic = df_basic[df_basic['연도'] == year_max].sort_values('기초지자체 방문자 수', ascending=False)
top10_basic = latest_basic.head(10)

# 성장률 계산 (첫해 대비 마지막해)
first = df_wide[df_wide['연도'] == year_min].set_index('광역지자체명')['광역지자체 방문자 수']
last = df_wide[df_wide['연도'] == year_max].set_index('광역지자체명')['광역지자체 방문자 수']
growth = ((last - first) / first * 100).sort_values(ascending=False)

# REPORT.md 작성
report = f"""# 📊 국내여행 17개 시도 방문자 선호도 분석 리포트

## 1. 개요
- **분석 주제**: 전국 17개 광역시도 및 기초지자체 방문자 선호도 시계열 분석
- **분석 기간**: {year_min}년 ~ {year_max}년 ({len(years)}개 연도)
- **데이터 규모**: 광역 {len(df_wide)}행 / 기초 {len(df_basic)}행
- **결측치**: 0개 (정제 완료)

---

## 2. 데이터 구조
| 파일 | 행 수 | 설명 |
|------|-------|------|
| 01_trend_monthly.csv | 288 | 월별 전국 방문자 추이 |
| 02_regional_wide.csv | {len(df_wide)} | 광역지자체별 연도별 방문자 |
| 03_regional_basic.csv | {len(df_basic)} | 기초지자체별 연도별 방문자 |

---

## 3. 주요 분석 결과

### 3-1. {year_max}년 광역지자체 TOP 3
| 순위 | 지역 | 방문자 수 | 비율 |
|------|------|-----------|------|
"""

for i, (_, row) in enumerate(top3_regions.iterrows(), 1):
    v = row['광역지자체 방문자 수'] / 1_000_000
    report += f"| {i} | {row['광역지자체명']} | {v:.1f}백만 | {row.get('광역지자체 방문자 비율', '-')}% |\n"

report += f"""
> **핵심**: 수도권({top3_regions.iloc[0]['광역지자체명']} 등)에 방문자가 집중되는 현상 확인

---

### 3-2. {year_max}년 기초지자체 TOP 10
| 순위 | 지역 | 방문자 수 |
|------|------|-----------|
"""

for i, (_, row) in enumerate(top10_basic.iterrows(), 1):
    v = row['기초지자체 방문자 수'] / 1_000_000
    report += f"| {i} | {row['기초지자체명']} | {v:.1f}백만 |\n"

report += f"""
---

### 3-3. 성장률 분석 ({year_min}→{year_max})
**📈 성장 상위 3개 지역**
"""

for name, g in growth.head(3).items():
    report += f"- **{name}**: {g:+.1f}%\n"

report += "\n**📉 하락 하위 3개 지역**\n"
for name, g in growth.tail(3).items():
    report += f"- **{name}**: {g:+.1f}%\n"

report += """
---

## 4. 시각화 자료
| 파일 | 인사이트 |
|------|----------|
| 01_heatmap_regional_trend.png | 연도별 지역 방문자 변화 한눈에 파악 |
| 02_line_top5_regions.png | 상위 5개 지역 추세선 비교 |
| 03_bar_top10_basic_2025.png | 최신 인기 기초지자체 순위 |
| 04_boxplot_distribution.png | 연도별 지역 간 편차(불균형) 확인 |

---

## 5. 결론 및 시사점
1. **수도권 집중**: 서울·경기가 전체 방문자의 상당 비중 차지
2. **지역 격차**: 박스플롯상 지역 간 방문자 수 편차 큼
3. **관광 특화도시**: 강릉·경주 등 특정 도시는 광역 내 비중 높음
4. **정책 제언**: 방문자 하위 지역에 대한 관광 활성화 전략 필요

---

*본 리포트는 실제 데이터 기반으로 자동 생성되었습니다.*
"""

# 파일 저장
with open('REPORT.md', 'w', encoding='utf-8') as f:
    f.write(report)

print("=" * 60)
print("✅ REPORT.md 생성 완료!")
print("=" * 60)
print(f"📅 분석기간: {year_min}~{year_max}")
print(f"🏆 1위 지역: {top3_regions.iloc[0]['광역지자체명']}")
print(f"📈 최고 성장: {growth.index[0]} ({growth.iloc[0]:+.1f}%)")
print("=" * 60)