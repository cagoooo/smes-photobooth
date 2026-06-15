#!/usr/bin/env python3
"""
Generate OG preview + favicon icon set for 石門國小 AI 智慧拍貼機
Run: python tools/gen_og.py
Outputs: og-preview.png (1200×630), favicon.ico, icon-192/512.png, apple-touch-icon.png
"""

import os
import sys
import math
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FONT_BOLD = "C:/Windows/Fonts/msjhbd.ttc"
FONT_REG  = "C:/Windows/Fonts/msjh.ttc"

# ── Brand palette ──────────────────────────────────────────────────────
BG1    = (255, 247, 236)   # #fff7ec warm cream
BG2    = (255, 231, 208)   # #ffe7d0 warm peach
INK    = (58,  42,  24)    # #3a2a18 dark brown
SOFT   = (122, 102, 80)    # #7a6650 muted brown
BRAND  = (224, 138, 60)    # #e08a3c orange
BRAND_D= (198, 111, 35)    # #c66f23 dark orange
ACCENT = (31,  143, 166)   # #1f8fa6 teal
WHITE  = (255, 255, 255)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

# ── Helpers ────────────────────────────────────────────────────────────

def gradient_bg(w, h, c1, c2):
    """Top→bottom linear gradient, c1 at top, c2 at bottom."""
    img = Image.new("RGB", (w, h), c1)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        draw.line([(0, y), (w, y)], fill=lerp(c1, c2, t * 0.65))
    return img

def rounded_rect(draw, x, y, w, h, r, fill):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)

def load_fonts():
    sizes = {}
    pairs = [(FONT_BOLD, [76, 60, 34, 26, 18]), (FONT_REG, [22])]
    result = {}
    for path, szs in pairs:
        for s in szs:
            try:
                result[s] = ImageFont.truetype(path, s)
            except Exception:
                result[s] = ImageFont.load_default()
    return result


# ══════════════════════════════════════════════════════════════════════
#  OG IMAGE  1200×630
# ══════════════════════════════════════════════════════════════════════

def draw_camera_decoration(draw, cx, cy, scale=1.0):
    """Draw camera body + lens + fish tail centered at (cx, cy)."""
    s = scale

    # Fish tail (left of camera)
    tail_pts = [
        (cx - int(130*s), cy),
        (cx - int(200*s), cy - int(60*s)),
        (cx - int(220*s), cy),
        (cx - int(200*s), cy + int(60*s)),
    ]
    draw.polygon(tail_pts, fill=BRAND, outline=INK)

    # Camera body (rounded rect)
    bx = cx - int(110*s)
    bw = int(280*s)
    bh = int(200*s)
    by = cy - int(100*s)
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=int(28*s), fill=INK)

    # Viewfinder bump on top
    vx = cx - int(20*s)
    vw = int(80*s)
    vh = int(30*s)
    draw.rounded_rectangle([vx, by-vh+6, vx+vw, by+8], radius=int(10*s), fill=INK)

    # Flash dot (red)
    fx = cx - int(78*s)
    fy = cy - int(65*s)
    fr = int(14*s)
    draw.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=(210, 85, 63))

    # Lens outer ring (brand orange)
    lr = int(80*s)
    draw.ellipse([cx-lr, cy-lr, cx+lr, cy+lr], fill=BRAND, outline=WHITE, width=int(8*s))
    # Lens inner (teal)
    ir = int(56*s)
    draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], fill=ACCENT, outline=INK, width=int(8*s))
    # Lens highlights
    draw.ellipse([cx-int(24*s), cy-int(24*s), cx+int(2*s), cy+int(2*s)], fill=(255,255,255,180))
    draw.ellipse([cx+int(10*s), cy+int(10*s), cx+int(20*s), cy+int(20*s)], fill=(255,255,255,120))

    # Bubbles (teal outline circles)
    for (bx2, by2, br) in [(cx+120*s, cy-90*s, 16*s), (cx+145*s, cy-130*s, 9*s)]:
        draw.ellipse([bx2-br, by2-br, bx2+br, by2+br], outline=ACCENT, width=int(5*s))

    # Fish fin on top of camera body
    fin = [
        (cx - int(10*s), by),
        (cx + int(15*s), by - int(40*s)),
        (cx + int(40*s), by),
    ]
    draw.polygon(fin, fill=BRAND, outline=INK)


