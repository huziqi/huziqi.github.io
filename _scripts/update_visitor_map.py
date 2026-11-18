#!/usr/bin/env python3
"""
update_visitor_map.py
=====================
Render images/visitor_map.svg: a world map with the number of visitors per
country, using the per-country counts from Flag Counter (counter pYAe).

Usage:
    python _scripts/update_visitor_map.py [--html saved_countries_page.html]

Only the Python standard library is needed. Country shapes come from
Natural Earth 1:110m (public domain), pre-converted to _scripts/world_110m.json.
If fetching or parsing fails, the existing SVG is left untouched.
"""

import argparse
import html
import json
import math
import re
import sys
import urllib.request
from pathlib import Path

COUNTER_ID = "pYAe"
COUNTRIES_URL = f"https://s01.flagcounter.com/countries/{COUNTER_ID}/"
ROOT = Path(__file__).resolve().parent.parent
WORLD_JSON = ROOT / "_scripts" / "world_110m.json"
OUT_SVG = ROOT / "images" / "visitor_map.svg"
BADGE_URL = (f"https://s01.flagcounter.com/count2/{COUNTER_ID}/bg_FFFFFF/txt_000000/border_CCCCCC/"
             "columns_2/maxflags_20/viewers_0/labels_0/pageviews_1/flags_0/percent_0/")
OUT_BADGE = ROOT / "images" / "flag_counter.png"  # fallback copy shown if the live badge fails to load

# Places too small for the 1:110m map: (lon, lat)
EXTRA_POINTS = {
    "HK": (114.17, 22.32), "MO": (113.55, 22.19), "SG": (103.82, 1.35),
    "BH": (50.56, 26.07), "MT": (14.38, 35.94), "MV": (73.22, 3.20),
    "MU": (57.55, -20.35), "LU": (6.13, 49.81), "AD": (1.52, 42.51),
    "MC": (7.42, 43.74), "LI": (9.55, 47.17), "SM": (12.46, 43.94),
    "VA": (12.45, 41.90), "BB": (-59.54, 13.19), "AG": (-61.80, 17.06),
    "KN": (-62.78, 17.36), "LC": (-60.98, 13.91), "GD": (-61.68, 12.12),
    "VC": (-61.20, 13.25), "DM": (-61.37, 15.41), "TO": (-175.20, -21.18),
    "WS": (-172.10, -13.76), "KI": (172.98, 1.45), "FM": (158.22, 6.89),
    "MH": (171.18, 7.13), "PW": (134.58, 7.51), "NR": (166.93, -0.52),
    "TV": (179.19, -8.52), "ST": (6.61, 0.19), "CV": (-23.60, 15.12),
    "KM": (43.87, -11.88), "SC": (55.49, -4.68), "BM": (-64.75, 32.31),
    "GU": (144.79, 13.44), "RE": (55.54, -21.12), "GI": (-5.35, 36.14),
    "JE": (-2.13, 49.21), "GG": (-2.59, 49.45), "IM": (-4.55, 54.24),
    "AW": (-69.97, 12.52), "CW": (-68.99, 12.17), "KY": (-81.25, 19.31),
}

# Map frame: equirectangular, Antarctica dropped
W, H = 1000, 432
LON0, LON1, LAT0, LAT1 = -170.0, 190.0, 84.0, -58.0
MAP_H = 400  # plot height; the rest is the footer

LAND = "#e2e8f0"
LAND_VISITED = "#b7d3f6"
BORDER = "#ffffff"
DOT = "#2a78d6"
INK = "#0f172a"
MUTED = "#64748b"
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"


def project(lon, lat):
    if lon < LON0:
        lon += 360
    x = (lon - LON0) / (LON1 - LON0) * W
    y = (LAT0 - lat) / (LAT0 - LAT1) * MAP_H
    return x, y


