#!/usr/bin/env python3
"""Generate dark.svg / light.svg — animated terminal profile banner.

Blueprint: GitHub-Profile-Master-Prompt.pdf (Phase 1), adapted for a
line-art source image: instead of photo-tone segmentation, dark mode
tonally knocks out the light backdrop so only the subject's linework
draws (dithering a flat-white face would erase it — the dots trace the
illustration's dark strokes in both modes).

Palette follows the profile's GitHub-dark design system, not the PDF's.
Source of truth is this script + the .npy grids it saves, not the SVGs.

Usage: python3 generate_banner.py  (needs Pillow, NumPy, SciPy)
"""

import os
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PHOTO = os.path.join(REPO, "profile.jpg")

# ---------------------------------------------------------------- geometry
GRID_W, GRID_H = 300, 340          # dither grid (spec)
CELL = 1.25                        # px per grid cell -> portrait 375 x 425
BANNER_W, BANNER_H = 1180, 610
PX0, PY0 = 48, 110                 # portrait top-left inside the frame
FRAME = (32, 94, 407, 457)         # x, y, w, h (16px padding around portrait)
RX0, RX1 = 488, 1148               # info panel text span
ROW_FS = 14
CHW = ROW_FS * 0.6                 # monospace char width at 14px = 8.4
ROW_CHARS = 78                     # chars per locked row (78*8.4 = 655.2px)
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# ---------------------------------------------------------------- timing
INTRO_END = 3.2                    # intro plays once, loop takes over here
LOOP = 14.2                        # portrait 3.0 + 4 transitions 1.3 + 3 logos 2.0
# cumulative keyTimes inside the loop (explicit, uneven — spec)
KT = [0.0, 3.0, 4.3, 6.3, 7.6, 9.6, 10.9, 12.9, 14.2]
KT = [round(t / LOOP, 4) for t in KT]

N_INTRO_GROUPS = 60
N_BANDS_X, N_BANDS_Y = 8, 12       # 96 drift bands (~94 per spec)
BAND_NOISE = 4.0                   # per-dot noise sigma before grouping (grid-trap fix)
DRIFT = 0.42                       # fraction of the way toward logo centroid
N_TRAVELLERS = 900

THEMES = {
    "dark": dict(
        panel="#0d1117", inset="#010409", border="#30363d", chrome="#58a6ff",
        muted="#8b949e", value="#e6edf3", faint="#30363d", hue="#ff7b72",
        green="#3fb950", red="#f85149", knockout=True,
    ),
    "light": dict(
        panel="#ffffff", inset="#f6f8fa", border="#d0d7de", chrome="#0969da",
        muted="#57606a", value="#24292f", faint="#d0d7de", hue="#cf222e",
        green="#1a7f37", red="#cf222e", knockout=False,
    ),
}

ROWS = [  # (label, value, color key) — None = section gap
    ("Subject", "MD. Kawsar Ahmed", "value"),
    ("Role", "Software Engineer", "value"),
    ("Origin", "Cumilla, Bangladesh", "value"),
    ("Education", "B.Sc. CSE (Data Science) - BAIUST '26", "value"),
    ("Status", "Building + Learning + Shipping", "green"),
    ("ToolChain", "VS Code - Git - Docker - Linux", "value"),
    None,
    ("Core.Lang", "JavaScript - TypeScript - Python", "value"),
    ("Core.Frontend", "React - Next.js - TanStack", "value"),
    ("Core.Backend", "Node - Hono - Django - FastAPI", "value"),
    ("Core.Database", "MongoDB - PostgreSQL - Redis", "value"),
    ("Core.Infra", "Docker - AWS - GitHub Actions", "value"),
    None,
    ("Grid.Mail", "knownaskawsar@gmail.com", "chrome"),
    ("Grid.Portfolio", "coming soon", "muted"),
    ("Grid.LinkedIn", "/in/curl-kawsar", "chrome"),
    ("Grid.GitHub", "@curl-kawsar", "chrome"),
    ("Grid.Facebook", "/python.kawsar", "chrome"),
]

GLYPHS = ["</>", "{ }", ">|"]      # generic dev glyphs — no brand tracing needed
                                   # ">|" = prompt + block cursor, built in glyph_points

rng = np.random.default_rng(42)


