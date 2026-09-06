import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
import plotly.express as px

# ============================================
# 탭3용: 지역별 방문자 추이 (선그래프)
# ============================================
def render_regional_visitor_trend():
    df = pd.read_csv("data/processed/02_regional_wide.csv")

    all_regions = sorted(df["광역지자체명"].unique())
    default_regions = ["서울특별시", "경기도", "부산광역시", "인천광역시", "제주특별자치도"]

    # 세션 상태 초기화 (이 탭 전용 키)
    if "region_all" not in st.session_state:
        st.session_state.region_all = False
    if "selected_regions" not in st.session_state:
        st.session_state.selected_regions = default_regions.copy()

    # 전체 선택 토글 동기화 함수
    def sync_region_all():
        if st.session_state.region_all:
            st.session_state.selected_regions = all_regions.copy()
        else:
            st.session_state.selected_regions = []

    # 전체 선택 토글
    st.toggle(
        "전체 선택",
        key="region_all",
        on_change=sync_region_all
    )

    # 지역 pills (토글 ON이면 비활성화)
    st.pills(
        "지역 선택",
        options=all_regions,
        selection_mode="multi",
        key="selected_regions",
        disabled=st.session_state.region_all
    )

    selected = st.session_state.selected_regions

    if not selected:
        st.warning("지역을 하나 이상 선택해주세요.")
        return

    filtered = df[df["광역지자체명"].isin(selected)]

    fig = px.line(
        filtered,
        x="연도",
        y="광역지자체 방문자 수",
        color="광역지자체명",
        markers=True,
        labels={"광역지자체 방문자 수": "방문자 수 (명)", "광역지자체명": "지역"},
        title="지역별 방문자 수 추이 (2018~2025)"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# 탭4용: 전국 관광 소비 추이 (월별)
# ============================================
def render_monthly_consumption_trend():
    df = pd.read_csv("data/processed/monthly_tourism_variables.csv")

    consumption_cols = {
        "관광총소비_천원": "관광 총소비",
        "숙박업소비_천원": "숙박업",
        "식음료업소비_천원": "식음료업",
        "쇼핑소비_천원": "쇼핑"
    }
    all_items = list(consumption_cols.keys())

    # 세션 상태 초기화 (이 탭 전용 키)
    if "consume_all" not in st.session_state:
        st.session_state.consume_all = False
    if "selected_items" not in st.session_state:
        st.session_state.selected_items = ["관광총소비_천원"]

    # 전체 선택 토글 동기화 함수
    def sync_consume_all():
        if st.session_state.consume_all:
            st.session_state.selected_items = all_items.copy()
        else:
            st.session_state.selected_items = []

    # 전체 선택 토글
    st.toggle(
        "전체 선택",
        key="consume_all",
        on_change=sync_consume_all
    )

    # 소비 항목 pills (토글 ON이면 비활성화)
    st.pills(
        "소비 항목 선택",
        options=all_items,
        selection_mode="multi",
        key="selected_items",
        disabled=st.session_state.consume_all,
        format_func=lambda x: consumption_cols[x]
    )

    selected = st.session_state.selected_items

    if not selected:
        st.warning("소비 항목을 하나 이상 선택해주세요.")
        return

    df["기준년월"] = df["기준년월"].astype(str)

    # X축 2줄 라벨 생성: 201801 -> "18<br>01"
    df["기준년월_label"] = df["기준년월"].str[2:4] + "<br>" + df["기준년월"].str[4:6]

    long_df = df.melt(
        id_vars=["기준년월", "기준년월_label"],
        value_vars=selected,
        var_name="항목",
        value_name="소비액"
    )
    long_df["항목"] = long_df["항목"].map(consumption_cols)

    fig = px.line(
        long_df,
        x="기준년월",          # 정렬/순서는 원본 값 기준
        y="소비액",
        color="항목",
        labels={"소비액": "소비액 (천원)", "기준년월": "연월"},
        title="전국 관광 소비 추이 (월별)"
    )

        # 각 연도의 1월(YYYY01)만 눈금으로 사용
    order = sorted(df["기준년월"].unique())
    year_ticks = [v for v in order if v.endswith("01")]   # 201801, 201901 ...

    fig.update_xaxes(
        tickmode="array",
        tickvals=year_ticks,
        ticktext=[v[2:4] for v in year_ticks]   # "18", "19", ... 한 줄로 연도만
    )

    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(
    page_title="전국 관광 데이터 월별 변동 패턴 대시보드",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
/* 탭 묶음 가운데 정렬 - 여러 방식 동시 적용 */
div[data-baseweb="tab-list"],
.stTabs [role="tablist"] {
    justify-content: center !important;
    gap: 30px !important;
}

/* 탭 안 모든 글씨 요소를 다 잡기 */
.stTabs button p,
.stTabs button div,
.stTabs [role="tab"] p,
.stTabs [role="tab"],
button[data-baseweb="tab"] p {
    font-size: 22px !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# 데이터 경로
DATA_PATH = Path(__file__).resolve().parent / "data" / "processed" / "monthly_tourism_variables.csv"

# 실제 데이터 컬럼명 -> 화면 표시명
VAR_LABEL_MAP = {
    "전체방문자수": "전체방문자수",
    "관광총소비_천원": "관광총소비",
    "숙박업소비_천원": "숙박업소비",
    "식음료업소비_천원": "식음료업소비",
    "쇼핑소비_천원": "쇼핑소비",
}

LABEL_TO_VAR = {v: k for k, v in VAR_LABEL_MAP.items()}

MONTH_LABELS = {
    1: "1월", 2: "2월", 3: "3월", 4: "4월",
    5: "5월", 6: "6월", 7: "7월", 8: "8월",
    9: "9월", 10: "10월", 11: "11월", 12: "12월"
}

# -----------------------------
# 스타일
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

div[data-testid="stPills"] button {
    min-height: 42px;
    padding: 0.45rem 0.95rem;
    font-size: 0.98rem;
    font-weight: 600;
    border-radius: 999px;
}

.summary-text {
    font-size: 1rem;
    margin-top: 0.3rem;
    margin-bottom: 0.3rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 데이터 로드
# -----------------------------
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        st.error(f"데이터 파일을 찾을 수 없습니다.\n\n확인 경로:\n{DATA_PATH}")
        st.stop()

    df = pd.read_csv(DATA_PATH)

    year_col = None
    month_col = None

    for col in ["year", "Year", "연도"]:
        if col in df.columns:
            year_col = col
            break

    for col in ["month", "Month", "월"]:
        if col in df.columns:
            month_col = col
            break

    if year_col is None or month_col is None:
        date_col = None
        for col in ["기준년월", "연월", "date", "Date"]:
            if col in df.columns:
                date_col = col
                break

        if date_col is not None:
            temp = df[date_col].astype(str).str.replace(r"[^0-9]", "", regex=True).str.zfill(6)
            df["year"] = temp.str[:4].astype(int)
            df["month"] = temp.str[4:6].astype(int)
            year_col = "year"
            month_col = "month"
        else:
            st.error("연도/월 정보를 찾을 수 없습니다. year/month 또는 기준년월 컬럼이 필요합니다.")
            st.stop()

    if year_col != "year":
        df = df.rename(columns={year_col: "year"})
    if month_col != "month":
        df = df.rename(columns={month_col: "month"})

    value_cols = [col for col in VAR_LABEL_MAP.keys() if col in df.columns]
    keep_cols = ["year", "month"] + value_cols
    df = df[keep_cols].copy()

    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["month"] = pd.to_numeric(df["month"], errors="coerce")

    for col in value_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["year", "month"]).copy()
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)

    return df

# -----------------------------
# 세션 상태 초기화
# -----------------------------
def init_session_state():
    defaults = {
        "year_all": False,
        "var_all": False,
        "selected_years": [],
        "selected_var_labels": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# -----------------------------
# 전체 선택 토글 동기화
# -----------------------------
def sync_year_all(all_years):
    if st.session_state.year_all:
        st.session_state.selected_years = all_years.copy()
    else:
        st.session_state.selected_years = []

def sync_var_all(all_var_labels):
    if st.session_state.var_all:
        st.session_state.selected_var_labels = all_var_labels.copy()
    else:
        st.session_state.selected_var_labels = []

# -----------------------------
# 그래프 생성
# -----------------------------
def make_line_chart(df, variable_col, variable_label, selected_years):
    fig = go.Figure()

    for year in sorted(selected_years):
        yearly_data = df[df["year"] == year].sort_values("month")
        if yearly_data.empty:
            continue

        fig.add_trace(
            go.Scatter(
                x=yearly_data["month"],
                y=yearly_data[variable_col],
                mode="lines+markers",
                name=str(year),
                marker=dict(size=7),
                line=dict(width=2),
                customdata=yearly_data["month"].map(MONTH_LABELS),
                hovertemplate=(
                    "월: %{customdata}<br>"
                    f"연도: {year}<br>"
                    "값: %{y:,.0f}<extra></extra>"
                )
            )
        )

    fig.update_layout(
        title=variable_label,
        xaxis_title="월",
        yaxis_title="값",
        hovermode="closest",
        legend_title="연도",
        template="plotly_dark",
        height=420,
        margin=dict(l=30, r=30, t=60, b=30),
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=list(MONTH_LABELS.keys()),
        ticktext=list(MONTH_LABELS.values())
    )
    fig.update_yaxes(tickformat=",")

    return fig

# -----------------------------
# 메인 실행
# -----------------------------
def run_dashboard():
    init_session_state()
    df = load_data()

    all_years = sorted(df["year"].dropna().unique().tolist())
    available_var_cols = [col for col in VAR_LABEL_MAP.keys() if col in df.columns]
    available_var_labels = [VAR_LABEL_MAP[col] for col in available_var_cols]

    st.title("전국 관광 데이터 월별 변동 패턴 대시보드")
    st.write("관광 관련 주요 지표의 월별 변동 패턴을 확인할 수 있습니다.")

    st.subheader("분석 조건")

    left, right = st.columns(2)

    # -----------------------------
    # 연도 선택
    # -----------------------------
    with left:
        st.markdown("### 연도 선택")

        st.toggle(
            "전체 선택",
            key="year_all",
            on_change=sync_year_all,
            args=(all_years,)
        )

        st.pills(
            "연도 선택",
            options=all_years,
            selection_mode="multi",
            key="selected_years",
            disabled=st.session_state.year_all,
            label_visibility="collapsed"
        )

    # -----------------------------
    # 변수 선택
    # -----------------------------
    with right:
        st.markdown("### 변수 선택")

        st.toggle(
            "전체 선택",
            key="var_all",
            on_change=sync_var_all,
            args=(available_var_labels,)
        )

        st.pills(
            "변수 선택",
            options=available_var_labels,
            selection_mode="multi",
            key="selected_var_labels",
            disabled=st.session_state.var_all,
            label_visibility="collapsed"
        )

    selected_years = st.session_state.selected_years
    selected_var_labels = st.session_state.selected_var_labels

    st.divider()

    year_text = ", ".join(map(str, selected_years)) if selected_years else "없음"
    var_text = ", ".join(selected_var_labels) if selected_var_labels else "없음"

    st.markdown(f"<p class='summary-text'><b>선택 연도:</b> {year_text}</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='summary-text'><b>선택 변수:</b> {var_text}</p>", unsafe_allow_html=True)

    st.divider()

    if not selected_years or not selected_var_labels:
        st.info("연도와 변수를 선택하면 그래프가 표시됩니다.")
        return

    selected_var_cols = [LABEL_TO_VAR[label] for label in selected_var_labels if label in LABEL_TO_VAR]

    for var_col in selected_var_cols:
        var_label = VAR_LABEL_MAP[var_col]
        fig = make_line_chart(df, var_col, var_label, selected_years)
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 탭 구조로 실행
# -----------------------------
def main():
    tab_home, tab1, tab3, tab4 = st.tabs([
        "🏠 소개",
        "📈 전국 월별 변화",
        "🗺️ 지역별 방문 변화",
        "📊 전국 관광 소비 분석"
    ])

    # ============================================
    # 탭1: 소개
    # ============================================
    with tab_home:
        # ===== 제목 =====
        st.markdown(
            "<h1 style='text-align:center;'>🧳 전국 관광 데이터 대시보드</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:gray;'>"
            "2018~2025년 전국 관광 방문자와 소비 데이터를 분석한 대시보드입니다."
            "</p>",
            unsafe_allow_html=True
        )

        # ===== 안내 문구 (박스) =====
        st.markdown(
            "<div style='background-color:#e7f1ff; padding:15px; "
            "border-radius:10px; text-align:center; color:#1f77b4; "
            "font-weight:600; margin:15px auto; max-width:600px;'>"
            "👆 상단의 탭을 눌러 원하는 분석 화면으로 이동하세요."
            "</div>",
            unsafe_allow_html=True
        )

        st.divider()

        # ===== 본문 (가운데 컬럼) =====
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown(
                "<h3 style='text-align:center;'>무엇을 볼 수 있나요?</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='text-align:center;'>"
                "<b>전국 월별 변화</b>: 연도별 방문자 수와 소비의 월별 패턴 비교<br>"
                "<b>지역별 방문 변화</b>: 17개 광역시도 방문자 규모 및 시간별 추이<br>"
                "<b>전국 관광 소비 분석</b>: 관광 소비 항목별 월별 추이"
                "</p>",
                unsafe_allow_html=True
            )
            st.write("")

            st.markdown(
                "<h3 style='text-align:center;'>주요 발견</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='text-align:center;'>"
                "관광 소비는 2022년 이후 뚜렷한 회복세를 보임<br>"
                "코로나 시기(2020년) 소비가 급감한 뒤 점진적으로 회복<br>"
                "방문자 수는 매년 5월과 10월에 정점을 이루는 계절성 존재"
                "</p>",
                unsafe_allow_html=True
            )
            st.write("")

            st.markdown(
                "<h3 style='text-align:center;'>데이터 출처</h3>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<p style='text-align:center;'>한국관광공사 데이터랩 (2018~2025)</p>",
                unsafe_allow_html=True
            )

    # ============================================
    # 탭1(전국 월별 변화): run_dashboard 호출  ⭐추가됨
    # ============================================
    with tab1:
        run_dashboard()

    # ============================================
    # 탭3: 지역별 방문 변화
    # ============================================
    with tab3:
        st.subheader("지역별 방문자 현황")

        base = Path(__file__).resolve().parent / "data" / "processed"
        df_region = pd.read_csv(base / "02_regional_wide.csv")

        years = sorted(df_region["연도"].unique())
        selected_year = st.pills(
            "연도를 선택하세요",
            years,
            default=years[-1],
        )
        if selected_year is None:
            selected_year = years[-1]

        year_df = df_region[df_region["연도"] == selected_year]
        year_df = year_df.sort_values("광역지자체 방문자 수", ascending=True)

        fig = px.bar(
            year_df,
            x="광역지자체 방문자 수",
            y="광역지자체명",
            orientation="h",
            title=f"{selected_year}년 지역별 방문자 수",
            text="광역지자체 방문자 비율",
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(template="plotly_dark", height=600)
        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        st.subheader("지역별 방문자 수 추이")
        render_regional_visitor_trend()

    # ============================================
    # 탭4: 전국 관광 소비 분석
    # ============================================
    with tab4:
        st.subheader("전국 관광 소비 추이")
        render_monthly_consumption_trend()


if __name__ == "__main__":
    main()