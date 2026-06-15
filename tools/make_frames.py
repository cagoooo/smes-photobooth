# -*- coding: utf-8 -*-
"""
石門國小 AI 拍貼機 — 透明邊框產生器
=====================================
產出「中央真透明、四周裝飾外框」的直版 PNG，給拍貼機網頁套在 webcam 即時畫面上。
鐵則（沿用 photobooth-transparent-frame skill）：
  - 中央窗必須 alpha=0（webcam 才能透出來）
  - 校名一律寫死「桃園市龍潭區石門國民小學」（防「新明」誤植）
  - 裝飾全用向量畫（星/魚/氣球/獎牌/雪花/吉祥物），不靠 emoji 字型（避免豆腐 □）

用法：  python tools/make_frames.py
"""
import os, math
from PIL import Image, ImageDraw, ImageFont, ImageChops

W, H = 1080, 1440                       # 3:4 直版，適合平板拍貼
OUT = os.path.join(os.path.dirname(__file__), "..", "frames")
os.makedirs(OUT, exist_ok=True)

SCHOOL = "桃園市龍潭區石門國民小學"      # ⛔ 不可寫成「新明」
FONT_PATH  = r"C:\Windows\Fonts\msjh.ttc"     # 微軟正黑
FONTB_PATH = r"C:\Windows\Fonts\msjhbd.ttc"   # 微軟正黑 Bold
WIN = (70, 215, W - 70, H - 205)        # 中央透明窗（上留標題、下留校名）


def font(bold, size):
    try:
        return ImageFont.truetype(FONTB_PATH if bold else FONT_PATH, size)
    except OSError:
        return ImageFont.truetype(FONT_PATH, size)


def vgrad(c1, c2):
    col = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        col.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return col.resize((W, H)).convert("RGBA")


def text_c(d, xy, s, fnt, fill, shadow=None):
    if shadow:
        d.text((xy[0] + 2, xy[1] + 3), s, font=fnt, fill=shadow, anchor="mm")
    d.text(xy, s, font=fnt, fill=fill, anchor="mm")


# ---------- 向量裝飾元件 ----------
def star(d, cx, cy, r, color, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        ang = rot + i * math.pi / 5
        rad = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=color)


def fish(d, cx, cy, s, body, fin):
    d.ellipse([cx - s, cy - s * 0.62, cx + s, cy + s * 0.62], fill=body)
    d.polygon([(cx + s * 0.8, cy), (cx + s * 1.5, cy - s * 0.6),
               (cx + s * 1.5, cy + s * 0.6)], fill=fin)
    d.ellipse([cx - s * 0.62, cy - s * 0.26, cx - s * 0.5, cy - s * 0.14], fill=(40, 60, 70))


def bubbles(d, cx, cy, color):
    for dx, dy, rr in [(0, 0, 13), (20, -22, 8), (-16, -30, 5)]:
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr], outline=color, width=4)


# ---------- 裝飾叢集（每個畫一組，放在四個角帶區）----------
def cl_star(d, x, y, c1, c2, ac, i):
    star(d, x, y, 30, c1); star(d, x + (24 if i % 2 == 0 else -24), y + 22, 14, c2)


def cl_fish(d, x, y, c1, c2, ac, i):
    fish(d, x, y, 26, c1, c2); bubbles(d, x + (30 if i % 2 == 0 else -46), y - 30, ac)


def cl_balloon(d, x, y, c1, c2, ac, i):
    for dx, col in [(-17, c1), (17, c2)]:
        bx, by = x + dx, y - 4
        d.ellipse([bx - 16, by - 21, bx + 16, by + 21], fill=col)
        d.polygon([(bx - 4, by + 19), (bx + 4, by + 19), (bx, by + 27)], fill=col)
        d.line([(bx, by + 25), (bx + (7 if i % 2 else -7), by + 55)], fill=(150, 120, 90), width=2)


def cl_medal(d, x, y, c1, c2, ac, i):
    d.polygon([(x - 15, y - 36), (x - 2, y - 36), (x - 6, y + 2)], fill=c2)   # 緞帶
    d.polygon([(x + 15, y - 36), (x + 2, y - 36), (x + 6, y + 2)], fill=c2)
    d.ellipse([x - 21, y - 6, x + 21, y + 36], fill=c1)                       # 金牌
    d.ellipse([x - 21, y - 6, x + 21, y + 36], outline=(255, 255, 255), width=3)
    star(d, x, y + 15, 12, (255, 255, 255))


def cl_snow(d, x, y, c1, c2, ac, i):
    for k in range(6):
        a = k * math.pi / 3
        ex, ey = x + 26 * math.cos(a), y + 26 * math.sin(a)
        d.line([(x, y), (ex, ey)], fill=c1, width=4)
        for s in (0.55, 0.8):
            bx, by = x + 26 * s * math.cos(a), y + 26 * s * math.sin(a)
            for sgn in (0.6, -0.6):
                d.line([(bx, by), (bx + 9 * math.cos(a + sgn), by + 9 * math.sin(a + sgn))],
                       fill=c1, width=3)
    d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c2)


