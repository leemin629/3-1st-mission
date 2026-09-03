# dashboard/config.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "processed" / "monthly_tourism_variables.csv"

APP_TITLE = "전국 관광 데이터 월별 변동 패턴 대시보드"
APP_DESCRIPTION = "관광 관련 주요 지표의 월별 변동 패턴을 확인할 수 있습니다."

DATE_COLUMN = "기준년월"
YEAR_COLUMN = "연도"
MONTH_COLUMN = "월"

MAX_VARIABLE_SELECTION = 3

VARIABLE_OPTIONS = {
    "전체방문자수": "전체방문자수",
    "관광총소비": "관광총소비_천원",
    "숙박업소비": "숙박업소비_천원",
    "식음료업소비": "식음료업소비_천원",
    "쇼핑소비": "쇼핑소비_천원",
}