def fetch_bytes(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (visitor-map updater)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch(url):
    return fetch_bytes(url).decode("utf-8", errors="replace")


def update_badge():
    """Save a copy of the Flag Counter badge; keep the old copy on any failure."""
    try:
        data = fetch_bytes(BADGE_URL)
    except Exception as e:
        print(f"warning: could not download Flag Counter badge: {e}", file=sys.stderr)
        return
    if not data.startswith(b"\x89PNG"):
        print("warning: Flag Counter badge is not a PNG; keeping the existing copy", file=sys.stderr)
        return
    OUT_BADGE.write_bytes(data)
    print(f"wrote {OUT_BADGE.relative_to(ROOT)} ({len(data)} bytes)")


def parse_countries(page):
    """Return [(iso2, name, visitors)] from the Flag Counter countries page."""
    rows = re.findall(
        r'class="flag-([a-z]{2})-png".*?<u>(.*?)</u>.*?<font face=arial size=2>([\d,]+)</font>',
        page, flags=re.S)
    out, seen = [], set()
    for iso, name, n in rows:
        iso = iso.upper()
        if iso in seen:
            continue
        seen.add(iso)
        out.append((iso, html.unescape(name).strip(), int(n.replace(",", ""))))
    m = re.search(r"Countries\s+\d+\s*-\s*(\d+)\s+of\s+(\d+)", re.sub(r"<[^>]+>", "", page))
    if m and int(m.group(1)) < int(m.group(2)):
        print(f"warning: only the first {m.group(1)} of {m.group(2)} countries are listed", file=sys.stderr)
    return out


def ring_path(ring):
    pts = []
    prev_x = None
    for lon, lat in ring:
        x, y = project(lon, lat)
        # avoid lines that wrap across the whole map
        if prev_x is not None and abs(x - prev_x) > W / 2:
            x = x - W if x > prev_x else x + W
        prev_x = x
        pts.append(f"{x:.1f} {y:.1f}")
    return "M" + "L".join(pts) + "Z"


def place_labels(points):
    """Greedy label placement: try right/left/above/below each dot, avoid overlaps."""
    boxes, placed = [], []
    for p in sorted(points, key=lambda p: -p["n"]):
        boxes.append((p["x"] - p["r"], p["y"] - p["r"], p["x"] + p["r"], p["y"] + p["r"]))
    for p in sorted(points, key=lambda p: -p["n"]):
        tw = 7.2 * len(str(p["n"])) + 2
        th = 13
        g = p["r"] + 3
        cands = [
            ("start", p["x"] + g, p["y"] + 4.5, (p["x"] + g, p["y"] - th / 2, p["x"] + g + tw, p["y"] + th / 2)),
            ("end", p["x"] - g, p["y"] + 4.5, (p["x"] - g - tw, p["y"] - th / 2, p["x"] - g, p["y"] + th / 2)),
            ("middle", p["x"], p["y"] - g - 2, (p["x"] - tw / 2, p["y"] - g - th, p["x"] + tw / 2, p["y"] - g)),
            ("middle", p["x"], p["y"] + g + 11, (p["x"] - tw / 2, p["y"] + g, p["x"] + tw / 2, p["y"] + g + th)),
        ]

        def hits(b):
            return sum(1 for o in boxes if not (b[2] <= o[0] or b[0] >= o[2] or b[3] <= o[1] or b[1] >= o[3]))

        best = min(cands, key=lambda c: (hits(c[3]), cands.index(c)))
        boxes.append(best[3])
        placed.append((p, best))
    return placed


def render(countries, world):
    shapes = {f["iso"]: f for f in world if f["iso"]}
    counts = {iso: n for iso, _, n in countries}
    total = sum(counts.values())
    nmax = max(counts.values()) if counts else 1

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" '
        f'aria-labelledby="vm-title vm-desc" font-family="{FONT}">',
        '<title id="vm-title">Visitor map</title>',
        '<desc id="vm-desc">' + html.escape(", ".join(f"{name}: {n}" for _, name, n in countries)) + "</desc>",
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<g stroke="{BORDER}" stroke-width="0.6" stroke-linejoin="round">',
    ]
    for f in world:
        fill = LAND_VISITED if f["iso"] in counts else LAND
        d = "".join(ring_path(r) for r in f["rings"])
        parts.append(f'<path fill="{fill}" d="{d}"/>')
    parts.append("</g>")

    points = []
    for iso, name, n in countries:
        if iso in shapes:
            lon, lat = shapes[iso]["label"]
        elif iso in EXTRA_POINTS:
            lon, lat = EXTRA_POINTS[iso]
        else:
            print(f"warning: no location for {iso} ({name}); skipped on map", file=sys.stderr)
            continue
        x, y = project(lon, lat)
        r = 3.5 + 7.5 * math.sqrt(n / nmax)
        points.append({"iso": iso, "name": name, "n": n, "x": x, "y": y, "r": r})

    parts.append(f'<g fill="{DOT}" fill-opacity="0.85" stroke="#ffffff" stroke-width="2">')
    for p in sorted(points, key=lambda p: -p["n"]):
        parts.append(f'<circle cx="{p["x"]:.1f}" cy="{p["y"]:.1f}" r="{p["r"]:.1f}">'
                     f'<title>{html.escape(p["name"])}: {p["n"]}</title></circle>')
    parts.append("</g>")

    labels = [f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="{anchor}">{p["n"]}</text>'
              for p, (anchor, tx, ty, _) in place_labels(points)]
    # white halo first, then the ink text on top (no paint-order dependency)
    parts.append('<g font-size="12" font-weight="600" fill="#ffffff" stroke="#ffffff" '
                 'stroke-width="3.5" stroke-linejoin="round">')
    parts.extend(labels)
    parts.append("</g>")
    parts.append(f'<g font-size="12" font-weight="600" fill="{INK}">')
    parts.extend(labels)
    parts.append("</g>")

    parts.append(
        f'<text x="12" y="{H - 10}" font-size="13" fill="{MUTED}">'
        f'<tspan fill="{INK}" font-weight="600">{total}</tspan> visitors from '
        f'<tspan fill="{INK}" font-weight="600">{len(counts)}</tspan> countries and regions'
        f' · dot size = visitors</text>')
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", help="use a saved Flag Counter countries page instead of fetching")
    args = ap.parse_args()

    page = Path(args.html).read_text(errors="replace") if args.html else fetch(COUNTRIES_URL)
    countries = parse_countries(page)
    if not countries:
        sys.exit("error: no countries parsed from Flag Counter; keeping the existing map")

    world = json.loads(WORLD_JSON.read_text())
    svg = render(countries, world)
    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT_SVG.relative_to(ROOT)}: {len(countries)} countries, "
          f"{sum(n for _, _, n in countries)} visitors")
    if not args.html:
        update_badge()


if __name__ == "__main__":
    main()