def gen_og():
    W, H = 1200, 630
    fonts = load_fonts()

    # Background
    img = gradient_bg(W, H, BG1, BG2)
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle white radial highlight top-left
    for r in range(280, 0, -10):
        alpha = int((1 - r / 280) * 40)
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.ellipse([-r, -r, r, r], fill=(*WHITE, alpha))
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

    # Right panel warm accent strip
    draw.rounded_rectangle([780, 0, W, H], radius=0, fill=(*lerp(BG1, BRAND, 0.08), 255))

    # Camera decoration (right side)
    draw_camera_decoration(draw, cx=970, cy=315, scale=1.35)

    # ── Left text content ──────────────────────────────────────────────

    # Icon badge top-left
    rounded_rect(draw, 72, 58, 64, 64, 18, (*BRAND, 255))
    # Draw a tiny camera symbol as text emoji substitute
    cam_f = None
    try:
        cam_f = ImageFont.truetype(FONT_BOLD, 36)
    except Exception:
        cam_f = ImageFont.load_default()
    draw.text((78, 66), "📷", font=cam_f, fill=WHITE)

    # Title (split into two lines for readability)
    title1 = "石門國小"
    title2 = "AI 智慧拍貼機"

    try:
        f76 = ImageFont.truetype(FONT_BOLD, 76)
        f60 = ImageFont.truetype(FONT_BOLD, 60)
        f34 = ImageFont.truetype(FONT_BOLD, 34)
        f26 = ImageFont.truetype(FONT_BOLD, 26)
        f22 = ImageFont.truetype(FONT_REG, 22)
        f18 = ImageFont.truetype(FONT_BOLD, 18)
    except Exception:
        f76 = f60 = f34 = f26 = f22 = f18 = ImageFont.load_default()

    draw.text((72, 152), title1, font=f76, fill=INK)
    draw.text((72, 244), title2, font=f60, fill=INK)

    # Orange divider line
    draw.rectangle([72, 326, 360, 332], fill=(*BRAND, 255))

    # School name
    draw.text((72, 346), "桃園市龍潭區石門國民小學 · 鱻魚特色學園", font=f26, fill=(*BRAND, 255))

    # Description lines
    desc1 = "✦ 手勢倒數自拍  ✦ 一鍵換邊框  ✦ 雲端相簿即時上傳"
    desc2 = "✦ 掃 QR Code 下載照片  ✦ 相片編輯工坊  ✦ 連拍 3 選 1"
    draw.text((72, 396), desc1, font=f22, fill=SOFT)
    draw.text((72, 426), desc2, font=f22, fill=SOFT)

    # URL capsule
    url_text = "cagoooo.github.io/smes-photobooth  →"
    capsule_w = 490
    rounded_rect(draw, 72, 496, capsule_w, 52, 26, (*INK, 255))
    draw.text((106, 511), url_text, font=f18, fill=WHITE)

    # School badge / tag bottom-right of left section
    badge_text = "📸 智慧拍貼機"
    rounded_rect(draw, 72, 568, 200, 38, 19, (*BRAND, 50))
    draw.text((92, 576), badge_text, font=f22, fill=(*BRAND_D, 255))

    # Save
    out = os.path.join(ROOT, "og-preview.png")
    img.save(out, "PNG", optimize=True, compress_level=7)
    kb = os.path.getsize(out) / 1024
    print(f"[OK] og-preview.png  {kb:.0f} KB  ({W}x{H})")
    return True


# ══════════════════════════════════════════════════════════════════════
#  FAVICON / APP ICONS  (draw camera-fish icon with PIL)
# ══════════════════════════════════════════════════════════════════════

