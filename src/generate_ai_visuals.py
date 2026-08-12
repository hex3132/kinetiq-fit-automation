import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

FONT_PATH_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_PATH_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

THEME_COLORS = {
    "Coach Aria": {"top": (255, 138, 158), "bottom": (255, 200, 150)},
    "Coach Kai": {"top": (60, 60, 80), "bottom": (30, 30, 45)},
}


def _gradient_background(width, height, top_color, bottom_color):
    base = Image.new("RGB", (width, height), top_color)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return base


def _wrap_text(text, width_chars=22):
    return "\n".join(textwrap.wrap(text, width=width_chars))


def _make_card(width, height, character_name, segment_text, segment_index, out_path):
    theme = THEME_COLORS.get(character_name, THEME_COLORS["Coach Aria"])
    img = _gradient_background(width, height, theme["top"], theme["bottom"])
    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype(FONT_PATH_BOLD, 64)
        font_body = ImageFont.truetype(FONT_PATH_REGULAR, 44)
        font_badge = ImageFont.truetype(FONT_PATH_BOLD, 36)
    except Exception:
        font_title = font_body = font_badge = ImageFont.load_default()

    # Character name badge, top of frame
    draw.text((60, 80), character_name, font=font_title, fill=(255, 255, 255))

    # Segment counter badge
    draw.text((60, 160), f"Segment {segment_index + 1}", font=font_badge, fill=(255, 255, 255, 200))

    # Main wrapped text, centered vertically
    wrapped = _wrap_text(segment_text, width_chars=24)
    lines = wrapped.split("\n")
    line_height = 60
    total_h = line_height * len(lines)
    start_y = (height - total_h) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font_body)
        line_w = bbox[2] - bbox[0]
        x = (width - line_w) // 2
        y = start_y + i * line_height
        draw.text((x, y), line, font=font_body, fill=(255, 255, 255))

    img.save(out_path, "JPEG", quality=90)
    return out_path


def generate_ai_visuals(script, config, character, out_dir="output/images"):
    os.makedirs(out_dir, exist_ok=True)
    v = config["video"]
    width, height = v["frame_width"], v["frame_height"]

    paths = []
    for i, seg in enumerate(script["segments"]):
        out_path = os.path.join(out_dir, f"segment_{i:02d}.jpg")
        _make_card(width, height, character["display_name"], seg["visual"], i, out_path)
        print(f"[generate_ai_visuals] segment {i} -> {out_path}")
        paths.append(out_path)

    return paths
