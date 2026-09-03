import plotly.express as px
from dashboard.config import YEAR_COLUMN, MONTH_COLUMN


def plot_yearly_comparison(df, value_col, label_name):
    # 원본 복사
    temp = df.copy()

    # 필요한 값이 없는 행 제거
    temp = temp.dropna(subset=[YEAR_COLUMN, MONTH_COLUMN, value_col])

    # 타입 정리
    temp[YEAR_COLUMN] = temp[YEAR_COLUMN].astype(int)
    temp[MONTH_COLUMN] = temp[MONTH_COLUMN].astype(int)

    # 연도-월별 평균 계산
    monthly = (
        temp.groupby([YEAR_COLUMN, MONTH_COLUMN], as_index=False)[value_col]
        .mean()
        .sort_values([YEAR_COLUMN, MONTH_COLUMN])
    )

    # Plotly에서 범례를 보기 좋게 하기 위해 문자열 변환
    monthly[YEAR_COLUMN] = monthly[YEAR_COLUMN].astype(str)

    # 선 그래프 생성
    fig = px.line(
        monthly,
        x=MONTH_COLUMN,
        y=value_col,
        color=YEAR_COLUMN,
        markers=True,
        title=f"{label_name} 연도별 월별 비교"
    )

    # hover에 표시될 문구 설정
    fig.update_traces(
        hovertemplate=(
            "<b>연도</b>: %{fullData.name}<br>"
            "<b>월</b>: %{x}월<br>"
            f"<b>{label_name}</b>: %{{y:,.0f}}<extra></extra>"
        ),
        line=dict(width=3),
        marker=dict(size=8)
    )

    # 레이아웃 설정
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="월",
        yaxis_title=label_name,
        legend_title="연도",
        height=550,
        hovermode="x unified"
    )

    # x축 1~12월 고정
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(1, 13)),
        ticktext=[f"{i}월" for i in range(1, 13)]
    )

    return fig