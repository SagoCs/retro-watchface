# -*- coding: utf-8 -*-
"""Build the RETRO LCD watch face for one colorway.

Usage:
  python src/build_face.py <white|amber|green|ice>

Writes a complete toolkit project to build/<colorway>/ (layout.json,
manifest.json, assets/, preview.png). src/build_all.py loops colorways and
drives the band10-toolkit CLI over each staging project.

Design system:
  - one hue per colorway, expressed as a luminance ladder (ink/sub/mid/low/dim)
  - all TEXT (header, labels, date row) in Michroma, area-downscaled with a
    hard threshold - one typographic voice
  - all DIGITS (time, temperature) in DSEG7 Classic Bold
  - weather icons: derived from Dhole/weather-pixel-icons (CC-BY-SA 4.0,
    see CREDITS.md), tinted to the colorway at build time
  - panel frames redrawn as crisp 2px lines at fixed positions
  - AOD: the header + time + date block in the dim "sub" role, centered
"""
import json
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
LAYOUT = os.path.join(ROOT, "face", "layout.json")
ICONS_SRC = os.path.join(ROOT, "face", "assets-src", "weather")
FONTS = os.path.join(ROOT, "tools", "fonts")
MICHROMA = os.path.join(FONTS, "Michroma.ttf")
DSEG = os.path.join(FONTS, "DSEG7Classic-Bold.ttf")

WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
CLEAR = (0, 0, 0, 0)

CANVAS = (212, 520)
PANELS = {
    "time": (100, 240, [202]),
    "weather": (249, 323, []),
    "activity": (331, 389, [352]),
    "battery": (397, 454, [418]),
}
PANEL_X = (15, 198)
CHAMFER = 8
WEATHER_DIVIDER_X = 106
HEADER_SEP_Y = 90

BRAND = "RETRO"
HEADER = {
    BRAND: ((27, 70, 104, 83), "ink"),
    "ALARM": ((141, 68, 183, 75), "sub"),
    "CHRONO": ((135, 78, 187, 86), "sub"),
}

# AOD: the header + time + date block in the dim role, centered on the canvas
AOD_HEADER_OFFSET = 113  # header box y-shift: normal y70 -> AOD y183
AOD_HEADER = {
    BRAND: ((27, 183, 104, 196), "sub"),
    "ALARM": ((141, 181, 183, 188), "sub"),
    "CHRONO": ((135, 191, 187, 199), "sub"),
}
AOD_SEP_Y = 203
AOD_PANELS = {"time": (213, 305, []), "date": (311, 339, [])}
AOD_TIME_Y = 227
AOD_DATE_Y = 319

COLORWAYS = {
    "white": (255, 255, 255),
    "amber": (255, 176, 0),
    "green": (74, 222, 128),
    "ice": (125, 211, 252),
    "red": (255, 30, 30),
}
FACE_IDS = {
    "white": "211020261",
    "amber": "211020262",
    "green": "211020263",
    "ice": "211020264",
    "red": "211020265",
}

BAR_W, BAR_H = 168, 20
BATT_W, BATT_H = 27, 12

_MICH = {}


def ladder(rgb):
    """One hue as a luminance ladder: ink full, roles scaled toward black."""
    def s(f):
        return tuple(round(c * f) for c in rgb) + (255,)
    return {
        "ink": rgb + (255,),
        "sub": s(170 / 255),
        "mid": s(150 / 255),
        "low": s(100 / 255),
        "dim": s(80 / 255),
    }


# ----------------------------------------------------------------------------
# Text + digits
# ----------------------------------------------------------------------------
def michroma_text(text, cap_h=11, color=WHITE):
    """Michroma text: bold source strokes, area downscale, uniform weight."""
    font = _MICH.setdefault(160, ImageFont.truetype(MICHROMA, 160))
    tmp = Image.new("L", (3000, 400), 0)
    ImageDraw.Draw(tmp).text((20, 20), text, font=font, fill=255,
                             stroke_width=3, stroke_fill=255)
    b = tmp.getbbox()
    ink = tmp.crop(b)
    sc = cap_h / (b[3] - b[1])
    tgt = (max(round((b[2] - b[0]) * sc), 1), cap_h)
    small = ink.resize(tgt, Image.BOX).point(lambda v: 255 if v >= 110 else 0)
    im = Image.new("RGBA", tgt, CLEAR)
    im.paste(Image.new("RGBA", tgt, color), (0, 0), small)
    return im


