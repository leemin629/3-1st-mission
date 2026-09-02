from pathlib import Path
import re
from collections import Counter, defaultdict

# =========================================================
# 설정
# =========================================================

BASE_DIR = Path(".")

# 입력 파일 -> 출력 파일
FILE_MAP = [
    ("04_보고서_1부.md", "07_최종보고서_1부.md"),
    ("05_보고서_2부.md", "08_최종보고서_2부.md"),
    ("06_보고서_3부.md", "09_최종보고서_3부.md"),
]

# 입력 파일이 위 이름이 아닐 경우 여기만 바꾸면 됩니다.
# 예:
# FILE_MAP = [
#     ("01_초안_1부.md", "07_최종보고서_1부.md"),
#     ("02_초안_2부.md", "08_최종보고서_2부.md"),
#     ("03_초안_3부.md", "09_최종보고서_3부.md"),
# ]

AUDIT_FILE = "10_v3_치환점검보고서.txt"

REPORT_TITLE_OLD_PATTERNS = [
    r"전국 관광 계절성 분석 보고서",
    r"전국 관광 계절지수 분석 보고서",
]

REPORT_TITLE_NEW = "전국 관광 연중 변동 패턴 분석 보고서"

# =========================================================
# 유틸
# =========================================================

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, text: str):
    path.write_text(text, encoding="utf-8")

def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.MULTILINE))

def apply_sub(text: str, pattern: str, repl: str, counter: Counter, key: str, flags=0):
    new_text, n = re.subn(pattern, repl, text, flags=flags)
    if n > 0:
        counter[key] += n
    return new_text

# =========================================================
# 1) 제목/소제목 치환
# =========================================================

def replace_headings(text: str, counter: Counter) -> str:
    # 메인 보고서 제목
    for pat in REPORT_TITLE_OLD_PATTERNS:
        text = apply_sub(
            text,
            pat,
            REPORT_TITLE_NEW,
            counter,
            f"[제목] {pat} -> {REPORT_TITLE_NEW}"
        )

    heading_rules = [
        # 장/절 제목
        (r"^(#+\s*.*)계절성 분석(.*)$", r"\1연중 변동 패턴 분석\2"),
        (r"^(#+\s*.*)계절성 비교(.*)$", r"\1연중 변동 패턴 비교\2"),
        (r"^(#+\s*.*)계절지수 분석(.*)$", r"\1월별 상대수준 분석\2"),
        (r"^(#+\s*.*)계절지수 비교(.*)$", r"\1월별 상대수준 비교\2"),
        (r"^(#+\s*.*)계절지수(.*)$", r"\1월별 상대수준\2"),
        (r"^(#+\s*.*)계절성(.*)$", r"\1연중 변동 패턴\2"),
        (r"^(#+\s*.*)전체평균=100(.*)$", r"\112개월 평균=100\2"),
    ]

    for pat, repl in heading_rules:
        text = apply_sub(
            text,
            pat,
            repl,
            counter,
            f"[소제목] {pat} -> {repl}",
            flags=re.MULTILINE
        )

    return text

# =========================================================
# 2) 표/그림 제목 치환
# =========================================================

def replace_captions(text: str, counter: Counter) -> str:
    caption_rules = [
        # 표/그림/도/그래프 제목
        (r"^(\s*(표|그림|도|그래프)\s*[\d\-]+[\.]?\s*.*)계절지수(.*)$", r"\1월별 상대수준\3"),
        (r"^(\s*(표|그림|도|그래프)\s*[\d\-]+[\.]?\s*.*)계절성(.*)$", r"\1연중 변동 패턴\3"),
        (r"^(\s*(표|그림|도|그래프)\s*[\d\-]+[\.]?\s*.*)전체평균=100(.*)$", r"\112개월 평균=100\3"),
    ]

    for pat, repl in caption_rules:
        text = apply_sub(
            text,
            pat,
            repl,
            counter,
            f"[표/그림] {pat} -> {repl}",
            flags=re.MULTILINE
        )

    return text

# =========================================================
# 3) 본문 자연화 치환
# =========================================================

