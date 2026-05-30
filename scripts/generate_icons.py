"""
Generate PWA icons for RoadSoS — minimal red square with white SOS text
and a small dot indicating "emergency". Runs offline via Pillow.

Outputs to static/icons/:
  icon-192.png            — standard 192x192 (any purpose)
  icon-512.png            — standard 512x512 (any purpose)
  icon-maskable-512.png   — 512x512 with safe zone padding (maskable purpose)
  favicon.png             — 32x32 browser tab icon
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "static/icons"
os.makedirs(OUT_DIR, exist_ok=True)

# RoadSoS brand colours
RED  = (220, 38, 38)        # #DC2626
RED2 = (153, 27, 27)        # #991B1B (deeper, for gradient)
WHITE = (255, 255, 255)
SAFE_ZONE_PAD = 0.10        # maskable purpose: 10% padding so the icon
                            # survives Android's circle/squircle masking


def _load_font(size):
    """Try several common fonts. Fall back to PIL default if none found."""
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def draw_icon(size: int, maskable: bool = False, save_to: str = ""):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background — rounded square (or full square for maskable, since the
    # platform masks the corners anyway)
    pad = int(size * SAFE_ZONE_PAD) if maskable else 0
    inner = size - 2 * pad
    radius = int(inner * 0.18) if not maskable else int(inner * 0.05)

    # Solid background — keep it simple and recognisable
    d.rounded_rectangle(
        [pad, pad, pad + inner - 1, pad + inner - 1],
        radius=radius, fill=RED,
    )

    # White "SOS" text, centred
    text = "SOS"
    font_size = int(inner * 0.42)
    font = _load_font(font_size)
    # Pillow ≥10 uses textbbox
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = pad + (inner - tw) / 2 - bbox[0]
    ty = pad + (inner - th) / 2 - bbox[1] - int(inner * 0.06)
    d.text((tx, ty), text, fill=WHITE, font=font)

    # Subtitle "RoadSoS" mini-text below — skip for very small icons
    if inner < 100:
        img.save(save_to, "PNG", optimize=True)
        print(f"  wrote {save_to}  ({size}x{size}{' maskable' if maskable else ''})")
        return
    sub = "RoadSoS"
    sub_size = max(8, int(inner * 0.13))
    sub_font = _load_font(sub_size)
    sbox = d.textbbox((0, 0), sub, font=sub_font)
    sw = sbox[2] - sbox[0]
    sh = sbox[3] - sbox[1]
    sx = pad + (inner - sw) / 2 - sbox[0]
    sy = pad + inner * 0.72 - sbox[1]
    d.text((sx, sy), sub, fill=WHITE, font=sub_font)

    # Small red dot as accent (the "emergency pulse")
    dot_r = int(inner * 0.04)
    dot_cx = pad + inner - int(inner * 0.20)
    dot_cy = pad + int(inner * 0.20)
    d.ellipse(
        [dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r],
        fill=WHITE,
    )

    img.save(save_to, "PNG", optimize=True)
    print(f"  wrote {save_to}  ({size}x{size}{' maskable' if maskable else ''})")


if __name__ == "__main__":
    draw_icon(192, False, f"{OUT_DIR}/icon-192.png")
    draw_icon(512, False, f"{OUT_DIR}/icon-512.png")
    draw_icon(512, True,  f"{OUT_DIR}/icon-maskable-512.png")
    draw_icon(32,  False, f"{OUT_DIR}/favicon.png")
    print("Done. Replace these with your team's logo any time.")
