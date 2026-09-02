from pathlib import Path
import re

BASE_DIR = Path(".")

OUTPUT_FILES = [
    "04_최종보고서_1부.md",
    "05_최종보고서_2부.md",
    "06_최종보고서_3부.md",
]

REPORT_TITLE = "전국 관광 월별 반복 패턴 분석 보고서"

REPLACEMENTS = [
    ("계절지수", "월별 반복 패턴"),
    ("계절성 지수", "월별 반복 패턴"),
    ("seasonal index", "monthly recurring pattern"),
    ("Seasonal Index", "Monthly Recurring Pattern"),
]

def apply_replacements(text: str) -> str:
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    return text

def normalize_markdown(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"^(#{1,6})([^\s#])", r"\1 \2", text, flags=re.MULTILINE)
    text = re.sub(r"^(\d+\.\d+)([^\s])", r"\1 \2", text, flags=re.MULTILINE)
    return text.strip() + "\n"

def normalize_section_format(text: str) -> str:
    text = re.sub(r"^(#{1,6}\s*)(5\.3)([^\s])", r"\1\2 \3", text, flags=re.MULTILINE)
    text = re.sub(r"^(#{1,6}\s*)(5\.4)([^\s])", r"\1\2 \3", text, flags=re.MULTILINE)
    text = re.sub(r"^(5\.3)([^\s])", r"\1 \2", text, flags=re.MULTILINE)
    text = re.sub(r"^(5\.4)([^\s])", r"\1 \2", text, flags=re.MULTILINE)
    return text

def make_submission_header(part_no: int) -> str:
    return (
        f"# {REPORT_TITLE}\n\n"
        f"**제출용 최종본 / 제{part_no}부**\n\n"
        "---\n\n"
    )

def process_text(text: str, part_no: int) -> str:
    text = apply_replacements(text)
    text = normalize_section_format(text)
    text = normalize_markdown(text)
    return make_submission_header(part_no) + text

def find_input_file(prefix: str):
    candidates = sorted([
        p for p in BASE_DIR.glob(f"{prefix}*.md")
        if not p.name.startswith(("04_", "05_", "06_"))
    ])
    return candidates[0] if candidates else None

def main():
    prefixes = ["01", "02", "03"]

    for i, (prefix, output_name) in enumerate(zip(prefixes, OUTPUT_FILES), start=1):
        input_path = find_input_file(prefix)

        if input_path is None:
            print(f"[경고] {prefix}로 시작하는 md 파일을 찾지 못했습니다.")
            continue

        print(f"[입력] {input_path.name}")

        text = input_path.read_text(encoding="utf-8")
        final_text = process_text(text, i)

        output_path = BASE_DIR / output_name
        output_path.write_text(final_text, encoding="utf-8")

        print(f"[완료] 생성됨: {output_path.name}")

    print("\n모든 작업이 끝났습니다.")

if __name__ == "__main__":
    main()