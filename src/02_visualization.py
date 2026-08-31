import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
import platform

# ===== 한글 폰트 설정 =====
if platform.system() == 'Windows':
    # 윈도우: 맑은 고딕
    rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    # 맥: 애플고딕
    rc('font', family='AppleGothic')
else:
    # 리눅스: 나눔고딕
    rc('font', family='NanumGothic')

# 마이너스(-) 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False
# ==========================
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 데이터 로드
print("=" * 70)
print("📊 데이터 로드 중...")
print("=" * 70)

df_wide = pd.read_csv('data/processed/02_regional_wide.csv')
df_basic = pd.read_csv('data/processed/03_regional_basic.csv')

print(f"✅ 광역별 데이터: {df_wide.shape}")
print(f"✅ 기초별 데이터: {df_basic.shape}")

# ============================================================
# 1️⃣ 히트맵: 연도별 광역지자체 방문자 수
# ============================================================
print("\n[1/4] 히트맵 생성 중...")

# 피벗 테이블 생성
heatmap_data = df_wide.pivot(index='광역지자체명', columns='연도', values='광역지자체 방문자 수')

# 백만 단위로 변환
heatmap_data = heatmap_data / 1_000_000

fig, ax = plt.subplots(figsize=(14, 10))
sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', 
            cbar_kws={'label': 'Visitors (Million)'}, ax=ax)
ax.set_title('Regional Visitor Trends by Year (2018-2025)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Region', fontsize=12)
plt.tight_layout()
plt.savefig('output/01_heatmap_regional_trend.png', dpi=300, bbox_inches='tight')
print("✅ Saved: output/01_heatmap_regional_trend.png")
plt.close()

# ============================================================
# 2️⃣ 라인 그래프: 시도별 연도별 방문자 수 변화
# ============================================================
print("\n[2/4] Line graph creating...")

fig, ax = plt.subplots(figsize=(16, 8))

# 상위 5개 지역만 표시 (가독성)
top_regions = df_wide.groupby('광역지자체명')['광역지자체 방문자 수'].mean().nlargest(5).index

for region in top_regions:
    data = df_wide[df_wide['광역지자체명'] == region].sort_values('연도')
    ax.plot(data['연도'], data['광역지자체 방문자 수'] / 1_000_000, 
            marker='o', linewidth=2.5, markersize=8, label=region)

ax.set_title('Top 5 Regions - Visitor Trends by Year', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Visitors (Million)', fontsize=12)
ax.legend(fontsize=11, loc='best')
ax.grid(True, alpha=0.3)
ax.set_xticks(range(2018, 2026))
plt.tight_layout()
plt.savefig('output/02_line_top5_regions.png', dpi=300, bbox_inches='tight')
print("✅ Saved: output/02_line_top5_regions.png")
plt.close()

# ============================================================
# 3️⃣ 막대 그래프: 2025년 기초지자체별 상위 10개
# ============================================================
print("\n[3/4] Bar chart creating...")

df_2025 = df_basic[df_basic['연도'] == 2025].nlargest(10, '기초지자체 방문자 수')

fig, ax = plt.subplots(figsize=(14, 8))
bars = ax.barh(df_2025['기초지자체명'], df_2025['기초지자체 방문자 수'] / 1_000_000, color='steelblue')

# 값 표시
for i, (idx, row) in enumerate(df_2025.iterrows()):
    ax.text(row['기초지자체 방문자 수'] / 1_000_000 + 1, i, 
            f"{row['기초지자체 방문자 수'] / 1_000_000:.1f}M", 
            va='center', fontsize=10)

ax.set_title('Top 10 Basic Municipalities by Visitors (2025)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Visitors (Million)', fontsize=12)
ax.set_ylabel('Municipality', fontsize=12)
plt.tight_layout()
plt.savefig('output/03_bar_top10_basic_2025.png', dpi=300, bbox_inches='tight')
print("✅ Saved: output/03_bar_top10_basic_2025.png")
plt.close()

# ============================================================
# 4️⃣ 박스플롯: 연도별 방문자 수 분포
# ============================================================
print("\n[4/4] Boxplot creating...")

fig, ax = plt.subplots(figsize=(14, 8))
sns.boxplot(data=df_wide, x='연도', y='광역지자체 방문자 수', ax=ax, palette='Set2')

ax.set_title('Distribution of Visitors by Year', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('Visitors', fontsize=12)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.0f}M'))
plt.tight_layout()
plt.savefig('output/04_boxplot_distribution.png', dpi=300, bbox_inches='tight')
print("✅ Saved: output/04_boxplot_distribution.png")
plt.close()

# ============================================================
# 📊 최종 요약
# ============================================================
print("\n" + "=" * 70)
print("✅ Visualization Complete!")
print("=" * 70)
print("\nGenerated files:")
print("  1️⃣  01_heatmap_regional_trend.png")
print("  2️⃣  02_line_top5_regions.png")
print("  3️⃣  03_bar_top10_basic_2025.png")
print("  4️⃣  04_boxplot_distribution.png")
print("\n📁 Check output folder!")
print("=" * 70)