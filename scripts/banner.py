#!/usr/bin/env python3
"""
banner.py – render a name as a dot-matrix SVG banner.

The dots are the same circle primitives used by dotify.py, so the banner
shares the exact visual DNA of the portrait without importing it.

Usage
-----
    python scripts/banner.py -o assets/banner
    python scripts/banner.py --name "NAITIK DARJI" --sub "CS · IIIT Vadodara" -o assets/banner

Writes assets/banner.svg (single colour-neutral file; the green palette reads
on both GitHub dark and light because the bg is transparent).
"""
from __future__ import annotations

import argparse
from pathlib import Path

# ── palette ─────────────────────────────────────────────────────────────────
FG      = "#39d353"   # bright green  — lit dot
DIM     = "#0e4429"   # dark green    — dim/off dot
SUB_FG  = "#8b949e"   # muted grey    — subtitle text
CURSOR  = "#39d353"

# ── 5 × 7 dot-matrix font (row 0 = top row) ─────────────────────────────────
# Each string is 5 chars wide; "1" = lit dot, "0" = off dot.
FONT: dict[str, list[str]] = {
    " ": ["00000"] * 7,
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "J": ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    "K": ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10001", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "Q": ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    "W": ["10001", "10001", "10001", "10001", "10101", "11011", "10001"],
    "X": ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    "Y": ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    "Z": ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    "0": ["01110", "10011", "10101", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "11111"],
    "2": ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    "3": ["11111", "00010", "00100", "00110", "00001", "10001", "01110"],
    "4": ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    "5": ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    "6": ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    "7": ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    "8": ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    "9": ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    ".": ["00000", "00000", "00000", "00000", "00000", "00100", "00100"],
    "&": ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "/": ["00001", "00010", "00100", "00100", "01000", "10000", "10000"],
    ":": ["00000", "00100", "00100", "00000", "00100", "00100", "00000"],
    "@": ["01110", "10001", "10111", "10101", "10111", "10000", "01110"],
    "!": ["00100", "00100", "00100", "00100", "00000", "00000", "00100"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
}

ROWS   = 7    # glyph height in dot rows
COLS   = 5    # glyph width in dot cols
CELL   = 8    # px per dot cell
DOT_R  = 2.8  # dot circle radius (px)
LGAP   = 10   # px gap between letter glyphs
PAD_X  = 20   # left/right padding
PAD_Y  = 18   # top/bottom padding
SUB_H  = 26   # height reserved below dots for the subtitle line
FONT_M = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def _xml_esc(s: str) -> str:
    """Escape characters that are invalid in SVG/XML text content."""
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


# ── rendering helpers ────────────────────────────────────────────────────────

def _char_dots(char: str, ox: float, oy: float) -> list[str]:
    """SVG circle elements for one character placed at (ox, oy)."""
    glyph = FONT.get(char.upper(), FONT[" "])
    out = []
    for r, row in enumerate(glyph):
        for c, px in enumerate(row):
            fill = FG if px == "1" else DIM
            if fill == DIM:
                continue  # skip off-dots entirely (transparent background)
            cx = ox + c * CELL + CELL / 2
            cy = oy + r * CELL + CELL / 2
            out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{DOT_R}" fill="{fill}"/>')
    return out


def _render_string(text: str) -> tuple[list[str], float]:
    """Render a string left-to-right; return (svg_elements, total_width)."""
    x = 0.0
    parts: list[str] = []
    for ch in text.upper():
        parts += _char_dots(ch, x, 0)
        x += COLS * CELL + LGAP
    return parts, x - LGAP  # strip trailing gap


# ── SVG builder ──────────────────────────────────────────────────────────────

def build_svg(name: str, sub: str, animate: bool) -> str:
    dot_elems, name_w = _render_string(name)
    glyph_h = ROWS * CELL

    # blinking cursor — a small 2-dot column just after the name
    cursor_x = name_w + LGAP / 2
    cursor_elems = [
        f'<circle cx="{cursor_x:.1f}" cy="{CELL * r + CELL / 2:.1f}" r="{DOT_R}" fill="{CURSOR}"/>'
        for r in range(ROWS - 1, ROWS)     # one dot on the bottom row
    ]

    # canvas size
    content_w = name_w + LGAP / 2 + DOT_R + 2  # up to right edge of cursor dot
    W = round(content_w + 2 * PAD_X)
    H = round(glyph_h + 2 * PAD_Y + SUB_H)

    # transform that centres the glyph block
    tx, ty = PAD_X, PAD_Y

    # ── CSS animations ──────────────────────────────────────────────────────
    css_parts: list[str] = []
    if animate:
        css_parts += [
            # cursor blink
            "@keyframes bk{0%,49%{opacity:1}50%,100%{opacity:0}}",
            ".cur{animation:bk 1.1s step-start infinite}",
            # name fade+slide in
            "@keyframes rv{from{opacity:0;transform:translateY(-5px)}"
            "to{opacity:1;transform:translateY(0)}}",
            ".nm{animation:rv .7s ease-out both}",
        ]
    style = f"<style>{''.join(css_parts)}</style>" if css_parts else ""

    nm_attr = ' class="nm"' if animate else ""
    cur_attr = ' class="cur"' if animate else ""

    # ── assemble SVG ────────────────────────────────────────────────────────
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-label="{name} dot-matrix banner">',
        style,
        # dot-matrix name
        f'<g transform="translate({tx:.0f},{ty:.0f})"{nm_attr}>',
        *dot_elems,
        "</g>",
        # blinking cursor
        f'<g transform="translate({tx:.0f},{ty:.0f})"{cur_attr}>',
        *cursor_elems,
        "</g>",
    ]

    # subtitle line — must XML-escape content before insertion
    if sub:
        sub_y = ty + glyph_h + 16
        parts.append(
            f'<text x="{W / 2:.1f}" y="{sub_y:.0f}" text-anchor="middle" '
            f'font-family="{FONT_M}" font-size="11.5" '
            f'letter-spacing="1.5" fill="{SUB_FG}">{_xml_esc(sub)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--name", default="NAITIK DARJI",
                   help="Text to render in dot-matrix (default: NAITIK DARJI)")
    p.add_argument("--sub",
                   default="3rd year CS  \u00b7  IIIT Vadodara  \u00b7  Java & React  \u00b7  DSA",
                   help="Subtitle line in regular monospace text")
    p.add_argument("-o", "--out", type=Path, default=Path("assets/banner"),
                   help="Output path WITHOUT extension")
    p.add_argument("--animate", action="store_true", default=True,
                   help="Add cursor blink + name fade-in animation (default on)")
    p.add_argument("--no-animate", dest="animate", action="store_false")
    args = p.parse_args(argv)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    svg = build_svg(args.name, args.sub, args.animate)
    dest = args.out.with_suffix(".svg")
    dest.write_text(svg, encoding="utf-8")
    print(f"wrote {dest}  ({len(svg) // 1024} KB, {len(args.name)} chars)")


if __name__ == "__main__":
    main()
