import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

def make_circle_mask(size):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    return mask

def make_rounded_mask(size, radius):
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + size, radius, fill=255)
    return mask

def process_favicon(logo_path, output_dir):
    print(f"Loading logo base: {logo_path}")
    logo = Image.open(logo_path).convert("RGBA")
    
    # Crop to square if it's not square
    w, h = logo.size
    min_dim = min(w, h)
    logo_square = logo.crop(((w - min_dim) // 2, (h - min_dim) // 2, (w + min_dim) // 2, (h + min_dim) // 2))
    
    # Generate PWA App Icons (Square/Circular)
    sizes = [192, 512, 180]
    icons = {}
    for sz in sizes:
        img_resized = logo_square.resize((sz, sz), Image.Resampling.LANCZOS)
        icons[sz] = img_resized
    
    # 1. apple-touch-icon.png (180x180, often rounded by OS but stored as square)
    icons[180].save(os.path.join(output_dir, "apple-touch-icon.png"), "PNG")
    print("Saved apple-touch-icon.png (180x180)")
    
    # 2. icon-192.png and icon-512.png
    icons[192].save(os.path.join(output_dir, "icon-192.png"), "PNG")
    icons[512].save(os.path.join(output_dir, "icon-512.png"), "PNG")
    print("Saved icon-192.png and icon-512.png")
    
    # 3. PWA Maskable Icons (Must have solid background, 60% safe zone)
    # Background color: Warm cream #fff7ec
    bg_color = (255, 247, 236, 255)
    for sz in [192, 512]:
        maskable = Image.new("RGBA", (sz, sz), bg_color)
        logo_sz = int(sz * 0.6)
        logo_resized = logo_square.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
        # Paste centered
        offset = (sz - logo_sz) // 2
        maskable.paste(logo_resized, (offset, offset), logo_resized)
        maskable.save(os.path.join(output_dir, f"icon-{sz}-maskable.png"), "PNG")
        print(f"Saved icon-{sz}-maskable.png")
        
    # 4. favicon.ico (multi-size: 16x16, 32x32, 48x48)
    ico_img = logo_square.resize((256, 256), Image.Resampling.LANCZOS)
    ico_img.save(
        os.path.join(output_dir, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)]
    )
    print("Saved favicon.ico (multi-size)")
    
    return logo_square

def draw_round_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)

def process_og_image(bg_path, logo_square, output_dir):
    print(f"Loading OG background base: {bg_path}")
    bg = Image.open(bg_path).convert("RGBA")
    
    # Scale to standard OG size: 1200x630
    bg_resized = bg.resize((1200, 630), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(bg_resized)
    
    # Load Font
    font_bold_path = "C:/Windows/Fonts/msjhbd.ttc"
    font_reg_path = "C:/Windows/Fonts/msjh.ttc"
    
    # Fallback to default if not exists
    if not os.path.exists(font_bold_path):
        font_bold_path = "arial.ttf"
    if not os.path.exists(font_reg_path):
        font_reg_path = "arial.ttf"
        
    try:
        font_title = ImageFont.truetype(font_bold_path, 62)
        font_sub = ImageFont.truetype(font_bold_path, 28)
        font_desc = ImageFont.truetype(font_reg_path, 22)
        font_url = ImageFont.truetype(font_bold_path, 18)
    except IOError:
        print("Warning: Fonts not found, using default.")
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_desc = ImageFont.load_default()
        font_url = ImageFont.load_default()
        
    # Colors
    color_ink = (58, 42, 24, 255)       # #3a2a18
    color_ink_soft = (122, 102, 80, 255) # #7a6650
    color_brand = (224, 138, 60, 255)   # #e08a3c
    
    # 1. Draw Title
    draw.text((80, 160), "石門國小 AI 智慧拍貼機 📸", font=font_title, fill=color_ink)
    
    # 2. Draw Subtitle
    draw.text((80, 255), "桃園市龍潭區石門國民小學 · 鱻魚特色學園", font=font_sub, fill=color_brand)
    
    # 3. Draw Description
    draw.text((80, 315), "手勢倒數自拍、可換邊框、雲端上傳、掃 QR Code 立刻下載照片！", font=font_desc, fill=color_ink_soft)
    draw.text((80, 350), "純靜態網頁與 Google 雲端相簿整合，最便利的校園活動拍照神器。", font=font_desc, fill=color_ink_soft)
    
    # 4. Draw URL capsule (cagoooo.github.io/smes-photobooth/)
    # Background capsule: #3a2a18
    capsule_x = 80
    capsule_y = 440
    capsule_w = 460
    capsule_h = 50
    draw_round_rect(draw, [capsule_x, capsule_y, capsule_x + capsule_w, capsule_y + capsule_h], radius=25, fill=color_ink)
    
    # Draw URL text in White
    draw.text((capsule_x + 30, capsule_y + 13), "cagoooo.github.io/smes-photobooth →", font=font_url, fill=(255, 255, 255, 255))
    
    # 5. Place Circular Logo on the right side
    logo_sz = 260
    logo_res = logo_square.resize((logo_sz, logo_sz), Image.Resampling.LANCZOS)
    
    # Mask to circular
    mask = make_circle_mask((logo_sz, logo_sz))
    
    # Paste logo at right (X=840, Y=160)
    bg_resized.paste(logo_res, (840, 160), mask=mask)
    
    # Save the OG preview
    bg_resized.save(os.path.join(output_dir, "og-preview.png"), "PNG")
    print("Saved og-preview.png (1200x630)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python generate_assets.py <logo_base_path> <og_bg_path>")
        sys.exit(1)
        
    logo_path = sys.argv[1]
    bg_path = sys.argv[2]
    
    output_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    logo_square = process_favicon(logo_path, output_dir)
    process_og_image(bg_path, logo_square, output_dir)
    print("All assets generated successfully!")
