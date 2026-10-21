# -*- coding: utf-8 -*-
"""Render the colorway gallery from staged projects: a 3x mock per colorway
(build/<cw>/preview-mock.png, normal + AOD) and one combined sheet
(retro-colorways.png at the repo root) for the README.

Usage: python src/preview_colorways.py   (run after src/build_all.py)
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
COLORWAYS = ["white", "amber", "green", "ice", "red"]


def zoom(im, f):
    return im.resize((im.width * f, im.height * f), Image.NEAREST)


def main():
    mocks = []
    for cw in COLORWAYS:
        proj = os.path.join(BUILD, cw)
        normal = Image.open(os.path.join(proj, "preview.png")).convert("RGBA")
        aod = Image.open(os.path.join(proj, "preview-aod.png")).convert("RGBA")
        big = zoom(normal, 3)
        big.save(os.path.join(proj, "preview-mock.png"))
        big_aod = zoom(aod, 3)
        big_aod.save(os.path.join(proj, "preview-aod-mock.png"))
        mocks.append((cw.upper(), normal, aod))

    zoom_f = 2
    pad = 24
    cw_w = 212 * zoom_f
    head = 34
    W = pad + len(mocks) * (cw_w + pad) + pad
    H = head + 2 * (520 * zoom_f + head) + pad
    sheet = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    x = pad
    for name, normal, aod in mocks:
        # caption in the face's own font, white on black
        from PIL import ImageFont, ImageDraw
        font = ImageFont.truetype(os.path.join(ROOT, "tools", "fonts", "Michroma.ttf"), 160)
        tmp = Image.new("L", (2000, 400), 0)
        ImageDraw.Draw(tmp).text((20, 20), name, font=font, fill=255,
                                 stroke_width=3, stroke_fill=255)
        b = tmp.getbbox()
        cap = tmp.crop(b)
        cap_h = 9
        cap = cap.resize((max(round(cap.width * cap_h / cap.height), 1), cap_h), Image.BOX)
        cap = cap.point(lambda v: 255 if v >= 110 else 0)
        white = Image.new("RGBA", cap.size, (255, 255, 255, 255))
        cap_img = Image.new("RGBA", cap.size, (0, 0, 0, 0))
        cap_img.paste(white, (0, 0), cap)
        sheet.alpha_composite(cap_img, (x + (cw_w - cap.width) // 2, 10))
        sheet.alpha_composite(zoom(normal, zoom_f), (x, head))
        sheet.alpha_composite(zoom(aod, zoom_f), (x, head + 520 * zoom_f + head))
        x += cw_w + pad
    out = os.path.join(ROOT, "retro-colorways.png")
    sheet.save(out)
    print("sheet:", out, sheet.size)


if __name__ == "__main__":
    main()