# ---------------------------------------------------------------- portrait
def load_processed():
    img = Image.open(PHOTO).convert("L")
    w, h = img.size
    crop_w = round(h * GRID_W / GRID_H)
    x0 = (w - crop_w) // 2
    img = img.crop((x0, 0, x0 + crop_w, h))
    img = ImageOps.autocontrast(img, cutoff=1)
    img = ImageEnhance.Contrast(img).enhance(1.3)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))
    return np.asarray(img.resize((GRID_W, GRID_H), Image.LANCZOS), dtype=np.float64)


def fs_dither_serpentine(gray):
    v = gray.copy()
    h, w = v.shape
    out = np.zeros((h, w), dtype=bool)
    for y in range(h):
        fwd = y % 2 == 0
        sgn = 1 if fwd else -1
        for x in (range(w) if fwd else range(w - 1, -1, -1)):
            old = v[y, x]
            new = 255.0 if old >= 128 else 0.0
            out[y, x] = new == 0.0
            err = old - new
            if 0 <= x + sgn < w:
                v[y, x + sgn] += err * 7 / 16
            if y + 1 < h:
                if 0 <= x - sgn < w:
                    v[y + 1, x - sgn] += err * 3 / 16
                v[y + 1, x] += err * 5 / 16
                if 0 <= x + sgn < w:
                    v[y + 1, x + sgn] += err * 1 / 16
    return out


def runs_from_dots(dots):
    """Horizontal runs: list of (row, col_start, length)."""
    runs = []
    for y in range(dots.shape[0]):
        row = dots[y]
        x = 0
        while x < len(row):
            if row[x]:
                x0 = x
                while x < len(row) and row[x]:
                    x += 1
                runs.append((y, x0, x - x0))
            else:
                x += 1
    return runs


# ---------------------------------------------------------------- glyphs
def find_mono_font():
    for p in ("/System/Library/Fonts/Menlo.ttc",
              "/System/Library/Fonts/Monaco.ttf",
              "/Library/Fonts/Courier New.ttf"):
        if os.path.exists(p):
            return p
    raise RuntimeError("no monospace font found")


def glyph_points(text, n):
    """Sample n points (in portrait px coords) from a rendered glyph."""
    W, H = 900, 1020
    im = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(find_mono_font(), 380)
    if text == ">|":
        # terminal prompt: ">" glyph + solid block cursor (font underscores
        # render as a detached sliver — a block reads far better as dots)
        bb = d.textbbox((0, 0), ">", font=font)
        gw, gh = bb[2] - bb[0], bb[3] - bb[1]
        gx = (W - gw * 1.9) / 2 - bb[0]
        gy = (H - gh) / 2 - bb[1]
        d.text((gx, gy), ">", font=font, fill=0)
        cx0 = gx + bb[2] + gw * 0.35
        d.rectangle([cx0, (H - gh) / 2 + gh * 0.15, cx0 + gw * 0.55,
                     (H - gh) / 2 + gh], fill=0)
    else:
        bb = d.textbbox((0, 0), text, font=font)
        d.text(((W - (bb[2] - bb[0])) / 2 - bb[0],
                (H - (bb[3] - bb[1])) / 2 - bb[1]), text, font=font, fill=0)
    a = np.asarray(im) < 128
    ys, xs = np.nonzero(a)
    idx = rng.choice(len(xs), size=n, replace=len(xs) < n)
    pts = np.stack([xs[idx], ys[idx]], axis=1).astype(np.float64)
    # fit into the central portrait box, preserving aspect
    span = pts.max(0) - pts.min(0)
    box_w, box_h = GRID_W * CELL * 0.62, GRID_H * CELL * 0.42
    s = min(box_w / max(span[0], 1), box_h / max(span[1], 1))
    pts = (pts - pts.min(0)) * s
    pts[:, 0] += (GRID_W * CELL - pts[:, 0].max()) / 2
    pts[:, 1] += (GRID_H * CELL - pts[:, 1].max()) / 2
    return pts


def chain_assign(shapes):
    """Optimal-transport chain: reorder each next shape to minimise travel."""
    ordered = [shapes[0]]
    for nxt in shapes[1:]:
        cur = ordered[-1]
        cost = ((cur[:, None, :] - nxt[None, :, :]) ** 2).sum(-1)
        _, cols = linear_sum_assignment(cost)
        ordered.append(nxt[cols])
    return ordered


