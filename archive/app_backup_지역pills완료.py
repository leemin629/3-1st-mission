import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path
import plotly.express as px

def render_regional_visitor_trend():
    df = pd.read_csv("data/processed/02_regional_wide.csv")

    all_regions = sorted(df["광역지자체명"].unique())
    default_regions = ["서울특별시", "경기도", "부산광역시", "인천광역시", "제주특별자치도"]

    # multiselect -> pills 로 변경
    selected = st.pills(
        "지역 선택",
        options=all_regions,
        default=default_regions,
        selection_mode="multi"   # 여러 개 선택 허용
    )

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

    def render_monthly_consumption_trend():
        df = pd.read_csv("data/processed/monthly_tourism_variables.csv")

    consumption_cols = {
        "관광총소비_천원": "관광 총소비",
        "숙박업소비_천원": "숙박업",
        "식음료업소비_천원": "식음료업",
        "쇼핑소비_천원": "쇼핑"
    }

    # multiselect -> pills 로 변경
    selected = st.pills(
        "소비 항목 선택",
        options=list(consumption_cols.keys()),
        default=["관광총소비_천원"],
        selection_mode="multi",
        format_func=lambda x: consumption_cols[x]
    )

    if not selected:
        st.warning("소비 항목을 하나 이상 선택해주세요.")
        return

    df["기준년월"] = df["기준년월"].astype(str)

    long_df = df.melt(
        id_vars="기준년월",
        value_vars=selected,
        var_name="항목",
        value_name="소비액"
    )
    long_df["항목"] = long_df["항목"].map(consumption_cols)

    fig = px.line(
        long_df,
        x="기준년월",
        y="소비액",
        color="항목",
        labels={"소비액": "소비액 (천원)", "기준년월": "기준년월"},
        title="전국 관광 소비 추이 (월별)"
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="전국 관광 데이터 월별 변동 패턴 대시보드",
    page_icon="📊",
    layout="wide"
)

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
    tab_home, tab1, tab2, tab3 = st.tabs([
    "🏠 소개",
    "📈 전국 월별 변화",
    "🗺️ 지역별 방문자",
    "📊 지역별 방문자 추이"
])
    with tab_home:
        st.write("메인 소개 화면 (곧 채울 예정)")

    with tab1:
        run_dashboard()   # ← 지금 완성된 화면!

    with tab2:
        st.subheader("지역별 방문자 현황")

        # 1) 데이터 불러오기
        base = Path(__file__).resolve().parent / "data" / "processed"
        df_region = pd.read_csv(base / "02_regional_wide.csv")

        # 2) 연도 선택 드롭다운
        years = sorted(df_region["연도"].unique())
        selected_year = st.pills(
            "연도를 선택하세요",
            years,
            default=years[-1],        # 마지막 연도(2025) 기본 선택
        )

        # 아무것도 선택 안 했을 때 방어 코드
        if selected_year is None:
            selected_year = years[-1]

        # 3) 선택한 연도만 필터 + 방문자 수로 정렬
        year_df = df_region[df_region["연도"] == selected_year]
        year_df = year_df.sort_values("광역지자체 방문자 수", ascending=True)

        # 4) 가로 막대 그래프
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

    with tab3:
        st.subheader("지역별 방문자 수 추이")
        render_regional_visitor_trend()      # ← (1)번 호출

        st.divider()

        st.subheader("전국 관광 소비 추이")
        render_monthly_consumption_trend()   # ← (2)번 호출
  
if __name__ == "__main__":
    main()