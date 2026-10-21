# RETRO LCD

A retro-inspired LCD watch face for the **Xiaomi Smart Band 10** - five
colorways, always-on display included.

![colorways](retro-colorways.png)

White-on-black vintage LCD style: big 7-segment time (24h), weekday /
date / month, weather condition + temperature, a 10-segment step-goal bar,
a battery bar + icon - and a dimmed miniature of it all as the AOD.

## Colorways

| File | Hue |
|---|---|
| `retro-watchface-white.bin` | classic white |
| `retro-watchface-amber.bin` | amber `#FFB000` |
| `retro-watchface-green.bin` | LCD green `#4ADE80` |
| `retro-watchface-ice.bin` | ice blue `#7DD3FC` |
| `retro-watchface-red.bin` | LED red `#FF1E1E` |

Every colorway is one hue expressed as a luminance ladder - primary ink,
secondary, dim levels - so the hierarchy survives the recolor. Each ships
with a matching AOD. Higher-resolution previews: `previews/`.

The band keeps ~9 downloaded faces, and every colorway has its own
identity - install as many as you like and switch them from the band's
face carousel.

## Install (no build needed)

The built faces are in [`face/dist/`](face/dist/). To install on the band:

1. Install [Notify for Xiaomi](https://play.google.com/store/apps/details?id=com.mc.xiaomi1)
   and open it once so it detects the band.
2. Android allows only one app to hold **Nearby devices**: revoke it from
   Mi Fitness, grant it to Notify.
3. Copy a `.bin` to the phone, then in Notify: **Watchfaces → Install
   private watchface** and pick the file (start from inside Notify).
4. Restore the **Nearby devices** permission to Mi Fitness. It may complain
   once about a third-party app - the face stays installed and Mi Fitness
   keeps working.

Tips: remove a previous copy of the same face before reinstalling an
update; keep custom faces under ~10. The AOD appears when the band's
system always-on display setting is on - it is a setting, not a separate
install.

## Build from source

Prerequisites: Python 3 with Pillow, Node.js 22+, and the
[band10-toolkit](https://github.com/utsabfdahal/band10-toolkit) cloned to
`tools/band10-toolkit`.

```sh
python src/build_all.py          # stage + validate + build + package all colorways
python src/preview_colorways.py  # 3x mocks + the gallery sheet
```

Faces are staged per colorway in `build/<colorway>/` and the packaged
`.bin`/`.face` land in `face/dist/`. To add a colorway, add one hue to
`COLORWAYS` in `src/build_face.py` - the luminance ladder does the rest.

## License & credits

- Code: [MIT](LICENSE)
- Fonts: DSEG7 Classic Bold (keshikan) and Michroma (Vernon Adams), both
  [SIL OFL 1.1](licenses/OFL-1.1.txt)
- Weather icons: derived from
  [Dhole/weather-pixel-icons](https://github.com/Dhole/weather-pixel-icons),
  [CC BY-SA 4.0](face/assets-src/weather/LICENSE.txt) - see
  [CREDITS.md](CREDITS.md) for the full breakdown

Hobby project - not affiliated with, endorsed by, or connected to Xiaomi
or Casio in any way.