def draw_icon(size, maskable=False):
    """Draw the camera-fish icon at given pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    s = size / 512  # scale factor relative to 512px reference

    if maskable:
        # Maskable: solid background fills the whole canvas
        draw.rectangle([0, 0, size, size], fill=(*BG1, 255))
        # Main content in 60% safe zone
        offset = int(size * 0.20)
        sub = draw_icon_content(size - 2 * offset, maskable=False)
        img.paste(sub, (offset, offset), sub)
    else:
        # Regular icon: rounded-rect background
        r = int(size * 0.25)
        draw.rounded_rectangle([0, 0, size, size], radius=r, fill=(*BG1, 255),
                                outline=(*BRAND, 255), width=max(1, int(size * 0.03)))
        # Draw camera content
        content = draw_icon_content(size, maskable=False)
        img = Image.alpha_composite(img, content)

    return img


def draw_icon_content(size, maskable=False):
    """Draw camera + fish on transparent canvas of given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    s = size / 512
    cx = int(size * 0.58)
    cy = int(size * 0.54)

    # Fish tail (left)
    tail = [
        (int(cx - 120*s), cy),
        (int(cx - 175*s), int(cy - 56*s)),
        (int(cx - 195*s), cy),
        (int(cx - 175*s), int(cy + 56*s)),
    ]
    draw.polygon(tail, fill=(*BRAND, 255), outline=(*INK, 255))

    # Inner tail highlight
    inner_tail = [
        (int(cx - 128*s), cy),
        (int(cx - 165*s), int(cy - 36*s)),
        (int(cx - 180*s), cy),
        (int(cx - 165*s), int(cy + 36*s)),
    ]
    draw.polygon(inner_tail, fill=(*BG2, 200))

    # Camera body
    bx = int(cx - 105*s)
    by = int(cy - 100*s)
    bw = int(270*s)
    bh = int(200*s)
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=int(28*s), fill=(*INK, 255))

    # Viewfinder bump
    vx = int(cx - 18*s)
    vw = int(72*s)
    vh = int(28*s)
    draw.rounded_rectangle([vx, by-vh+6, vx+vw, by+8], radius=int(10*s), fill=(*INK, 255))

    # Flash dot
    fr = int(13*s)
    fx = int(cx - 74*s)
    fy = int(cy - 63*s)
    draw.ellipse([fx-fr, fy-fr, fx+fr, fy+fr], fill=(210, 85, 63, 255))

    # Lens outer (orange)
    lr = int(80*s)
    draw.ellipse([cx-lr, cy-lr, cx+lr, cy+lr], fill=(*BRAND, 255),
                 outline=(*WHITE, 255), width=max(1, int(10*s)))
    # Lens inner (teal)
    ir = int(56*s)
    draw.ellipse([cx-ir, cy-ir, cx+ir, cy+ir], fill=(*ACCENT, 255),
                 outline=(*INK, 255), width=max(1, int(10*s)))
    # Lens highlights
    hs = int(18*s)
    draw.ellipse([cx-hs*2, cy-hs*2, cx, cy], fill=(255,255,255,160))
    draw.ellipse([cx+int(8*s), cy+int(8*s), cx+int(16*s), cy+int(16*s)],
                 fill=(255,255,255,100))

    # Fish fin on top
    fin = [(int(cx-8*s), by), (int(cx+14*s), int(by-38*s)), (int(cx+38*s), by)]
    draw.polygon(fin, fill=(*BRAND, 255), outline=(*INK, 255))

    # Bubbles (only at larger sizes)
    if size >= 64:
        for (bxb, byb, br) in [(int(cx+108*s), int(cy-78*s), int(13*s)),
                                (int(cx+134*s), int(cy-118*s), int(8*s))]:
            draw.ellipse([bxb-br, byb-br, bxb+br, byb+br],
                         outline=(*ACCENT, 255), width=max(1, int(5*s)))

    return img


def gen_icons():
    configs = [
        ("apple-touch-icon.png", 180, False),
        ("icon-192.png",         192, False),
        ("icon-512.png",         512, False),
        ("icon-192-maskable.png",192, True),
        ("icon-512-maskable.png",512, True),
    ]
    for fname, sz, mask in configs:
        out = os.path.join(ROOT, fname)
        img = draw_icon(sz, maskable=mask)
        img.save(out, "PNG", optimize=True)
        kb = os.path.getsize(out) / 1024
        print(f"[OK] {fname:<28} {sz}x{sz}  {kb:.0f} KB")

    # favicon.ico — render at 256px then let PIL resize to all sizes
    ico_base = draw_icon(256, maskable=False).convert("RGBA")
    ico_path = os.path.join(ROOT, "favicon.ico")
    ico_base.save(
        ico_path, format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (256, 256)]
    )
    kb = os.path.getsize(ico_path) / 1024
    print(f"[OK] favicon.ico               multi-size  {kb:.1f} KB")


if __name__ == "__main__":
    print("=== smes-photobooth: Generate OG + Icons ===\n")
    try:
        gen_og()
        gen_icons()
        print("\n[DONE] All assets generated. Ready to commit & push.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        sys.exit(1)