# ---------------------------------------------------------------- metrics
def evenness_metric(runs, groups):
    """Mean total-variation distance of each intro group's spatial spread
    vs the overall distribution over a 4x4 grid. ~0.05 good, ~0.7 patchy."""
    cells = np.zeros((len(runs),), dtype=int)
    for i, (y, x0, ln) in enumerate(runs):
        cells[i] = (min(3, y * 4 // GRID_H)) * 4 + min(3, (x0 + ln // 2) * 4 // GRID_W)
    overall = np.bincount(cells, minlength=16) / len(runs)
    tvs = []
    for g in range(N_INTRO_GROUPS):
        sel = cells[groups == g]
        if len(sel) == 0:
            continue
        dist = np.bincount(sel, minlength=16) / len(sel)
        tvs.append(0.5 * np.abs(dist - overall).sum())
    return float(np.mean(tvs))


def boundary_metric(band_of):
    """Max column share of vertical band boundaries. ~0.01 organic, ~0.17 grid."""
    diff = band_of[:, 1:] != band_of[:, :-1]
    cols = np.nonzero(diff)[1]
    if len(cols) == 0:
        return 0.0
    counts = np.bincount(cols, minlength=GRID_W - 1)
    return float(counts.max() / counts.sum())


# ---------------------------------------------------------------- svg bits
def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return s if s else "0"


def portrait_path(runs):
    parts = []
    for y, x0, ln in runs:
        parts.append(f"M{fmt(x0 * CELL)} {fmt((y + 0.5) * CELL)}h{fmt(ln * CELL)}")
    return "".join(parts)


def grouped_paths(runs, assign, n_groups):
    out = [[] for _ in range(n_groups)]
    for r, g in zip(runs, assign):
        y, x0, ln = r
        out[g].append(f"M{fmt(x0 * CELL)} {fmt((y + 0.5) * CELL)}h{fmt(ln * CELL)}")
    return ["".join(p) for p in out]


def info_rows_svg(t):
    y = 114
    parts = []
    for row in ROWS:
        if row is None:
            y += 10
            continue
        label, value, ck = row
        n_dots = ROW_CHARS - len(label) - len(value) - 2
        lx = RX0
        dx = RX0 + CHW * (len(label) + 1)
        color = t[ck]
        parts.append(
            f'<text x="{lx}" y="{y}" class="mono" font-size="{ROW_FS}" fill="{t["muted"]}" '
            f'textLength="{fmt(CHW * len(label))}" lengthAdjust="spacingAndGlyphs">{label}</text>'
            f'<text x="{fmt(dx)}" y="{y}" class="mono" font-size="{ROW_FS}" fill="{t["faint"]}" '
            f'textLength="{fmt(CHW * n_dots)}" lengthAdjust="spacingAndGlyphs">{"." * n_dots}</text>'
            f'<text x="{RX1}" y="{y}" class="mono" font-size="{ROW_FS}" fill="{color}" '
            f'text-anchor="end" textLength="{fmt(CHW * len(value))}" '
            f'lengthAdjust="spacingAndGlyphs">{esc(value)}</text>'
        )
        y += 23
    return "".join(parts), y


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(theme_name, t, runs, intro_assign, band_assign, band_shift, waypoints):
    kt = ";".join(f"{k:.4f}" for k in KT)

    # --- intro layer: portrait duplicated, 60 interleaved fade-in groups
    intro_paths = grouped_paths(runs, intro_assign, N_INTRO_GROUPS)
    intro = []
    for i, d in enumerate(intro_paths):
        if not d:
            continue
        b = 0.10 + (i % N_INTRO_GROUPS) * 0.030
        intro.append(
            f'<path d="{d}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" begin="{b:.2f}s" '
            f'dur="0.55s" fill="freeze"/></path>'
        )
    intro_layer = (
        f'<g stroke="{t["hue"]}" stroke-width="1.05" fill="none" '
        f'shape-rendering="crispEdges">{"".join(intro)}'
        f'<set attributeName="opacity" to="0" begin="{INTRO_END}s" fill="freeze"/></g>'
    )

    # --- loop layer: same dots grouped into drift bands
    n_bands = N_BANDS_X * N_BANDS_Y
    band_paths = grouped_paths(runs, band_assign, n_bands)
    bands = []
    for bidx, d in enumerate(band_paths):
        if not d:
            continue
        dx, dy = band_shift[bidx]
        tv = f"0 0;0 0;{fmt(dx)} {fmt(dy)};{fmt(dx)} {fmt(dy)};0 0"
        ktv = f"{KT[0]};{KT[1]};{KT[2]};{KT[7]};{KT[8]}"
        bands.append(
            f'<g><animateTransform attributeName="transform" type="translate" '
            f'values="{tv}" keyTimes="{ktv}" dur="{LOOP}s" begin="{INTRO_END}s" '
            f'repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="{ktv}" '
            f'dur="{LOOP}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
            f'<path d="{d}"/></g>'
        )
    loop_layer = (
        f'<g opacity="0" stroke="{t["hue"]}" stroke-width="1.05" fill="none" '
        f'shape-rendering="crispEdges">'
        f'<set attributeName="opacity" to="1" begin="{INTRO_END}s" fill="freeze"/>'
        f'{"".join(bands)}</g>'
    )

    # --- travellers: portrait sample -> glyphs -> back, opacity-gated
    trav = []
    P0, L1, L2, L3 = waypoints
    for i in range(N_TRAVELLERS):
        xs = [P0[i][0], P0[i][0], L1[i][0], L1[i][0], L2[i][0], L2[i][0],
              L3[i][0], L3[i][0], P0[i][0]]
        ys = [P0[i][1], P0[i][1], L1[i][1], L1[i][1], L2[i][1], L2[i][1],
              L3[i][1], L3[i][1], P0[i][1]]
        trav.append(
            f'<circle cx="{fmt(xs[0])}" cy="{fmt(ys[0])}" r="2">'
            f'<animate attributeName="cx" values="{";".join(fmt(v) for v in xs)}" '
            f'keyTimes="{kt}" dur="{LOOP}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{";".join(fmt(v) for v in ys)}" '
            f'keyTimes="{kt}" dur="{LOOP}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;1;1;1;1;1;1;0" '
            f'keyTimes="{kt}" dur="{LOOP}s" begin="{INTRO_END}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    trav_layer = (
        f'<g opacity="0" fill="{t["chrome"]}">'
        f'<set attributeName="opacity" to="1" begin="{INTRO_END}s" fill="freeze"/>'
        f'{"".join(trav)}</g>'
    )

    rows_svg, _ = info_rows_svg(t)
    fx, fy, fw, fh = FRAME

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{BANNER_W}" height="{BANNER_H}" viewBox="0 0 {BANNER_W} {BANNER_H}" role="img" aria-label="MD. Kawsar Ahmed — animated terminal profile">
<style>.mono{{font-family:{MONO};}}</style>
<rect x="6" y="6" width="{BANNER_W - 12}" height="{BANNER_H - 12}" rx="12" fill="{t["panel"]}" stroke="{t["border"]}"/>
<line x1="6" y1="46" x2="{BANNER_W - 6}" y2="46" stroke="{t["border"]}"/>
<circle cx="30" cy="26" r="5.5" fill="#ff5f56"/><circle cx="50" cy="26" r="5.5" fill="#ffbd2e"/><circle cx="70" cy="26" r="5.5" fill="#27c93f"/>
<text x="590" y="31" class="mono" font-size="13" fill="{t["muted"]}" text-anchor="middle" textLength="132.6" lengthAdjust="spacingAndGlyphs">profile.sh --live</text>
<g>
  <animate attributeName="opacity" values="1;0.25;1" dur="1.6s" repeatCount="indefinite"/>
  <circle cx="1086" cy="26" r="4" fill="{t["red"]}"/>
  <text x="1098" y="31" class="mono" font-size="12" fill="{t["red"]}" letter-spacing="2" textLength="40" lengthAdjust="spacingAndGlyphs">LIVE</text>
</g>
<text x="{fx}" y="82" class="mono" font-size="13" fill="{t["chrome"]}" letter-spacing="3" textLength="120" lengthAdjust="spacingAndGlyphs">VISUAL.MAP</text>
<text x="{RX0}" y="82" class="mono" font-size="13" fill="{t["chrome"]}" letter-spacing="3" textLength="132" lengthAdjust="spacingAndGlyphs">SYSTEM.INFO</text>
<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="8" fill="{t["inset"]}" stroke="{t["border"]}"/>
<g transform="translate({PX0},{PY0})">
{intro_layer}
{loop_layer}
{trav_layer}
</g>
{rows_svg}
<rect x="{RX0}" y="505" width="132" height="32" rx="16" fill="{t["chrome"]}" fill-opacity="0.12" stroke="{t["chrome"]}"/>
<text x="{RX0 + 66}" y="526" class="mono" font-size="14" fill="{t["chrome"]}" text-anchor="middle" textLength="100.8" lengthAdjust="spacingAndGlyphs">@curl-kawsar</text>
</svg>'''
    return svg


# ---------------------------------------------------------------- main
def main():
    proc = load_processed()
    dots = {
        "light": fs_dither_serpentine(proc),
        "dark": fs_dither_serpentine(np.where(proc >= 200, 255.0, proc)),
    }
    np.save(os.path.join(HERE, "light_dots.npy"), dots["light"])
    np.save(os.path.join(HERE, "dark_dots.npy"), dots["dark"])

    glyph_pts = [glyph_points(g, N_TRAVELLERS) for g in GLYPHS]

    for name, theme in THEMES.items():
        d = dots[name]
        runs = runs_from_dots(d)

        # intro: random interleaved groups (scattered everywhere by construction)
        intro_assign = rng.integers(0, N_INTRO_GROUPS, size=len(runs))
        even = evenness_metric(runs, intro_assign)

        # drift bands: quantized position + per-dot noise (the grid-trap fix)
        centers = np.array([[(x0 + ln / 2.0), y] for y, x0, ln in runs])
        noisy = centers + rng.normal(0, BAND_NOISE, size=centers.shape)
        bx = np.clip((noisy[:, 0] / (GRID_W / N_BANDS_X)).astype(int), 0, N_BANDS_X - 1)
        by = np.clip((noisy[:, 1] / (GRID_H / N_BANDS_Y)).astype(int), 0, N_BANDS_Y - 1)
        band_assign = by * N_BANDS_X + bx

        # boundary straightness measured on the full dot grid
        cell_centers = np.argwhere(d)[:, ::-1].astype(float)  # x, y
        cn = cell_centers + rng.normal(0, BAND_NOISE, size=cell_centers.shape)
        gx = np.clip((cn[:, 0] / (GRID_W / N_BANDS_X)).astype(int), 0, N_BANDS_X - 1)
        gy = np.clip((cn[:, 1] / (GRID_H / N_BANDS_Y)).astype(int), 0, N_BANDS_Y - 1)
        grid_band = np.full(d.shape, -1, dtype=int)
        grid_band[d] = (gy * N_BANDS_X + gx)
        bmetric = boundary_metric(np.where(d, grid_band, -1))

        # no-noise comparison
        gx0 = np.clip((cell_centers[:, 0] / (GRID_W / N_BANDS_X)).astype(int), 0, N_BANDS_X - 1)
        gy0 = np.clip((cell_centers[:, 1] / (GRID_H / N_BANDS_Y)).astype(int), 0, N_BANDS_Y - 1)
        grid_band0 = np.full(d.shape, -1, dtype=int)
        grid_band0[d] = (gy0 * N_BANDS_X + gx0)
        bmetric0 = boundary_metric(np.where(d, grid_band0, -1))

        # per-band translation toward first logo centroid
        target = glyph_pts[0].mean(0)
        n_bands = N_BANDS_X * N_BANDS_Y
        band_shift = np.zeros((n_bands, 2))
        for b in range(n_bands):
            sel = centers[band_assign == b]
            if len(sel):
                mean_px = sel.mean(0) * CELL
                band_shift[b] = DRIFT * (target - mean_px)

        # travellers: sample portrait dots, chain optimal transport thru glyphs
        pool = cell_centers * CELL
        pick = rng.choice(len(pool), size=N_TRAVELLERS, replace=len(pool) < N_TRAVELLERS)
        P0 = pool[pick]
        chained = chain_assign([P0] + glyph_pts)
        waypoints = chained  # P0, L1, L2, L3 aligned index-wise

        svg = build_svg(name, theme, runs, intro_assign, band_assign, band_shift, waypoints)
        out = os.path.join(REPO, f"{name}.svg")
        with open(out, "w") as f:
            f.write(svg)
        kb = os.path.getsize(out) / 1024
        print(f"{name}.svg: {kb:.0f} KB | dots {int(d.sum())} runs {len(runs)} "
              f"| evenness {even:.3f} (good ~0.05) "
              f"| boundary {bmetric:.3f} vs no-noise {bmetric0:.3f} (organic ~0.01, grid ~0.17)")


if __name__ == "__main__":
    main()
