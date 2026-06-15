# -*- coding: utf-8 -*-
"""產出「拍貼成品示意圖」：在邊框透明窗後面合成簡單人像剪影，看實際拍出來效果。"""
import os
from PIL import Image, ImageDraw, ImageFilter

FR = os.path.join(os.path.dirname(__file__), "..", "frames")
OUT = os.path.join(os.path.dirname(__file__), "..", "previews")
os.makedirs(OUT, exist_ok=True)


def people_bg(W, H, sky):
    """背景：暖色漸層 + 兩個卡通剪影（模擬站在拍貼機前的人）。"""
    base = Image.new("RGB", (W, H))
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(sky[0][i] + (sky[1][i] - sky[0][i]) * t) for i in range(3))
        ImageDraw.Draw(base).line([(0, y), (W, y)], fill=c)
    d = ImageDraw.Draw(base)
    sil = (60, 70, 90)
    for cx, scale in [(int(W * 0.36), 1.0), (int(W * 0.64), 0.92)]:
        hy = int(H * 0.42)
        hr = int(W * 0.12 * scale)
        d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=sil)            # 頭
        bw = int(W * 0.22 * scale)
        d.rounded_rectangle([cx - bw, hy + hr - 6, cx + bw, H],
                            radius=int(bw * 0.5), fill=sil)                   # 身體
    return base


def build(frame_name, out_name, sky):
    frame = Image.open(os.path.join(FR, frame_name)).convert("RGBA")
    W, H = frame.size
    bg = people_bg(W, H, sky).convert("RGBA")
    bg.alpha_composite(frame)                 # 邊框疊上去，透明窗露出剪影
    bg.convert("RGB").save(os.path.join(OUT, out_name), quality=90)
    print("✓", out_name)


if __name__ == "__main__":
    build("frame_graduation.png", "preview_graduation.jpg",
          ((255, 244, 222), (250, 210, 150)))
    build("frame_ocean.png", "preview_ocean.jpg",
          ((215, 240, 246), (130, 195, 210)))
    print("完成 → previews/")
