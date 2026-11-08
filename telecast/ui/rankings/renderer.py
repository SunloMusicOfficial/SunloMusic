# Copyright (C) @itsSmartDev

from __future__ import annotations

import math
import os
import random
from pathlib import Path

import io

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

try:
    import numpy as _np
except Exception:
    _np = None


W, H = 1536, 1024
MARGIN = 30
GAP = 22

FONT_CANDIDATES = {
    "display_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansDisplay-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "display_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans_regular": [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "bn_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "bn_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansBengali-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "deva_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "deva_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "guru_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGurmukhi-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "guru_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGurmukhi-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "gujr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGujarati-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "gujr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGujarati-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "orya_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansOriya-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "orya_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansOriya-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "taml_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "taml_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansTamil-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "telu_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansTelugu-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "telu_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansTelugu-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "knda_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "knda_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansKannada-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mlym_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mlym_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sinh_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansSinhala-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "sinh_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansSinhala-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "thai_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "thai_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansThai-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "lao_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansLao-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "lao_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansLao-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "mymr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mymr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansMyanmar-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "khmr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansKhmer-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "khmr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansKhmer-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "arab_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "arab_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "hebr_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "hebr_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansHebrew-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "armn_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansArmenian-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "armn_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansArmenian-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "geor_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "geor_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansGeorgian-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "ethi_regular": [
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "ethi_bold": [
        "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "cjk": [
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "mono": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ],
    "emoji": [
        "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "old_italic": [
        "/usr/share/fonts/truetype/noto/NotoSansOldItalic-Regular.ttf",
        "/usr/share/fonts/truetype/unifont/unifont.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "math_fraktur": [
        "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "math_sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    "symbol": [
        "/usr/share/fonts/truetype/unifont/unifont.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansSymbols2-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}

_BUNDLED_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "fonts")


def _with_bundled(candidates: list[str]) -> list[str]:
    out: list[str] = []
    for path in candidates:
        bundled = os.path.join(_BUNDLED_FONT_DIR, os.path.basename(path))
        out.append(bundled)
        out.append(path)
    return out


FONT_CANDIDATES = {name: _with_bundled(paths) for name, paths in FONT_CANDIDATES.items()}

PALETTE = {
    "bg0": (5, 8, 22),
    "bg1": (12, 16, 34),
    "card": (10, 15, 31),
    "card2": (15, 21, 42),
    "muted": (151, 163, 184),
    "text": (244, 247, 251),
    "line": (79, 93, 124),
    "violet": (139, 92, 246),
    "cyan": (34, 211, 238),
    "pink": (236, 72, 153),
    "green": (74, 222, 128),
    "gold": (245, 196, 81),
    "silver": (203, 213, 225),
    "bronze": (217, 119, 87),
}


def font_path(name: str) -> str:
    for path in FONT_CANDIDATES[name]:
        if Path(path).exists():
            return path
    for fallback in (
        os.path.join(_BUNDLED_FONT_DIR, "DejaVuSans.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(fallback).exists():
            return fallback
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


_font_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def f(name: str, size: int) -> ImageFont.FreeTypeFont:
    key = (name, size)
    font = _font_cache.get(key)
    if font is None:
        font = ImageFont.truetype(font_path(name), size=size, layout_engine=ImageFont.Layout.RAQM)
        _font_cache[key] = font
    return font


def bbox(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


SCRIPT_RANGES = {
    "armn": [(0x0530, 0x058F)],
    "hebr": [(0x0590, 0x05FF)],
    "arab": [(0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF), (0xFB50, 0xFDFF), (0xFE70, 0xFEFF)],
    "deva": [(0x0900, 0x097F)],
    "bn": [(0x0980, 0x09FF)],
    "guru": [(0x0A00, 0x0A7F)],
    "gujr": [(0x0A80, 0x0AFF)],
    "orya": [(0x0B00, 0x0B7F)],
    "taml": [(0x0B80, 0x0BFF)],
    "telu": [(0x0C00, 0x0C7F)],
    "knda": [(0x0C80, 0x0CFF)],
    "mlym": [(0x0D00, 0x0D7F)],
    "sinh": [(0x0D80, 0x0DFF)],
    "thai": [(0x0E00, 0x0E7F)],
    "lao": [(0x0E80, 0x0EFF)],
    "mymr": [(0x1000, 0x109F), (0xAA60, 0xAA7F)],
    "geor": [(0x10A0, 0x10FF)],
    "ethi": [(0x1200, 0x137F), (0x1380, 0x139F), (0x2D80, 0x2DDF), (0xAB00, 0xAB2F)],
    "khmr": [(0x1780, 0x17FF), (0x19E0, 0x19FF)],
    "cjk": [
        (0x2E80, 0x303F), (0x3040, 0x30FF), (0x31F0, 0x31FF),
        (0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xAC00, 0xD7AF),
        (0x1100, 0x11FF), (0x3130, 0x318F), (0xF900, 0xFAFF), (0xFF00, 0xFFEF),
    ],
}


SCRIPT_FONTS = {
    "armn": ("armn_regular", "armn_bold"),
    "hebr": ("hebr_regular", "hebr_bold"),
    "arab": ("arab_regular", "arab_bold"),
    "deva": ("deva_regular", "deva_bold"),
    "bn": ("bn_regular", "bn_bold"),
    "guru": ("guru_regular", "guru_bold"),
    "gujr": ("gujr_regular", "gujr_bold"),
    "orya": ("orya_regular", "orya_bold"),
    "taml": ("taml_regular", "taml_bold"),
    "telu": ("telu_regular", "telu_bold"),
    "knda": ("knda_regular", "knda_bold"),
    "mlym": ("mlym_regular", "mlym_bold"),
    "sinh": ("sinh_regular", "sinh_bold"),
    "thai": ("thai_regular", "thai_bold"),
    "lao": ("lao_regular", "lao_bold"),
    "mymr": ("mymr_regular", "mymr_bold"),
    "geor": ("geor_regular", "geor_bold"),
    "ethi": ("ethi_regular", "ethi_bold"),
    "khmr": ("khmr_regular", "khmr_bold"),
    "cjk": ("cjk", "cjk"),
}


def script_of(ch: str) -> str | None:
    cp = ord(ch)
    for kind, ranges in SCRIPT_RANGES.items():
        for lo, hi in ranges:
            if lo <= cp <= hi:
                return kind
    return None


def is_emoji_char(ch: str) -> bool:
    cp = ord(ch)
    return 0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or 0x1F1E6 <= cp <= 0x1F1FF or ch in {"♾", "∞"}


def run_type(ch: str) -> str:
    cp = ord(ch)
    if ch in {"\ufe0f", "\u200d"} or is_emoji_char(ch):
        return "emoji"
    if 0x10300 <= cp <= 0x1032F:
        return "old_italic"
    if 0x1D56C <= cp <= 0x1D59F:
        return "math_fraktur"
    if 0x1D400 <= cp <= 0x1D7FF:
        return "math_sans"
    if 0x2300 <= cp <= 0x23FF:
        return "symbol"
    s = script_of(ch)
    if s is not None:
        return s
    return "latin"


def split_runs(text: str) -> list[tuple[str, str]]:
    runs: list[tuple[str, str]] = []
    cur = ""
    cur_type = ""
    for ch in text:
        typ = run_type(ch)
        if typ == "emoji" and ch in {"\ufe0f", "\u200d"} and cur:
            cur += ch
            continue
        if cur and typ != cur_type:
            runs.append((cur, cur_type))
            cur = ch
        else:
            cur += ch
        cur_type = typ
    if cur:
        runs.append((cur, cur_type))
    return runs


def text_font(kind: str, size: int, weight: str) -> ImageFont.FreeTypeFont:
    if kind in SCRIPT_FONTS:
        regular, bold = SCRIPT_FONTS[kind]
        return f(bold if weight == "bold" else regular, size)
    if kind in {"old_italic", "math_fraktur", "math_sans", "symbol"}:
        return f(kind, size)
    return f("sans_bold" if weight == "bold" else "sans_regular", size)


def emoji_image(text: str, target_h: int) -> Image.Image | None:
    try:
        emoji_font = f("emoji", 109)
        temp = Image.new("RGBA", (220, 180), (0, 0, 0, 0))
        td = ImageDraw.Draw(temp)
        td.text((6, 8), text, font=emoji_font, embedded_color=True)
        box = temp.getbbox()
        if not box:
            return None
        crop = temp.crop(box)
        scale = target_h / max(1, crop.height)
        return crop.resize((max(1, int(crop.width * scale)), target_h), Image.Resampling.LANCZOS)
    except Exception:
        return None


def measure_mixed(draw: ImageDraw.ImageDraw, text: str, size: int, weight: str = "regular") -> tuple[int, int]:
    width = 0
    height = 0
    for run, kind in split_runs(text):
        if kind == "emoji":
            img = emoji_image(run, int(size * 1.05))
            w, h = (img.width, img.height) if img else (size, size)
        else:
            w, h = bbox(draw, run, text_font(kind, size, weight))
        width += w
        height = max(height, h)
    return width, height


def ellipsize(draw: ImageDraw.ImageDraw, text: str, size: int, weight: str, max_w: int) -> str:
    if measure_mixed(draw, text, size, weight)[0] <= max_w:
        return text
    out = text.rstrip()
    while out and measure_mixed(draw, out + "…", size, weight)[0] > max_w:
        out = out[:-1].rstrip()
    return out + "…" if out else "…"


def draw_mixed(base: Image.Image, xy: tuple[int, int], text: str, size: int, fill, weight: str = "regular", max_width: int | None = None):
    draw = ImageDraw.Draw(base, "RGBA")
    if max_width:
        text = ellipsize(draw, text, size, weight, max_width)
    tw, th = measure_mixed(draw, text, size, weight)
    x, y = xy
    cursor = x
    for run, kind in split_runs(text):
        if kind == "emoji":
            img = emoji_image(run, int(size * 1.05))
            if img:
                base.alpha_composite(img, (int(cursor), int(y + (th - img.height) / 2)))
                cursor += img.width
            else:
                ft = text_font("latin", size, weight)
                draw.text((cursor, y), "□", font=ft, fill=fill)
                cursor += bbox(draw, "□", ft)[0]
        else:
            ft = text_font(kind, size, weight)
            draw.text((cursor, y), run, font=ft, fill=fill)
            cursor += bbox(draw, run, ft)[0]


def fit_plain_font(draw: ImageDraw.ImageDraw, font_name: str, text: str, start_size: int, max_w: int) -> ImageFont.FreeTypeFont:
    size = start_size
    while size > 18:
        ft = f(font_name, size)
        if bbox(draw, text, ft)[0] <= max_w:
            return ft
        size -= 1
    return f(font_name, size)


def rounded_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), radius, fill=255)
    return mask


def shadowed_round_rect(base: Image.Image, rect: tuple[int, int, int, int], radius: int, fill, outline, shadow=(0, 0, 0, 130), blur: int = 18, offset=(0, 12)):
    x0, y0, x1, y1 = rect
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer, "RGBA")
    sd.rounded_rectangle((x0 + offset[0], y0 + offset[1], x1 + offset[0], y1 + offset[1]), radius, fill=shadow)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))
    shape = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sh = ImageDraw.Draw(shape, "RGBA")
    sh.rounded_rectangle(rect, radius, fill=fill, outline=outline, width=1)
    base.alpha_composite(shape)