def replace_body_phrases(text: str, counter: Counter) -> str:
    body_rules = [
        # 가장 중요한 문장 자연화
        (r"계절성이 강하게 나타났다", "연중 변동 폭이 크게 나타났다"),
        (r"계절성이 강하다", "연중 변동 폭이 크다"),
        (r"계절성이 크게 나타났다", "연중 변동 폭이 크게 나타났다"),
        (r"계절성이 뚜렷하다", "월별 차이가 뚜렷하다"),
        (r"계절성이 존재한다", "연중 변동 패턴이 나타난다"),
        (r"계절성이 확인되었다", "연중 변동 패턴이 확인되었다"),
        (r"계절성이 약하다", "연중 변동 폭이 작다"),
        (r"계절성이 낮다", "연중 변동 폭이 크지 않다"),

        (r"계절적 변동", "월별 변동"),
        (r"계절적 차이", "월별 차이"),
        (r"계절적 패턴", "연중 변동 패턴"),
        (r"계절적 요인", "월별 변동 요인"),
        (r"계절적 특성", "월별 변동 특성"),
        (r"계절적 집중", "특정 월 집중"),
        (r"계절적 상승", "특정 시기 상승"),
        (r"계절적 하락", "특정 시기 하락"),

        (r"성수기", "상대수준이 높은 시기"),
        (r"비수기", "상대수준이 낮은 시기"),

        # 해석 표현 자연화
        (r"전체평균을 100으로 두고", "12개월 평균을 100으로 두고"),
        (r"전체 평균을 100으로 두고", "12개월 평균을 100으로 두고"),
        (r"전체평균=100", "12개월 평균=100"),
        (r"전체 평균=100", "12개월 평균=100"),

        (r"계절지수 값", "월별 상대수준 값"),
        (r"계절지수는", "월별 상대수준은"),
        (r"계절지수를", "월별 상대수준을"),
        (r"계절지수의", "월별 상대수준의"),

        # 자주 나오는 분석 표현
        (r"특정 월에 계절성이 집중된다", "특정 월에 변동이 집중된다"),
        (r"계절성 차이가 크다", "월별 차이가 크다"),
        (r"계절성 차이가 작다", "월별 차이가 작다"),
        (r"계절성 완화", "월별 변동 완화"),
        (r"계절성 확대", "월별 변동 확대"),
    ]

    for old, new in body_rules:
        text = apply_sub(
            text,
            re.escape(old),
            new,
            counter,
            f"[본문] {old} -> {new}"
        )

    return text

# =========================================================
# 4) 일반 용어 통일 치환
# =========================================================

def replace_general_terms(text: str, counter: Counter) -> str:
    general_rules = [
        # 남은 것들 일괄 정리
        (r"계절지수", "월별 상대수준"),
        (r"계절성", "연중 변동 패턴"),
        (r"전체평균=100", "12개월 평균=100"),
        (r"전체 평균=100", "12개월 평균=100"),
        (r"전체평균", "12개월 평균"),
    ]

    for pat, repl in general_rules:
        text = apply_sub(
            text,
            pat,
            repl,
            counter,
            f"[일반] {pat} -> {repl}"
        )

    return text

# =========================================================
# 5) 수식/방법론 문장 보정
# =========================================================

def replace_methodology(text: str, counter: Counter) -> str:
    method_rules = [
        (
            r"월별 평균값을 전체 평균으로 나누어 산출하였다",
            "월별 평균값을 12개월 평균으로 나누어 산출하였다"
        ),
        (
            r"각 월의 평균을 전체 평균과 비교하였다",
            "각 월의 평균을 12개월 평균과 비교하였다"
        ),
        (
            r"각 월의 값을 전체 평균 대비 지수화하였다",
            "각 월의 값을 12개월 평균 대비 상대수준으로 산출하였다"
        ),
        (
            r"평균을 100으로 환산하였다",
            "12개월 평균을 100으로 환산하였다"
        ),
        (
            r"계절지수는 월별 평균을 전체 평균으로 나눈 값이다",
            "월별 상대수준은 월별 평균을 12개월 평균으로 나눈 값이다"
        ),
    ]

    for old, new in method_rules:
        text = apply_sub(
            text,
            re.escape(old),
            new,
            counter,
            f"[방법론] {old} -> {new}"
        )

    return text

# =========================================================
# 6) 서식 정리
# =========================================================

def cleanup_format(text: str, counter: Counter) -> str:
    original = text

    # 이중 공백 정리
    text = re.sub(r"[ \t]{2,}", " ", text)

    # 빈 줄 3개 이상 -> 2개
    text = re.sub(r"\n{3,}", "\n\n", text)

    # "12개월 평균 = 100" 형태 통일
    text = re.sub(r"12개월 평균\s*=\s*100", "12개월 평균=100", text)

    # 괄호 앞 공백 정리
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r"\(\s+", "(", text)

    if text != original:
        counter["[서식] 공백/빈줄/표기 정리"] += 1

    return text

