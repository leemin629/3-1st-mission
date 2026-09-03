import pandas as pd
import streamlit as st

from dashboard.data_loader import load_data
from dashboard.charts import plot_yearly_comparison
from dashboard.config import (
    APP_TITLE,
    APP_DESCRIPTION,
    VARIABLE_OPTIONS,
    YEAR_COLUMN,
    MONTH_COLUMN,
)

st.set_page_config(page_title=APP_TITLE, layout="wide")

st.title(APP_TITLE)
st.markdown(APP_DESCRIPTION)

# ----------------------------
# 데이터 로드
# ----------------------------
try:
    df = load_data()
except Exception as e:
    st.error(f"데이터 로딩 오류: {e}")
    st.stop()

# 연도 / 월 컬럼 숫자형 변환
df[YEAR_COLUMN] = pd.to_numeric(df[YEAR_COLUMN], errors="coerce")
df[MONTH_COLUMN] = pd.to_numeric(df[MONTH_COLUMN], errors="coerce")

# 선택 옵션 목록 생성
year_list = sorted(df[YEAR_COLUMN].dropna().astype(int).unique().tolist())
variable_labels = list(VARIABLE_OPTIONS.keys())

# ----------------------------
# session_state 초기화
# ----------------------------
if "selected_years" not in st.session_state:
    st.session_state.selected_years = []

if "selected_labels" not in st.session_state:
    st.session_state.selected_labels = []

if "all_years_toggle" not in st.session_state:
    st.session_state.all_years_toggle = False

if "all_vars_toggle" not in st.session_state:
    st.session_state.all_vars_toggle = False

# ----------------------------
# 토글 동기화 함수
# ON  -> 전체 선택
# OFF -> 전체 해제
# ----------------------------
def sync_year_toggle():
    if st.session_state.all_years_toggle:
        st.session_state.selected_years = year_list
    else:
        st.session_state.selected_years = []


def sync_var_toggle():
    if st.session_state.all_vars_toggle:
        st.session_state.selected_labels = variable_labels
    else:
        st.session_state.selected_labels = []


# ----------------------------
# 분석 조건 UI
# ----------------------------
st.subheader("분석 조건")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 연도 선택")
    st.toggle(
        "전체 선택",
        key="all_years_toggle",
        on_change=sync_year_toggle
    )

    selected_years = st.pills(
        "연도 선택",
        options=year_list,
        selection_mode="multi",
        key="selected_years",
        disabled=st.session_state.all_years_toggle,
        label_visibility="collapsed",
    )

with col2:
    st.markdown("### 변수 선택")
    st.toggle(
        "전체 선택",
        key="all_vars_toggle",
        on_change=sync_var_toggle
    )

    selected_labels = st.pills(
        "변수 선택",
        options=variable_labels,
        selection_mode="multi",
        key="selected_labels",
        disabled=st.session_state.all_vars_toggle,
        label_visibility="collapsed",
    )

# None 방지
selected_years = selected_years if selected_years is not None else []
selected_labels = selected_labels if selected_labels is not None else []

st.markdown("---")

# ----------------------------
# 선택 안내
# ----------------------------
if not selected_years or not selected_labels:
    st.info("연도와 변수를 선택하면 그래프와 데이터가 표시됩니다.")
    st.stop()

# ----------------------------
# 데이터 필터링
# ----------------------------
filtered_df = df[df[YEAR_COLUMN].isin(selected_years)].copy()

if filtered_df.empty:
    st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
    st.stop()

filtered_df = filtered_df.sort_values([YEAR_COLUMN, MONTH_COLUMN]).reset_index(drop=True)

st.caption(f"선택 연도: {', '.join(map(str, selected_years))}")
st.caption(f"선택 변수: {', '.join(selected_labels)}")

st.markdown("---")

# ----------------------------
# 그래프 출력
# ----------------------------
for label in selected_labels:
    col_name = VARIABLE_OPTIONS[label]

    if col_name not in filtered_df.columns:
        st.warning(f"'{label}'에 해당하는 컬럼('{col_name}')이 데이터에 없습니다.")
        continue

    st.subheader(f"{label}: 연도별 월별 비교")
    fig = plot_yearly_comparison(filtered_df, col_name, label)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("---")

# ----------------------------
# 데이터 미리보기
# ----------------------------
preview_cols = [YEAR_COLUMN, MONTH_COLUMN] + [
    VARIABLE_OPTIONS[label]
    for label in selected_labels
    if VARIABLE_OPTIONS[label] in filtered_df.columns
]

preview_df = (
    filtered_df[preview_cols]
    .sort_values([YEAR_COLUMN, MONTH_COLUMN])
    .reset_index(drop=True)
)

rename_map = {VARIABLE_OPTIONS[label]: label for label in selected_labels}
preview_df = preview_df.rename(columns=rename_map)

st.subheader("선택한 연도 데이터 미리보기")
st.dataframe(preview_df, use_container_width=True, hide_index=True)