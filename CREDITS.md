# Credits & licenses

Code, layout and the palette system: MIT (see `LICENSE`).

## Fonts (SIL Open Font License 1.1)

| Font | Author | Used for |
|---|---|---|
| [DSEG7 Classic Bold](https://github.com/keshikan/DSEG) | keshikan | time & temperature digits |
| [Michroma](https://fonts.google.com/specimen/Michroma) | Vernon Adams | wordmark, labels, date row |

Both are bundled in `tools/fonts/` under the SIL Open Font License 1.1
(`licenses/OFL-1.1.txt`). The generator renders their glyphs to bitmaps at
build time; the license terms travel with any redistribution of the font
files.

## Weather icons (CC BY-SA 4.0)

The weather icons are derived from
[Dhole/weather-pixel-icons](https://github.com/Dhole/weather-pixel-icons)
© Dhole, licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Modifications: rescaled 2× (nearest neighbor) and color-tinted per colorway
at build time. The source bitmaps live in `face/assets-src/weather/` and the
tinted derivatives ship inside the built faces; both are licensed under the
same CC BY-SA 4.0 (see `face/assets-src/weather/LICENSE.txt`). Any
redistribution of these icons - standalone or inside a face - must keep the
attribution and the share-alike terms.

## Toolkit

Built with [band10-toolkit](https://github.com/utsabfdahal/band10-toolkit)
(MIT) - native `.bin` packer verified on real Band 10 hardware. Not
redistributed here; clone it into `tools/band10-toolkit` to build (see README).

## Disclaimer

This is a hobby project. It is not affiliated with, endorsed by, or connected
to Xiaomi or Casio in any way.