def michroma_box(text, box, color):
    """Michroma text area-downscaled into a fixed box (header wordmark)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    font = _MICH.setdefault(160, ImageFont.truetype(MICHROMA, 160))
    tmp = Image.new("L", (3000, 400), 0)
    ImageDraw.Draw(tmp).text((20, 20), text, font=font, fill=255,
                             stroke_width=3, stroke_fill=255)
    ink = tmp.crop(tmp.getbbox())
    small = ink.resize((w, h), Image.BOX).point(lambda v: 255 if v >= 110 else 0)
    out = Image.new("RGBA", (w, h), CLEAR)
    out.paste(Image.new("RGBA", (w, h), color), (0, 0), small)
    return out


def dseg_cells(chars, target_h, target_w=None, color=WHITE):
    """DSEG7 characters on a shared crop box so cells keep glyph positions."""
    font = ImageFont.truetype(DSEG, 100)
    origin = (40, 40)
    probe = Image.new("L", (500, 400), 0)
    ImageDraw.Draw(probe).text(origin, "8", font=font, fill=255)
    bx = probe.getbbox()
    out = {}
    for ch in chars:
        tmp = Image.new("L", (500, 400), 0)
        ImageDraw.Draw(tmp).text(origin, ch, font=font, fill=255)
        ink = tmp.crop(bx)
        sc = target_h / (bx[3] - bx[1])
        tgt = (target_w or max(round((bx[2] - bx[0]) * sc), 1), target_h)
        small = ink.resize(tgt, Image.LANCZOS).point(lambda v: 255 if v >= 128 else 0)
        im = Image.new("RGBA", tgt, CLEAR)
        im.paste(Image.new("RGBA", tgt, color), (0, 0), small)
        out[ch] = im
    return out


def colon7(h=70, t=10, color=WHITE):
    im = Image.new("RGBA", (t, h), CLEAR)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 21, t - 1, 21 + t - 1], fill=color)
    d.rectangle([0, 39, t - 1, 39 + t - 1], fill=color)
    return im


def degc_unit(color=WHITE):
    """Degree ring + DSEG "C" - same font as the temperature digits."""
    c = dseg_cells("C", 26, color=color)["C"]
    im = Image.new("RGBA", (11 + c.width, 30), CLEAR)
    d = ImageDraw.Draw(im)
    d.ellipse([0, 0, 9, 9], fill=color)
    d.ellipse([3, 3, 6, 6], fill=CLEAR)
    im.alpha_composite(c, (11, 2))
    return im


# ----------------------------------------------------------------------------
# Bars + battery
# ----------------------------------------------------------------------------
def draw_frames(d, panels, color):
    """Chamfered panel outlines + internal separators, at PANEL_X."""
    x0, x1 = PANEL_X
    for top, bot, seps in panels.values():
        cx = CHAMFER
        pts = [(x0 + cx, top), (x1 - cx, top), (x1, top + cx), (x1, bot - cx),
               (x1 - cx, bot), (x0 + cx, bot), (x0, bot - cx), (x0, top + cx),
               (x0 + cx, top)]
        d.line(pts, fill=color, width=2, joint="curve")
        for sy in seps:
            d.rectangle([x0, sy, x1, sy + 1], fill=color)


def bar_image(filled, pal):
    im = Image.new("RGBA", (BAR_W, BAR_H), CLEAR)
    d = ImageDraw.Draw(im)
    for i in range(10):
        x = i * 17
        d.rectangle([x, 0, x + 14, BAR_H - 1],
                    fill=pal["ink"] if i < filled else pal["dim"])
    return im


def hatch_stripes(pal):
    """Three short slanted stripes, right edge aligned with the battery icon."""
    im = Image.new("RGBA", (32, 12), CLEAR)
    d = ImageDraw.Draw(im)
    for i, col in enumerate((pal["ink"], pal["sub"], pal["low"])):
        x0 = i * 10
        d.polygon([(x0 + 1, 12), (x0 + 5, 12), (x0 + 10, 0), (x0 + 6, 0)], fill=col)
    return im


def battery_icon(level, pal):
    """Rounded outline, flat fill, short nub."""
    im = Image.new("RGBA", (BATT_W, BATT_H), CLEAR)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, 24, BATT_H - 1], radius=3, outline=pal["ink"], width=2)
    d.rectangle([25, 3, BATT_W - 1, BATT_H - 4], fill=pal["ink"])
    fill_w = round(level / 5 * 17)
    if fill_w:
        d.rectangle([3, 3, 3 + fill_w - 1, BATT_H - 4], fill=pal["mid"])
    return im


# ----------------------------------------------------------------------------
# Backgrounds
# ----------------------------------------------------------------------------
def build_background(pal):
    """Pure black base + vector separator, frames, labels, header. No artwork."""
    bg = Image.new("RGBA", CANVAS, BLACK)
    d = ImageDraw.Draw(bg)
    d.rectangle([14, HEADER_SEP_Y, 198, HEADER_SEP_Y + 1], fill=pal["ink"])
    draw_frames(d, PANELS, pal["ink"])
    d.rectangle([WEATHER_DIVIDER_X, 255, WEATHER_DIVIDER_X, 317], fill=pal["ink"])
    for text, (box, role) in HEADER.items():
        bg.alpha_composite(michroma_box(text, box, pal[role]), (box[0], box[1]))
    t = michroma_text("TEMP", 11, pal["ink"])
    bg.alpha_composite(t, (110, 263))
    act = michroma_text("ACTIVITY", 11, pal["ink"])
    bg.alpha_composite(act, (24, 333 + (352 - 333 - act.height) // 2))
    bat = michroma_text("BATTERY", 11, pal["ink"])
    bg.alpha_composite(bat, (24, 399 + (418 - 399 - bat.height) // 2))
    bg.alpha_composite(hatch_stripes(pal), (155, 336))
    return bg


def build_aod_background(pal):
    """Black AOD canvas: dim header + separator + two chamfered frames."""
    bg = Image.new("RGBA", CANVAS, BLACK)
    d = ImageDraw.Draw(bg)
    draw_frames(d, AOD_PANELS, pal["sub"])
    d.rectangle([14, AOD_SEP_Y, 198, AOD_SEP_Y + 1], fill=pal["sub"])
    for text, (box, role) in AOD_HEADER.items():
        bg.alpha_composite(michroma_box(text, box, pal[role]), (box[0], box[1]))
    return bg


def tint_icon(im, rgb):
    """White-on-transparent icon -> tint, keeping per-pixel coverage."""
    out = Image.new("RGBA", im.size, rgb + (255,))
    out.putalpha(im.getchannel("A"))
    return out


# ----------------------------------------------------------------------------
# Preview
# ----------------------------------------------------------------------------
def compose_preview(assets, pal):
    """Full face with sample data (positions mirror face/layout.json)."""
    def a(rel):
        return Image.open(os.path.join(assets, rel)).convert("RGBA")
    im = a("background.png")
    for i, d in enumerate("20"):
        im.alpha_composite(a(f"digits/time-{d}.png"), (26 + i * 35, 122))
    im.alpha_composite(a("colon.png"), (100, 122))
    for i, d in enumerate("48"):
        im.alpha_composite(a(f"digits/time-{d}.png"), (118 + i * 35, 122))
    im.alpha_composite(a("text/weekday-2.png"), (28, 214))
    for i, d in enumerate("20"):
        im.alpha_composite(a(f"digits/date7-{d}.png"), (92 + i * 14, 214))
    im.alpha_composite(a("text/month-10.png"), (132, 214))
    im.alpha_composite(a("weather/part.png"), (28, 254))
    for i, d in enumerate("24"):
        im.alpha_composite(a(f"digits/temp-{d}.png"), (121 + i * 22, 282))
    im.alpha_composite(a("text/unit-degc.png"), (167, 282))
    im.alpha_composite(a("bars/activity-7.png"), (23, 361))
    im.alpha_composite(a("bars/battery-8.png"), (23, 426))
    im.alpha_composite(a("battery/icon-4.png"), (159, 402))
    return im


def compose_aod_preview(assets):
    def a(rel):
        return Image.open(os.path.join(assets, rel)).convert("RGBA")
    im = a("aod/background.png")
    for i, d in enumerate("20"):
        im.alpha_composite(a(f"aod/time-{d}.png"), (26 + i * 35, AOD_TIME_Y))
    im.alpha_composite(a("aod/colon.png"), (100, AOD_TIME_Y))
    for i, d in enumerate("48"):
        im.alpha_composite(a(f"aod/time-{d}.png"), (118 + i * 35, AOD_TIME_Y))
    im.alpha_composite(a("aod/weekday-2.png"), (28, AOD_DATE_Y))
    for i, d in enumerate("20"):
        im.alpha_composite(a(f"aod/date7-{d}.png"), (92 + i * 14, AOD_DATE_Y))
    im.alpha_composite(a("aod/month-10.png"), (132, AOD_DATE_Y))
    return im


# ----------------------------------------------------------------------------
def save(im, assets, rel):
    path = os.path.join(assets, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path)


def build(colorway):
    pal = ladder(COLORWAYS[colorway])
    proj = os.path.join(BUILD, colorway)
    assets = os.path.join(proj, "assets")
    os.makedirs(assets, exist_ok=True)

    def s(im, rel):
        save(im, assets, rel)

    s(build_background(pal), "background.png")

    tcells = dseg_cells("0123456789-", 64, target_w=32, color=pal["ink"])
    for d_ in "0123456789":
        s(tcells[d_], f"digits/time-{d_}.png")
    s(tcells["-"], "digits/time-minus.png")
    s(colon7(color=pal["ink"]), "colon.png")

    dg = {d_: michroma_text(d_, 12, pal["ink"]) for d_ in "0123456789"}
    ch = max(g.height for g in dg.values())
    for d_ in "0123456789":
        cell = Image.new("RGBA", (13, ch), CLEAR)
        cell.alpha_composite(dg[d_], (0, 0))
        s(cell, f"digits/date7-{d_}.png")
    s(Image.new("RGBA", (13, ch), CLEAR), "digits/date7-minus.png")

    wcells = dseg_cells("0123456789-", 28, color=pal["ink"])
    for d_ in "0123456789":
        s(wcells[d_], f"digits/temp-{d_}.png")
    s(wcells["-"], "digits/temp-minus.png")
    s(degc_unit(pal["ink"]), "text/unit-degc.png")

    days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
    for i, name in enumerate(days):
        t = michroma_text(name, 12, pal["ink"])
        cell = Image.new("RGBA", (56, t.height), CLEAR)
        cell.alpha_composite(t, (0, 0))
        s(cell, f"text/weekday-{i}.png")
    months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
    for i, name in enumerate(months):
        t = michroma_text(name, 12, pal["ink"])
        cell = Image.new("RGBA", (56, t.height), CLEAR)
        cell.alpha_composite(t, (56 - t.width, 0))
        s(cell, f"text/month-{i + 1}.png")

    # weather icons: committed derived Dhole PNGs (CC-BY-SA 4.0), tinted
    for name in sorted(os.listdir(ICONS_SRC)):
        if not name.endswith(".png"):
            continue
        icon = Image.open(os.path.join(ICONS_SRC, name)).convert("RGBA")
        if name == "unknown.png":
            icon = Image.new("RGBA", (64, 64), CLEAR)
        else:
            icon = tint_icon(icon, pal["ink"][:3])
        s(icon, f"weather/{name}")

    for i in range(11):
        s(bar_image(i, pal), f"bars/activity-{i}.png")
        s(bar_image(i, pal), f"bars/battery-{i}.png")
    for i in range(6):
        s(battery_icon(i, pal), f"battery/icon-{i}.png")

    # AOD set
    s(build_aod_background(pal), "aod/background.png")
    acells = dseg_cells("0123456789-", 64, target_w=32, color=pal["sub"])
    for d_ in "0123456789":
        s(acells[d_], f"aod/time-{d_}.png")
    s(acells["-"], "aod/time-minus.png")
    s(colon7(color=pal["sub"]), "aod/colon.png")
    adg = {d_: michroma_text(d_, 12, color=pal["sub"]) for d_ in "0123456789"}
    ach = max(g.height for g in adg.values())
    for d_ in "0123456789":
        cell = Image.new("RGBA", (13, ach), CLEAR)
        cell.alpha_composite(adg[d_], (0, 0))
        s(cell, f"aod/date7-{d_}.png")
    s(Image.new("RGBA", (13, ach), CLEAR), "aod/date7-minus.png")
    for i, name in enumerate(days):
        t = michroma_text(name, 12, color=pal["sub"])
        cell = Image.new("RGBA", (56, t.height), CLEAR)
        cell.alpha_composite(t, (0, 0))
        s(cell, f"aod/weekday-{i}.png")
    for i, name in enumerate(months):
        t = michroma_text(name, 12, color=pal["sub"])
        cell = Image.new("RGBA", (56, t.height), CLEAR)
        cell.alpha_composite(t, (56 - t.width, 0))
        s(cell, f"aod/month-{i + 1}.png")

    # layout + manifest + preview
    shutil.copyfile(LAYOUT, os.path.join(proj, "layout.json"))
    manifest = {
        "$schema": "../../tools/band10-toolkit/schemas/manifest.schema.json",
        "formatVersion": 1,
        "id": FACE_IDS[colorway],
        "name": f"RETRO {colorway.capitalize()}",
        "author": "SagoCs",
        "version": "1.0.0",
        "description": ("Retro LCD watch face for the Xiaomi Smart Band 10: "
                        "24h time, weekday/date/month, weather with "
                        "temperature, activity and battery bars, AOD. "
                        "Not affiliated with Xiaomi."),
        "device": "xiaomi-smart-band-10",
        "preview": "preview.png",
        "output": f"retro-watchface-{colorway}",
        "compiler": {"target": "native", "imageCompression": True},
    }
    with open(os.path.join(proj, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    compose_preview(assets, pal).save(os.path.join(proj, "preview.png"))
    compose_aod_preview(assets).save(os.path.join(proj, "preview-aod.png"))
    print(f"staged {colorway} -> {proj}")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COLORWAYS:
        print("usage: python src/build_face.py <" + "|".join(COLORWAYS) + ">")
        sys.exit(1)
    build(sys.argv[1])