def cl_fishbig(d, x, y, c1, c2, ac, i):
    s = 32
    d.ellipse([x - s, y - s * 0.7, x + s, y + s * 0.7], fill=c1)                       # 身
    d.polygon([(x + s * 0.85, y), (x + s * 1.55, y - s * 0.7), (x + s * 1.55, y + s * 0.7)], fill=c2)  # 尾
    d.polygon([(x - s * 0.25, y - s * 0.65), (x + s * 0.25, y - s * 1.0),
               (x + s * 0.45, y - s * 0.55)], fill=c2)                                 # 背鰭
    d.ellipse([x - s * 0.6, y - s * 0.32, x - s * 0.22, y + s * 0.06], fill=(255, 255, 255))  # 眼白
    d.ellipse([x - s * 0.5, y - s * 0.22, x - s * 0.3, y - s * 0.02], fill=(40, 55, 65))      # 瞳
    d.arc([x - s * 0.45, y - s * 0.05, x + s * 0.15, y + s * 0.5], 15, 150, fill=(150, 50, 35), width=3)  # 笑


MOTIFS = {"star": cl_star, "fish": cl_fish, "balloon": cl_balloon,
          "medal": cl_medal, "snow": cl_snow, "fishbig": cl_fishbig}


def build(name, c1, c2, frame_rgb, win_line, win_soft, title, eyebrow, tagline,
          motif, motif_color, motif2_color, name_color=None):
    base = vgrad(c1, c2)
    # 外框圓角 + 中央窗：alpha = 外圓角遮罩 − 窗遮罩
    outer = Image.new("L", (W, H), 0)
    ImageDraw.Draw(outer).rounded_rectangle([0, 0, W - 1, H - 1], radius=58, fill=255)
    hole = Image.new("L", (W, H), 0)
    ImageDraw.Draw(hole).rounded_rectangle(list(WIN), radius=44, fill=255)
    base.putalpha(ImageChops.subtract(outer, hole))

    d = ImageDraw.Draw(base)
    d.rounded_rectangle(list(WIN), radius=44, outline=win_line, width=7)
    d.rounded_rectangle([WIN[0] - 10, WIN[1] - 10, WIN[2] + 10, WIN[3] + 10],
                        radius=54, outline=win_soft, width=3)

    text_c(d, (W // 2, 96), title, font(True, 92), frame_rgb, shadow=(0, 0, 0, 60))
    text_c(d, (W // 2, 178), eyebrow, font(False, 30), win_line)
    text_c(d, (W // 2, H - 128), SCHOOL, font(True, 38), name_color or frame_rgb)
    text_c(d, (W // 2, H - 76), tagline, font(False, 26), win_line)

    cluster = MOTIFS[motif]
    for i, (x, y) in enumerate([(150, 100), (W - 150, 100), (130, H - 110), (W - 130, H - 110)]):
        cluster(d, x, y, motif_color, motif2_color, win_soft, i)

    base.save(os.path.join(OUT, name))
    mx = base.crop((WIN[0] + 40, WIN[1] + 40, WIN[2] - 40, WIN[3] - 40)).split()[3].getextrema()[1]
    print(f"✓ {name}  中央窗 alpha 最大值 = {mx}  (應為 0 = 真透明)")


if __name__ == "__main__":
    # 1) 畢業快樂（暖金）
    build("frame_graduation.png", (255, 249, 232), (246, 214, 146),
          (150, 96, 28), (212, 160, 64), (248, 224, 150),
          "畢業快樂", "2026 GRADUATION · 鳳凰花開", "石門國小 · 智慧拍貼機",
          "star", (230, 176, 70), (248, 210, 120))

    # 2) 鱻魚特色學園（海洋）
    build("frame_ocean.png", (226, 247, 250), (118, 196, 208),
          (20, 92, 110), (255, 255, 255), (200, 240, 246),
          "鱻魚特色學園", "SHIH MEN ELEMENTARY · 海闊天空", "石門國小 · 智慧拍貼機",
          "fish", (255, 156, 90), (255, 120, 70))

    # 3) 歡慶校慶（粉桃 + 氣球）
    build("frame_anniversary.png", (255, 240, 244), (250, 168, 182),
          (172, 44, 78), (255, 255, 255), (255, 212, 222),
          "歡慶校慶", "SCHOOL ANNIVERSARY · 生日快樂", "石門國小 · 智慧拍貼機",
          "balloon", (235, 92, 112), (104, 168, 232))

    # 4) 活力運動會（橙 + 獎牌）
    build("frame_sports.png", (255, 243, 224), (255, 168, 88),
          (188, 86, 18), (255, 255, 255), (255, 222, 184),
          "活力運動會", "SPORTS DAY · 超越自我", "石門國小 · 智慧拍貼機",
          "medal", (245, 188, 70), (216, 70, 58))

    # 5) 歡樂佳節（墨綠 + 雪花）
    build("frame_festival.png", (236, 246, 244), (44, 120, 104),
          (198, 58, 52), (255, 255, 255), (214, 238, 232),
          "歡樂佳節", "HAPPY HOLIDAYS · 佳節愉快", "石門國小 · 智慧拍貼機",
          "snow", (255, 255, 255), (210, 236, 245), name_color=(245, 250, 248))

    # 6) 鱻魚吉祥（亮青 + 大魚吉祥物）
    build("frame_fishmascot.png", (224, 250, 252), (88, 204, 210),
          (14, 108, 120), (255, 178, 92), (255, 226, 200),
          "鱻魚吉祥", "SHIH MEN FISH · 悠游石門", "石門國小 · 智慧拍貼機",
          "fishbig", (255, 150, 90), (255, 112, 72))

    print("\n全部完成 → frames/")
