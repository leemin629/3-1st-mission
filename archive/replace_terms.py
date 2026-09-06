from pathlib import Path

# 긴 표현부터 먼저 치환
replacements = [
    ("월별 계절 패턴", "월별 변동 패턴"),
    ("계절 패턴", "월별 변동 패턴"),
    ("계절성 분석", "월별 변동 패턴 분석"),
    ("계절적 패턴", "월별 변동 패턴"),
    ("계절적 변동", "월별 변동"),
    ("계절적 차이", "월별 차이"),
    ("계절 변동", "월별 변동"),
    ("계절지수", "월별 상대수준 지수"),
    ("계절성", "월별 변동 패턴"),
]

src = Path(".")
dst = src / "term_fixed"
dst.mkdir(exist_ok=True)

targets = []
for p in src.iterdir():
    if p.is_file() and p.suffix.lower() in {".md", ".txt"}:
        targets.append(p)

print(f"대상 파일 수: {len(targets)}")
print("-" * 40)

for p in targets:
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = p.read_text(encoding="cp949")

    original = text
    total_count = 0

    for old, new in replacements:
        count = text.count(old)
        if count > 0:
            total_count += count
            text = text.replace(old, new)

    out_file = dst / p.name
    out_file.write_text(text, encoding="utf-8")

    print(f"{p.name}: {total_count}개 치환")

    if "계절" in text:
        print("  -> '계절' 표현이 남아 있음(사계절/계절별 등 수동 확인 필요)")

print("-" * 40)
print("완료: term_fixed 폴더를 확인하세요.")