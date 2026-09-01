from pathlib import Path
import pandas as pd
import re


def get_project_root():
    """
    src/check_data.py 기준으로 프로젝트 루트 폴더 반환
    예: 3-1st mission/
    """
    return Path(__file__).resolve().parents[1]


def classify_file_type(filename: str) -> str:
    """
    파일명 기준으로 데이터 유형 분류
    """
    name = filename

    if "관광소비 추이" in name:
        return "tourism_spending_trend"
    elif "방문자 수 추이" in name:
        return "visitor_trend"
    elif "업종별 지출액" in name:
        return "business_spending"
    elif "지역별 방문자 수" in name and "광역" in name:
        return "regional_visitors_metro"
    elif "지역별 방문자 수" in name and "기초" in name:
        return "regional_visitors_local"
    elif "지역별 지출액" in name:
        return "regional_spending"
    else:
        return "unknown"


def extract_period(filename: str):
    """
    파일명에서 기간 추출
    예: 201801-201812_관광소비 추이.csv
    -> ('201801', '201812')
    """
    match = re.search(r"(\d{6})-(\d{6})", filename)
    if match:
        return match.group(1), match.group(2)
    return None, None


def read_csv_safe(file_path: Path):
    """
    여러 인코딩으로 CSV 읽기 시도
    """
    encodings = ["utf-8-sig", "cp949", "euc-kr", "utf-8"]

    last_error = None
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            return df, enc
        except Exception as e:
            last_error = e

    raise last_error


def guess_date_columns(columns):
    """
    컬럼명 중 날짜/연월 관련 가능성이 있는 컬럼 찾기
    """
    keywords = ["date", "month", "year", "연월", "날짜", "월", "기준", "시점"]
    date_cols = []

    for col in columns:
        col_str = str(col)
        if any(k in col_str for k in keywords):
            date_cols.append(col_str)

    return date_cols


def inspect_file(file_path: Path):
    """
    파일 1개 점검 결과 반환
    """
    filename = file_path.name
    file_type = classify_file_type(filename)
    period_start, period_end = extract_period(filename)

    try:
        df, encoding_used = read_csv_safe(file_path)

        columns = [str(c) for c in df.columns.tolist()]
        null_count = int(df.isnull().sum().sum())
        date_cols = guess_date_columns(columns)

        info = {
            "filename": filename,
            "file_type": file_type,
            "period_start": period_start,
            "period_end": period_end,
            "rows": df.shape[0],
            "cols": df.shape[1],
            "encoding": encoding_used,
            "null_count": null_count,
            "date_like_columns": " | ".join(date_cols) if date_cols else "",
            "columns": " | ".join(columns),
            "status": "ok",
            "error_message": "",
            "head3": df.head(3).to_string(index=False)
        }

    except Exception as e:
        info = {
            "filename": filename,
            "file_type": file_type,
            "period_start": period_start,
            "period_end": period_end,
            "rows": None,
            "cols": None,
            "encoding": None,
            "null_count": None,
            "date_like_columns": "",
            "columns": "",
            "status": "error",
            "error_message": str(e),
            "head3": ""
        }

    return info


def print_basic_summary(result_df: pd.DataFrame):
    """
    터미널용 요약 출력
    """
    print("\n" + "=" * 70)
    print("RAW DATA CHECK SUMMARY")
    print("=" * 70)

    print(f"\n총 파일 수: {len(result_df)}")

    print("\n[유형별 파일 개수]")
    type_counts = result_df["file_type"].value_counts(dropna=False)
    print(type_counts.to_string())

    print("\n[상태별 개수]")
    status_counts = result_df["status"].value_counts(dropna=False)
    print(status_counts.to_string())

    print("\n[읽기 실패 파일]")
    error_df = result_df[result_df["status"] == "error"]
    if error_df.empty:
        print("없음")
    else:
        for _, row in error_df.iterrows():
            print(f"- {row['filename']} -> {row['error_message']}")

    print("\n[유형별 샘플 파일]")
    for file_type in result_df["file_type"].dropna().unique():
        sample = result_df[result_df["file_type"] == file_type].head(1)
        if not sample.empty:
            row = sample.iloc[0]
            print(f"\n▶ {file_type}")
            print(f"  파일명: {row['filename']}")
            print(f"  기간: {row['period_start']} ~ {row['period_end']}")
            print(f"  shape: ({row['rows']}, {row['cols']})")
            print(f"  인코딩: {row['encoding']}")
            print(f"  날짜 관련 컬럼: {row['date_like_columns'] if row['date_like_columns'] else '없음'}")
            print(f"  컬럼명: {row['columns']}")


def save_text_report(result_df: pd.DataFrame, report_path: Path):
    """
    자세한 txt 리포트 저장
    """
    with open(report_path, "w", encoding="utf-8-sig") as f:
        f.write("=" * 80 + "\n")
        f.write("RAW DATA CHECK REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"총 파일 수: {len(result_df)}\n\n")

        f.write("[유형별 파일 개수]\n")
        f.write(result_df["file_type"].value_counts(dropna=False).to_string())
        f.write("\n\n")

        f.write("[상태별 개수]\n")
        f.write(result_df["status"].value_counts(dropna=False).to_string())
        f.write("\n\n")

        for _, row in result_df.iterrows():
            f.write("-" * 80 + "\n")
            f.write(f"파일명: {row['filename']}\n")
            f.write(f"유형: {row['file_type']}\n")
            f.write(f"기간: {row['period_start']} ~ {row['period_end']}\n")
            f.write(f"상태: {row['status']}\n")

            if row["status"] == "ok":
                f.write(f"행 수: {row['rows']}\n")
                f.write(f"열 수: {row['cols']}\n")
                f.write(f"인코딩: {row['encoding']}\n")
                f.write(f"결측치 수: {row['null_count']}\n")
                f.write(f"날짜 관련 컬럼: {row['date_like_columns']}\n")
                f.write(f"컬럼명: {row['columns']}\n")
                f.write("[상위 3행]\n")
                f.write(str(row["head3"]) + "\n")
            else:
                f.write(f"에러 메시지: {row['error_message']}\n")

            f.write("\n")


def main():
    project_root = get_project_root()
    raw_dir = project_root / "data" / "raw"
    output_dir = project_root / "output"

    output_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists():
        print(f"[오류] raw 폴더가 없습니다: {raw_dir}")
        return

    csv_files = sorted(raw_dir.glob("*.csv"))

    if not csv_files:
        print(f"[오류] raw 폴더에 CSV 파일이 없습니다: {raw_dir}")
        return

    print(f"[INFO] raw 폴더: {raw_dir}")
    print(f"[INFO] 발견된 CSV 파일 수: {len(csv_files)}")

    results = []
    for file_path in csv_files:
        print(f"[CHECK] {file_path.name}")
        info = inspect_file(file_path)
        results.append(info)

    result_df = pd.DataFrame(results)

    # 저장용 summary
    summary_path = output_dir / "check_data_summary.csv"
    report_path = output_dir / "check_data_report.txt"

    result_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    save_text_report(result_df, report_path)

    # 콘솔 요약 출력
    print_basic_summary(result_df)

    print("\n" + "=" * 70)
    print("저장 완료")
    print(f"- summary csv : {summary_path}")
    print(f"- detail txt  : {report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()