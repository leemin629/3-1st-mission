# make_images.py  (한 번만 실행하는 이미지 생성용 파일)
from pathlib import Path
from PIL import Image, ImageDraw

# assets 폴더 준비
img_dir = Path(__file__).resolve().parent / "assets"
img_dir.mkdir(exist_ok=True)   # 폴더 없으면 자동 생성

def make_season(filename, bg_color, circle_color, label):
    """단색 배경 + 원 + 글자로 계절 이미지를 만든다"""
    img = Image.new("RGB", (400, 300), bg_color)   # 400x300 배경
    draw = ImageDraw.Draw(img)
    draw.ellipse([150, 90, 250, 190], fill=circle_color)  # 가운데 원
    draw.text((160, 250), label, fill="white")            # 하단 글자
    img.save(img_dir / filename)
    print(f"저장 완료: {filename}")

# 계절별로 색을 다르게
make_season("spring.png", (255, 214, 224), (255, 130, 170), "SPRING")  # 분홍(봄)
make_season("summer.png", (135, 206, 235), (255, 200, 0),   "SUMMER")  # 하늘+태양(여름)
make_season("autumn.png", (255, 190, 120), (200, 80, 30),   "AUTUMN")  # 주황(가을)
make_season("winter.png", (220, 235, 255), (255, 255, 255), "WINTER")  # 하양(겨울)

print("=== 4장 모두 완성! ===")