# =========================================================
# 7) 위험 표현 탐지
# =========================================================

RISK_PATTERNS = [
    r"순수 계절성",
    r"계절요인만 반영",
    r"비수기 특성 입증",
    r"성수기 특성 입증",
    r"계절적 불균형",
    r"계절적 왜곡",
    r"seasonal index",
    r"seasonality",
    r"전체평균=100",
    r"전체 평균=100",
    r"계절지수",
    r"계절성",
]

def detect_risks(text: str):
    findings = defaultdict(list)
    lines = text.splitlines()

    for i, line in enumerate(lines, start=1):
        for pat in RISK_PATTERNS:
            if re.search(pat, line):
                findings[pat].append((i, line.strip()))

    return findings

# =========================================================
# 8) 처리 파이프라인
# =========================================================

def transform_text(text: str):
    counter = Counter()

    text = replace_headings(text, counter)
    text = replace_captions(text, counter)
    text = replace_methodology(text, counter)
    text = replace_body_phrases(text, counter)
    text = replace_general_terms(text, counter)
    text = cleanup_format(text, counter)

    risks = detect_risks(text)
    return text, counter, risks

# =========================================================
# 9) 점검 보고서 작성
# =========================================================

def build_audit_report(results):
    """
    results = [
        {
            "input": ...,
            "output": ...,
            "counter": Counter(...),
            "risks": {...}
        },
        ...
    ]
    """
    lines = []
    lines.append("v3 치환 점검 보고서")
    lines.append("=" * 60)
    lines.append("")

    total_counter = Counter()
    total_risk_count = 0

    for item in results:
        input_file = item["input"]
        output_file = item["output"]
        counter = item["counter"]
        risks = item["risks"]

        lines.append(f"[파일] {input_file} -> {output_file}")
        lines.append("-" * 60)

        if counter:
            lines.append("치환 내역:")
            for k, v in counter.most_common():
                lines.append(f"  - {k}: {v}회")
                total_counter[k] += v
        else:
            lines.append("치환 내역: 없음")

        lines.append("")

        if risks:
            lines.append("잔여 위험 표현:")
            for pat, hits in risks.items():
                total_risk_count += len(hits)
                lines.append(f"  - 패턴: {pat} ({len(hits)}건)")
                for line_no, line_text in hits[:10]:
                    lines.append(f"      · line {line_no}: {line_text}")
                if len(hits) > 10:
                    lines.append(f"      · ... 외 {len(hits) - 10}건")
        else:
            lines.append("잔여 위험 표현: 없음")

        lines.append("")
        lines.append("")

    lines.append("=" * 60)
    lines.append("[전체 요약]")
    lines.append("-" * 60)

    if total_counter:
        for k, v in total_counter.most_common():
            lines.append(f"  - {k}: {v}회")
    else:
        lines.append("  - 전체 치환 없음")

    lines.append("")
    lines.append(f"잔여 위험 표현 총 건수: {total_risk_count}건")
    lines.append("")

    if total_risk_count == 0:
        lines.append("판정: 제출용으로 매우 양호")
    elif total_risk_count <= 10:
        lines.append("판정: 제출 가능, 잔여 표현 수동 점검 권장")
    else:
        lines.append("판정: 자동 치환 후 수동 검수 필요")

    return "\n".join(lines)

# =========================================================
# 10) 메인 실행
# =========================================================

def main():
    results = []

    for input_name, output_name in FILE_MAP:
        input_path = BASE_DIR / input_name
        output_path = BASE_DIR / output_name

        if not input_path.exists():
            print(f"[경고] 입력 파일 없음: {input_path}")
            results.append({
                "input": input_name,
                "output": output_name,
                "counter": Counter(),
                "risks": {"FILE_NOT_FOUND": [(0, f"입력 파일 없음: {input_name}")]}
            })
            continue

        text = read_text(input_path)
        new_text, counter, risks = transform_text(text)

        write_text(output_path, new_text)

        results.append({
            "input": input_name,
            "output": output_name,
            "counter": counter,
            "risks": risks
        })

        print(f"[완료] {input_name} -> {output_name}")

    audit_text = build_audit_report(results)
    write_text(BASE_DIR / AUDIT_FILE, audit_text)

    print(f"[완료] 점검 보고서 생성: {AUDIT_FILE}")
    print("[종료] v3 치환 끝판왕 실행 완료")

if __name__ == "__main__":
    main()