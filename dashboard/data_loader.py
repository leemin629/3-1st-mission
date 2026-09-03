# dashboard/data_loader.py

import pandas as pd
from dashboard.config import DATA_PATH, DATE_COLUMN


def load_data():
    df = pd.read_csv(DATA_PATH)

    df[DATE_COLUMN] = pd.to_datetime(df[DATE_COLUMN], errors="coerce")

    return df