def overlay_round_rect(base: Image.Image, rect: tuple[int, int, int, int], radius: int, fill=None, outline=None, width: int = 1):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer, "RGBA")
    ld.rounded_rectangle(rect, radius, fill=fill, outline=outline, width=width)
    base.alpha_composite(layer)


def gradient_rect(base: Image.Image, rect: tuple[int, int, int, int], c1, c2, radius: int, alpha: int = 255):
    x0, y0, x1, y1 = rect
    ww, hh = x1 - x0, y1 - y0
    grad = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
    gp = grad.load()
    for x in range(ww):
        t = x / max(1, ww - 1)
        col = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
        for y in range(hh):
            gp[x, y] = (*col, alpha)
    mask = rounded_mask((ww, hh), radius).point(lambda p: int(p * alpha / 255))
    grad.putalpha(mask)
    base.alpha_composite(grad, (x0, y0))


def icon_people(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.36, y + s * 0.08, x + s * 0.64, y + s * 0.36), fill=col)
    d.rounded_rectangle((x + s * 0.23, y + s * 0.42, x + s * 0.77, y + s * 0.83), int(s * 0.16), fill=col)
    d.ellipse((x + s * 0.12, y + s * 0.20, x + s * 0.34, y + s * 0.42), fill=col)
    d.ellipse((x + s * 0.66, y + s * 0.20, x + s * 0.88, y + s * 0.42), fill=col)
    d.rounded_rectangle((x + s * 0.05, y + s * 0.48, x + s * 0.36, y + s * 0.78), int(s * 0.12), fill=col)
    d.rounded_rectangle((x + s * 0.64, y + s * 0.48, x + s * 0.95, y + s * 0.78), int(s * 0.12), fill=col)


