# -*- coding: utf-8 -*-
"""四格拍貼成品示意圖：模擬 index.html shootGrid 的合成（4 格拼進邊框窗 + 白間隙 + 疊框）。"""
import os
from PIL import Image, ImageDraw

FR = os.path.join(os.path.dirname(__file__), "..", "frames")
OUT = os.path.join(os.path.dirname(__file__), "..", "previews")
os.makedirs(OUT, exist_ok=True)

WIN = (70, 215, 1010, 1235)   # 與 index.html CONFIG.frameWindow / make_frames.py WIN 一致
GAP = 16


def cell_photo(w, h, sky, sil):
    """單格示意「照片」：漸層背景 + 人物剪影。"""
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(sky[0][i] + (sky[1][i] - sky[0][i]) * t) for i in range(3)))
    cx, hy, hr = w // 2, int(h * 0.42), int(w * 0.20)
    d.ellipse([cx - hr, hy - hr, cx + hr, hy + hr], fill=sil)                      # 頭
    bw = int(w * 0.34)
    d.rounded_rectangle([cx - bw, hy + hr - 6, cx + bw, h], radius=int(bw * .5), fill=sil)  # 身
    return im


def build(frame_name, out_name):
    frame = Image.open(os.path.join(FR, frame_name)).convert("RGBA")
    W, H = frame.size
    canvas = Image.new("RGB", (W, H), (255, 255, 255))     # 白底＝格子間隙
    cw, ch = (WIN[2] - WIN[0]) // 2, (WIN[3] - WIN[1]) // 2
    skies = [((255, 244, 222), (250, 210, 150)), ((226, 247, 250), (130, 200, 212)),
             ((255, 240, 244), (250, 175, 188)), ((232, 248, 240), (150, 210, 170))]
    sils = [(70, 80, 100), (60, 90, 95), (95, 70, 85), (70, 95, 80)]
    pos = [(WIN[0], WIN[1]), (WIN[0] + cw, WIN[1]), (WIN[0], WIN[1] + ch), (WIN[0] + cw, WIN[1] + ch)]
    for i in range(4):
        cell = cell_photo(cw - GAP, ch - GAP, skies[i], sils[i])
        canvas.paste(cell, (pos[i][0] + GAP // 2, pos[i][1] + GAP // 2))
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(frame)
    canvas.convert("RGB").save(os.path.join(OUT, out_name), quality=90)
    print("✓", out_name)


if __name__ == "__main__":
    build("frame_graduation.png", "preview_4grid.jpg")
    print("完成 → previews/")
