# -*- coding: utf-8 -*-
"""
theme.py — colour palettes per niche.

Layout/structure is IDENTICAL across all sites (the "Summit Roofing"
reference structure). What changes per niche is the PALETTE:

  * accent colours (buttons, icons, highlights), and
  * the CANVAS itself. The page background used to be the same near-black
    (#0a0a0a) for every niche. It is now a deep, niche-tinted shade —
    lawn care sits on deep green, plumbing on deep navy, roofing on warm
    charcoal-brown, electricians on deep amber-brown, and so on — so every
    niche reads as its own brand while white text keeps full contrast.

Each palette is described by its accent colours plus a background hue and
saturation; every background / surface / border shade is derived from that
in `_derive()`, so adding a palette is one line.

A niche picks its palette with the `theme` key in niche_content.py.
The three original keys ("dark", "green", "blue") still work.
"""
import colorsys


def _hsl(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h / 360.0, l, s)
    return round(r * 255), round(g * 255), round(b * 255)


def _hex(rgb):
    return "#%02x%02x%02x" % rgb


def _rgbs(rgb):
    return "%d, %d, %d" % rgb


def _accent_rgb(hexcol):
    hexcol = hexcol.lstrip("#")
    return "%d, %d, %d" % tuple(int(hexcol[i:i + 2], 16) for i in (0, 2, 4))


# name: (accent, accent2, accent_d, bg_hue, bg_sat)
#   accent   = primary buttons / icon fills
#   accent2  = highlighted text / icons on the dark canvas
#   accent_d = deep shade for gradients / button hover
#   bg_hue   = hue (0-360) of the tinted canvas
#   bg_sat   = saturation (0-1) of the tinted canvas
PALETTES = {
    "orange":  ("#ea580c", "#f97316", "#7c2d12", 24, 0.45),
    "red":     ("#dc2626", "#f87171", "#7f1d1d", 0, 0.45),
    "crimson": ("#e11d48", "#fb7185", "#881337", 345, 0.42),
    "amber":   ("#d97706", "#fbbf24", "#78350f", 38, 0.50),
    "yellow":  ("#ca8a04", "#facc15", "#713f12", 48, 0.45),
    "brown":   ("#b45309", "#d6a15c", "#5c2c0c", 28, 0.38),
    "terracotta": ("#c2410c", "#e8875a", "#6b2410", 14, 0.40),
    "sand":    ("#b7791f", "#e6c27a", "#5f4114", 40, 0.30),
    "lime":    ("#65a30d", "#a3e635", "#365314", 85, 0.45),
    "green":   ("#15803d", "#22c55e", "#14532d", 140, 0.50),
    "emerald": ("#059669", "#34d399", "#064e3b", 158, 0.50),
    "olive":   ("#4d7c0f", "#a3c46b", "#2f4a0b", 75, 0.35),
    "teal":    ("#0d9488", "#2dd4bf", "#134e4a", 175, 0.50),
    "cyan":    ("#0891b2", "#22d3ee", "#164e63", 192, 0.55),
    "sky":     ("#0284c7", "#38bdf8", "#0c4a6e", 202, 0.55),
    "blue":    ("#1d4ed8", "#3b82f6", "#172554", 220, 0.55),
    "ice":     ("#0ea5e9", "#7dd3fc", "#075985", 205, 0.40),
    "indigo":  ("#4f46e5", "#818cf8", "#312e81", 240, 0.45),
    "violet":  ("#7c3aed", "#a78bfa", "#4c1d95", 262, 0.45),
    "purple":  ("#9333ea", "#c084fc", "#581c87", 275, 0.42),
    "pink":    ("#db2777", "#f472b6", "#831843", 330, 0.40),
    "slate":   ("#475569", "#94a3b8", "#1e293b", 215, 0.25),
    "steel":   ("#0369a1", "#7cb4d8", "#0c3a5a", 210, 0.30),
    "gold":    ("#b8860b", "#f0c75e", "#5c430a", 45, 0.40),
}

# Backward compatibility with the original three theme keys.
ALIASES = {"dark": "orange"}


def _derive(name):
    acc, acc2, accd, hue, sat = PALETTES[name]
    bg = _hsl(hue, sat, 0.085)          # main canvas
    bg_deep = _hsl(hue, sat, 0.055)     # top bar / footer
    surface = _hsl(hue, sat * 0.75, 0.16)   # cards, glass badges
    field = _hsl(hue, sat * 0.6, 0.19)      # form inputs
    line = _hsl(hue, sat * 0.55, 0.20)      # borders
    line_hi = _hsl(hue, sat * 0.5, 0.30)    # hover borders / scrollbar
    grad = tuple(_hex(_hsl(hue, sat, l)) for l in (0.05, 0.08, 0.11, 0.14, 0.17))
    tint_a, tint_b = _hex(_hsl(hue, sat, 0.09)), _hex(_hsl(hue, sat, 0.16))
    return {
        "name": name,
        "bg": _hex(bg),
        "bg_rgb": _rgbs(bg),
        "bg_deep": _hex(bg_deep),
        "surface_rgb": _rgbs(surface),
        "field_rgb": _rgbs(field),
        "line": _hex(line),
        "line_rgb": _rgbs(line),
        "line_hi": _hex(line_hi),
        "ink": "#ffffff",
        "font_disp": "'Inter',sans-serif",
        "font_body": "'Inter',sans-serif",
        "accent": acc,
        "accent2": acc2,
        "accent_d": accd,
        "accent_rgb": _accent_rgb(acc),
        "hero_grad": grad,
        "img_tint": f"linear-gradient(135deg, {tint_a} 0%, {tint_b} 50%, {tint_a} 100%)",
    }


THEMES = {name: _derive(name) for name in PALETTES}
for _old, _new in ALIASES.items():
    THEMES[_old] = THEMES[_new]


def get_theme(key: str) -> dict:
    return THEMES.get(key) or THEMES[ALIASES.get(key, "orange")]


# The engine's templates were written against a fixed near-black canvas.
# These are the literal colour strings they use; `apply_theme_canvas()`
# swaps each one for the niche's tinted equivalent in the finished HTML.
def canvas_replacements(T: dict):
    return [
        ("#0a0a0a", T["bg"]),
        ("#050505", T["bg_deep"]),
        ("rgba(10,10,10,", f"rgba({T['bg_rgb']},"),
        ("rgba(23, 23, 23, 0.55)", f"rgba({T['surface_rgb']}, 0.55)"),
        ("rgba(23,23,23,0.2)", f"rgba({T['surface_rgb']},0.35)"),
        ("rgba(38,38,38,0.8)", f"rgba({T['field_rgb']},0.85)"),
        ("rgba(38,38,38,0.5)", f"rgba({T['line_rgb']},0.6)"),
        ("#262626", T["line"]),
        ("#404040", T["line_hi"]),
    ]


def apply_theme_canvas(html: str, T: dict) -> str:
    for old, new in canvas_replacements(T):
        html = html.replace(old, new)
    return html


if __name__ == "__main__":
    for k, v in THEMES.items():
        print(f"{k:<11} bg={v['bg']}  accent={v['accent']}  accent2={v['accent2']}")