def icon_user(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.31, y + s * 0.08, x + s * 0.69, y + s * 0.46), fill=col)
    d.rounded_rectangle((x + s * 0.18, y + s * 0.53, x + s * 0.82, y + s * 0.90), int(s * 0.18), fill=col)


def icon_note(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x + s * 0.10, y + s * 0.62, x + s * 0.40, y + s * 0.92), fill=col)
    d.rectangle((x + s * 0.34, y + s * 0.13, x + s * 0.44, y + s * 0.72), fill=col)
    d.polygon([(x + s * 0.43, y + s * 0.13), (x + s * 0.86, y + s * 0.04), (x + s * 0.86, y + s * 0.23), (x + s * 0.43, y + s * 0.32)], fill=col)


def icon_clock(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x, y, x + s, y + s), outline=col, width=max(3, s // 13))
    d.line((x + s / 2, y + s / 2, x + s / 2, y + s * 0.25), fill=col, width=max(3, s // 17))
    d.line((x + s / 2, y + s / 2, x + s * 0.70, y + s * 0.62), fill=col, width=max(3, s // 17))


def draw_icon(d: ImageDraw.ImageDraw, kind: str, x: int, y: int, s: int, col):
    if kind == "group":
        icon_people(d, x, y, s, col)
    elif kind == "user":
        icon_user(d, x, y, s, col)
    elif kind == "clock":
        icon_clock(d, x, y, s, col)
    else:
        icon_note(d, x, y, s, col)


def draw_crown(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.polygon([(x, y + s * 0.76), (x + s * 0.15, y + s * 0.34), (x + s * 0.39, y + s * 0.58), (x + s * 0.50, y + s * 0.18), (x + s * 0.61, y + s * 0.58), (x + s * 0.85, y + s * 0.34), (x + s, y + s * 0.76)], fill=col)
    d.rounded_rectangle((x + s * 0.08, y + s * 0.72, x + s * 0.92, y + s * 0.88), 2, fill=col)



NAVY = (6, 10, 32)
MEDALS = [((253, 224, 71), (217, 148, 20)), ((226, 232, 240), (130, 146, 170)), ((251, 146, 60), (186, 84, 24))]


def mix(a, b, t: float):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


def hgradient(size: tuple[int, int], c1, c2, alpha: int = 255) -> Image.Image:
    ww, hh = size
    strip = Image.new("RGBA", (ww, 1))
    sp = strip.load()
    for x in range(ww):
        sp[x, 0] = (*mix(c1, c2, x / max(1, ww - 1)), alpha)
    return strip.resize((ww, max(1, hh)))


def vgradient(size: tuple[int, int], c1, c2, a1: int = 255, a2: int = 255) -> Image.Image:
    ww, hh = size
    strip = Image.new("RGBA", (1, hh))
    sp = strip.load()
    for y in range(hh):
        t = y / max(1, hh - 1)
        sp[0, y] = (*mix(c1, c2, t), int(a1 * (1 - t) + a2 * t))
    return strip.resize((max(1, ww), hh))


def masked(img: Image.Image, mask: Image.Image) -> Image.Image:
    img = img.copy()
    img.putalpha(Image.composite(img.getchannel("A"), Image.new("L", img.size, 0), mask))
    return img


def glow(base: Image.Image, rect, radius: int, color, blur: int = 20, alpha: int = 90, outline: int = 0):
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    if outline:
        ld.rounded_rectangle(rect, radius, outline=(*color, alpha), width=outline)
    else:
        ld.rounded_rectangle(rect, radius, fill=(*color, alpha))
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(blur)))


def neon_card(base: Image.Image, rect, radius: int, accent, top_mix: float = 0.30, bottom_mix: float = 0.05, border: int = 2):
    x0, y0, x1, y1 = rect
    glow(base, rect, radius, accent, blur=14, alpha=170, outline=5)
    w, h = x1 - x0, y1 - y0
    body = vgradient((w, h), mix(NAVY, accent, top_mix), mix(NAVY, accent, bottom_mix), 244, 244)
    base.alpha_composite(masked(body, rounded_mask((w, h), radius)), (x0, y0))
    overlay_round_rect(base, rect, radius, outline=(*accent, 225), width=border)
    overlay_round_rect(base, (x0 + 3, y0 + 3, x1 - 3, y1 - 3), radius - 3, outline=(255, 255, 255, 22), width=1)


def gradient_text(base: Image.Image, xy: tuple[int, int], text: str, font, c1, c2, glow_rgb=None):
    d = ImageDraw.Draw(base)
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    mask = Image.new("L", (r - l + 8, b - t + 8), 0)
    ImageDraw.Draw(mask).text((4 - l, 4 - t), text, font=font, fill=255)
    pos = (xy[0] + l - 4, xy[1] + t - 4)
    if glow_rgb:
        halo = Image.new("RGBA", base.size, (0, 0, 0, 0))
        halo.paste((*glow_rgb, 150), (pos[0], pos[1]), mask)
        base.alpha_composite(halo.filter(ImageFilter.GaussianBlur(12)))
    fill = hgradient(mask.size, c1, c2)
    fill.putalpha(mask)
    base.alpha_composite(fill, pos)


def background(seed: int) -> Image.Image:
    rng = random.Random(seed)
    img = Image.new("RGBA", (W, H), (*NAVY, 255))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for cx, cy, r, col, a in [
        (260, 80, 420, (40, 70, 200), 120), (1300, 140, 420, (150, 50, 200), 90),
        (780, 120, 360, (50, 110, 230), 70), (140, 880, 380, (90, 50, 210), 70),
        (1420, 900, 380, (30, 150, 210), 60), (780, 1060, 560, (40, 60, 190), 80),
    ]:
        ld.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*col, a))
    img.alpha_composite(layer.filter(ImageFilter.GaussianBlur(120)))
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(260):
        x, y = rng.randrange(W), rng.randrange(H)
        col = rng.choice([(139, 92, 246), (34, 211, 238), (236, 72, 153), (255, 255, 255)])
        d.ellipse((x, y, x + 2, y + 2), fill=(*col, rng.randrange(25, 110)))
    return img


def draw_world_dots(base: Image.Image, seed: int):
    d = ImageDraw.Draw(base, "RGBA")
    rng = random.Random(seed + 3)
    blobs = [(300, 78, 150, 40, (59, 130, 246)), (520, 62, 150, 44, (99, 102, 241)), (760, 66, 190, 46, (139, 92, 246)),
             (990, 80, 170, 44, (217, 70, 239)), (1180, 70, 120, 36, (236, 72, 153))]
    for cx, cy, rx, ry, col in blobs:
        for xx in range(-rx, rx, 9):
            for yy in range(-ry, ry, 9):
                if (xx / rx) ** 2 + (yy / ry) ** 2 < rng.uniform(0.5, 1.0):
                    d.rounded_rectangle((cx + xx, cy + yy, cx + xx + 4, cy + yy + 4), 1, fill=(*col, rng.randrange(45, 130)))


def draw_wave(base: Image.Image, x0: int, x1: int, cy: int, max_h: int, color, seed: int):
    rng = random.Random(seed)
    d = ImageDraw.Draw(base, "RGBA")
    n = (x1 - x0) // 7
    for i in range(n):
        t = i / max(1, n - 1)
        env = math.sin(math.pi * t) ** 1.4
        bh = max(3, int(max_h * env * rng.uniform(0.35, 1.0)))
        x = x0 + i * 7
        d.line((x, cy - bh / 2, x, cy + bh / 2), fill=(*color, 215), width=3)
    glow(base, (x0, cy - max_h // 3, x1, cy + max_h // 3), 20, color, blur=14, alpha=45)


def draw_header(base: Image.Image, title: str, tagline: str, seed: int):
    d = ImageDraw.Draw(base, "RGBA")
    draw_world_dots(base, seed)
    draw_wave(base, 120, 300, 140, 96, PALETTE["cyan"], seed + 11)
    draw_wave(base, W - 300, W - 120, 140, 96, PALETTE["pink"], seed + 12)

    first, _, rest = title.partition(" ")
    tf = fit_plain_font(d, "display_bold", title, 98, 900)
    w1, w2, sp = bbox(d, first, tf)[0], bbox(d, rest, tf)[0] if rest else 0, bbox(d, " ", tf)[0]
    total = w1 + (sp + w2 if rest else 0)
    x = (W - total) // 2
    gradient_text(base, (x, 70), first, tf, (255, 255, 255), (232, 238, 255), glow_rgb=(120, 150, 255))
    if rest:
        gradient_text(base, (x + w1 + sp, 70), rest, tf, PALETTE["cyan"], (244, 114, 182), glow_rgb=(200, 90, 240))

    pill = (484, 188, 1052, 230)
    overlay_round_rect(base, pill, 21, fill=(10, 14, 48, 235))
    overlay_round_rect(base, pill, 21, outline=(150, 160, 255, 210), width=2)
    pf = f("sans_bold", 20)
    sw = sum(bbox(d, ch, pf)[0] + 7 for ch in tagline.upper())
    cx0 = (W - sw) // 2
    for ch in tagline.upper():
        d.text((cx0, 197), ch, font=pf, fill=(236, 240, 255, 245))
        cx0 += bbox(d, ch, pf)[0] + 7 if ch != " " else 14
    d.line((190, 214, 468, 214), fill=(*PALETTE["cyan"], 160), width=2)
    d.line((1068, 214, 1346, 214), fill=(*PALETTE["pink"], 160), width=2)


def _initial(name: str) -> str:
    for ch in name:
        if ch.isalnum():
            return ch.upper()
    return "?"


def avatar_tile(data: bytes | None, kind: str, name: str, size: int, accent) -> Image.Image:
    ss = size * 3
    if data:
        try:
            img = ImageOps.fit(Image.open(io.BytesIO(data)).convert("RGBA"), (ss, ss), Image.Resampling.LANCZOS)
        except Exception:
            img = None
    else:
        img = None
    if img is None:
        img = vgradient((ss, ss), mix(accent, (255, 255, 255), 0.18), mix(accent, NAVY, 0.55))
        td = ImageDraw.Draw(img)
        if kind == "music":
            draw_icon(td, "music", int(ss * 0.27), int(ss * 0.25), int(ss * 0.5), (255, 255, 255, 235))
        elif kind == "group" and not any(c.isalnum() for c in name):
            draw_icon(td, "group", int(ss * 0.2), int(ss * 0.2), int(ss * 0.6), (255, 255, 255, 235))
        else:
            ch = _initial(name)
            td.text((ss // 2, ss // 2), ch, font=text_font(run_type(ch), int(ss * 0.5), "bold"), fill=(255, 255, 255, 245), anchor="mm")
    mask = Image.new("L", (ss, ss), 0)
    md = ImageDraw.Draw(mask)
    if kind == "music":
        md.rounded_rectangle((0, 0, ss - 1, ss - 1), int(ss * 0.2), fill=255)
    else:
        md.ellipse((0, 0, ss - 1, ss - 1), fill=255)
    img.putalpha(mask)
    return img.resize((size, size), Image.Resampling.LANCZOS)


def draw_globe(d: ImageDraw.ImageDraw, x: int, y: int, s: int, col):
    d.ellipse((x, y, x + s, y + s), outline=col, width=2)
    d.ellipse((x + s * 0.3, y, x + s * 0.7, y + s), outline=col, width=2)
    d.line((x, y + s / 2, x + s, y + s / 2), fill=col, width=2)
    d.arc((x, y + s * 0.12, x + s, y + s * 0.88), 0, 360, fill=col, width=1)


def draw_panel(base: Image.Image, x: int, y: int, w: int, h: int, title: str, kind: str, accent, data, subtitle: str = ""):
    d = ImageDraw.Draw(base, "RGBA")
    neon_card(base, (x, y, x + w, y + h), 26, accent)

    ib = (x + 22, y + 20, x + 80, y + 78)
    glow(base, ib, 18, accent, blur=10, alpha=130)
    badge = vgradient((58, 58), mix(accent, (255, 255, 255), 0.22), mix(accent, NAVY, 0.35))
    base.alpha_composite(masked(badge, rounded_mask((58, 58), 18)), (ib[0], ib[1]))
    overlay_round_rect(base, ib, 18, outline=(255, 255, 255, 70), width=1)
    draw_icon(d, kind, x + 36, y + 34, 30, (255, 255, 255, 250))
    d.text((x + 98, y + 20), title, font=f("display_bold", 31), fill=(255, 255, 255, 252))
    if subtitle:
        d.text((x + 98, y + 59), ellipsize(d, subtitle, 15, "regular", w - 162), font=f("sans_regular", 15), fill=(205, 214, 240, 215))
    draw_crown(d, x + w - 58, y + 32, 34, (*mix(accent, (255, 255, 255), 0.2), 235))
    d.line((x + 22, y + 92, x + w - 22, y + 92), fill=(*accent, 90), width=1)

    row_h, step = 63, 70
    ry0 = y + 104
    pic_kind = {"group": "group", "user": "user"}.get(kind, "music")
    for idx in range(1, 6):
        yy = ry0 + (idx - 1) * step
        overlay_round_rect(base, (x + 14, yy, x + w - 14, yy + row_h), 16, fill=(255, 255, 255, 14 if idx == 1 else 8), outline=(*accent, 40), width=1)
        if idx > len(data):
            continue
        row = data[idx - 1]
        name, value, unit = row[0], row[1], row[2]
        pic = row[3] if len(row) > 3 else None

        c1, c2 = MEDALS[idx - 1] if idx <= 3 else (mix(accent, (255, 255, 255), 0.18), mix(accent, NAVY, 0.4))
        b = (x + 26, yy + 8, x + 73, yy + 55)
        badge = vgradient((47, 47), c1, c2)
        base.alpha_composite(masked(badge, rounded_mask((47, 47), 13)), (b[0], b[1]))
        overlay_round_rect(base, b, 13, outline=(255, 255, 255, 60), width=1)
        d.text((x + 49, yy + 32), str(idx), font=f("display_bold", 27), fill=(255, 255, 255, 255), anchor="mm", stroke_width=1, stroke_fill=(20, 12, 0, 90))

        av = avatar_tile(pic, pic_kind, name, 46, accent)
        base.alpha_composite(av, (x + 84, yy + 8))
        d.ellipse((x + 83, yy + 7, x + 131, yy + 55), outline=(255, 255, 255, 50), width=1) if pic_kind != "music" else None

        name_x = x + 146
        draw_mixed(base, (name_x, yy + 19), name, 24, (*PALETTE["text"], 250), "bold", max_width=w - 146 - 124)
        vtxt = str(value)
        d.text((x + w - 30, yy + 7), vtxt, font=fit_plain_font(d, "display_bold", vtxt, 31, 100), fill=(*mix(accent, (255, 255, 255), 0.25), 255), anchor="ra")
        d.text((x + w - 30, yy + 40), unit, font=f("sans_regular", 16), fill=(*PALETTE["muted"], 235), anchor="ra")


def draw_stat_deco(base: Image.Image, kind: str, x: int, y: int, w: int, h: int, accent, seed: int):
    d = ImageDraw.Draw(base, "RGBA")
    if kind == "group":
        draw_icon(d, "group", x + w - 112, y + h - 100, 100, (*accent, 70))
        return
    rng = random.Random(seed)
    n = 7
    for i in range(n):
        bh = int((h - 30) * (0.25 + 0.7 * (i + 1) / n) * rng.uniform(0.8, 1.0))
        bx = x + w - 12 * n - 14 + i * 12
        d.rounded_rectangle((bx, y + h - bh + 8, bx + 7, y + h + 8), 3, fill=(*accent, 80 + i * 12))


def draw_stats(base: Image.Image, stats_title: str, stats_subtitle: str, stats):
    d = ImageDraw.Draw(base, "RGBA")
    x, y, w, h = MARGIN, 744, W - MARGIN * 2, 234
    accent = (96, 120, 255)
    glow(base, (x, y, x + w, y + h), 28, accent, blur=16, alpha=130, outline=5)
    body = vgradient((w, h), (10, 18, 56), (7, 11, 36), 245, 245)
    base.alpha_composite(masked(body, rounded_mask((w, h), 28)), (x, y))
    overlay_round_rect(base, (x, y, x + w, y + h), 28, outline=(*accent, 215), width=2)

    gx = x + 30
    overlay_round_rect(base, (gx - 8, y + 12, gx + 40, y + 60), 14, fill=(255, 255, 255, 14), outline=(130, 150, 255, 120))
    draw_globe(d, gx + 2, y + 22, 28, (190, 205, 255, 235))
    tf = f("display_bold", 34)
    d.text((gx + 56, y + 36), stats_title, font=tf, fill=(255, 255, 255, 250), anchor="lm")
    tw = bbox(d, stats_title, tf)[0]
    d.text((gx + 56 + tw + 18, y + 40), ellipsize(d, stats_subtitle, 17, "regular", w - 560), font=f("sans_regular", 17), fill=(*PALETTE["muted"], 235), anchor="lm")

    pw_ = (W - MARGIN - 262, y + 14, W - MARGIN - 30, y + 58)
    overlay_round_rect(base, pw_, 22, fill=(10, 16, 50, 220), outline=(120, 140, 255, 170), width=1)
    pf, bf = f("sans_regular", 17), f("display_bold", 19)
    pw1, bw1 = bbox(d, "Powered by ", pf)[0], bbox(d, "SunloMusic", bf)[0]
    sx = pw_[0] + (pw_[2] - pw_[0] - pw1 - bw1) // 2
    d.text((sx, pw_[1] + 12), "Powered by ", font=pf, fill=(210, 220, 245, 235))
    gradient_text(base, (sx + pw1, pw_[1] + 10), "SunloMusic", bf, PALETTE["cyan"], (120, 140, 255))

    gap = 20
    cw = (w - 60 - gap * 2) // 3
    cy, ch = y + 76, 142
    for i, (kind, value, label, desc, ac) in enumerate(stats):
        cx = x + 30 + i * (cw + gap)
        glow(base, (cx, cy, cx + cw, cy + ch), 24, ac, blur=10, alpha=110, outline=4)
        cb = vgradient((cw, ch), mix(NAVY, ac, 0.55), mix(NAVY, ac, 0.12), 240, 240)
        base.alpha_composite(masked(cb, rounded_mask((cw, ch), 24)), (cx, cy))
        overlay_round_rect(base, (cx, cy, cx + cw, cy + ch), 24, outline=(*ac, 220), width=2)
        draw_stat_deco(base, kind, cx, cy, cw, ch - 18, ac, 40 + i)
        ib = (cx + 20, cy + 30, cx + 98, cy + 108)
        glow(base, ib, 22, ac, blur=10, alpha=140)
        ig = vgradient((78, 78), mix(ac, (255, 255, 255), 0.25), mix(ac, NAVY, 0.3))
        base.alpha_composite(masked(ig, rounded_mask((78, 78), 22)), (ib[0], ib[1]))
        overlay_round_rect(base, ib, 22, outline=(255, 255, 255, 80), width=1)
        draw_icon(d, kind, cx + 41, cy + 51, 36, (255, 255, 255, 250))
        vf = fit_plain_font(d, "display_bold", value, 56, cw - 130 - 90)
        d.text((cx + 118, cy + 14), value, font=vf, fill=(*mix(ac, (255, 255, 255), 0.3), 255))
        d.text((cx + 120, cy + 78), label, font=f("sans_bold", 20), fill=(255, 255, 255, 250))
        d.text((cx + 120, cy + 108), ellipsize(d, desc, 15, "regular", cw - 120 - 96), font=f("sans_regular", 15), fill=(205, 214, 240, 215))


def render_banner(output: Path, title: str, tagline: str, panels, stats_title: str, stats_subtitle: str, stats, seed: int):
    base = background(seed)
    draw_header(base, title, tagline, seed)
    count = len(panels)
    panel_w = (W - MARGIN * 2 - GAP * (count - 1)) // count
    for i, panel in enumerate(panels):
        panel_title, kind, accent, data = panel[:4]
        subtitle = panel[4] if len(panel) > 4 else ""
        draw_panel(base, MARGIN + i * (panel_w + GAP), 246, panel_w, 470, panel_title, kind, accent, data, subtitle)
    draw_stats(base, stats_title, stats_subtitle, stats)
    output.parent.mkdir(parents=True, exist_ok=True)
    base.convert("RGB").save(output, quality=96)
