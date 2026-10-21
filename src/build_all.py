# -*- coding: utf-8 -*-
"""Build all colorways: stage each project, then validate/build/package it
with the band10-toolkit, collecting the .bin/.face into face/dist/.

Requires:
  - tools/band10-toolkit (clone https://github.com/utsabfdahal/band10-toolkit
    here; Node.js 22+ with `npx tsx` available)
  - tools/fonts/Michroma.ttf + DSEG7Classic-Bold.ttf (SIL OFL)

Usage: python src/build_all.py
"""
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLKIT = os.path.join(ROOT, "tools", "band10-toolkit")
DIST = os.path.join(ROOT, "face", "dist")
COLORWAYS = ["white", "amber", "green", "ice", "red"]


def run_toolkit(args):
    npx = "npx.cmd" if os.name == "nt" else "npx"
    cmd = [npx, "tsx", "cli/index.ts"] + args
    r = subprocess.run(cmd, cwd=TOOLKIT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    keep = [l for l in (r.stdout + r.stderr).splitlines()
            if l.strip() and "WIDGET_OVERLAP" not in l
            and "allowOverlap" not in l and "Widgets \"background\"" not in l]
    print("   " + "\n   ".join(keep[-4:]))
    if r.returncode != 0:
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        sys.exit(f"toolkit failed: {' '.join(args)}")


def main():
    if not os.path.isdir(TOOLKIT):
        sys.exit("tools/band10-toolkit missing - see README (clone it first).")
    os.makedirs(DIST, exist_ok=True)
    for cw in COLORWAYS:
        print(f"[{cw}] staging")
        subprocess.run([sys.executable, os.path.join(ROOT, "src", "build_face.py"), cw],
                       check=True)
        proj = os.path.join(ROOT, "build", cw)
        print(f"[{cw}] validate")
        run_toolkit(["validate", proj])
        print(f"[{cw}] build")
        run_toolkit(["build", proj])
        print(f"[{cw}] package")
        run_toolkit(["package", proj])
        dist = os.path.join(proj, "dist")
        for f in sorted(os.listdir(dist)):
            shutil.copyfile(os.path.join(dist, f),
                            os.path.join(DIST, f"{f}"))
            print(f"   -> face/dist/{f}")
    print("all colorways built ->", DIST)


if __name__ == "__main__":
    main()
