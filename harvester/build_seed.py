"""THE CURATED CORE of games.ofthepast.org.

A hand-authored table of the great board, sowing, dice and guessing games of
**all of human history and every continent** — the spine the harvester reads.
Each entry carries everything the live site and the JustPlay launcher need: a
`boardgame/1.1` pack (a self-contained generated SVG board + glyph pieces, so
there are **zero binary assets**), the rules, and a curated historical `context`
blurb that the Wikipedia/Wikidata enrichers later augment.

Run `python -m harvester.build_seed` to (re)write `harvester/data/seed.json`.
Everything in `data/` downstream is generated from it.

Sibling, in machinery and house style, to **games.ofancientrome.org** (the same
curated-seed -> harvester -> static-data -> GitHub-Pages shape) and to
**rulers.ofthepast.org** (the same "whole world on a spine" broadening of a
single-culture sibling). House rule, shared with both: **never fabricate
history.** The rules of several of these games are *not recorded* — where we give
a playable set we mark the game `reconstruction: True` and say so plainly in the
rules and the context.
"""

import base64
import datetime
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = Path(__file__).resolve().parent / "data" / "seed.json"

# ---------------------------------------------------------------------------
# palette — a worn world gaming table: boxwood / parchment field, inked lines
# ---------------------------------------------------------------------------
STONE   = "#211a12"     # backdrop behind the board (dark wood)
FIELD   = "#e8d8b6"     # the board field (boxwood / parchment)
FIELD2  = "#d9c399"     # secondary field shade (dark squares, sunk areas)
INCISE  = "#6b4a2a"     # inked / incised lines
INCISE2 = "#9c7a48"     # lighter line / highlight
ROSETTE = "#b4472e"     # terracotta accent (rosettes, centres, rivers)
NODE    = "#4f3720"     # marked point

ALBUM = "#efe4cc"       # player one — bone / ivory / white men
RUBER = "#a8412e"       # player two — terracotta / red men
NIGER = "#2b241c"       # player two (war games) — slate / black
GOLD  = "#c8a24e"
GREEN = "#3f7a55"       # seeds / sowing
BLUE  = "#3a6ea5"
AMETH = "#8a5a8a"


def data_uri(svg):
    b64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + b64


def _svg(w, h, body, bg=FIELD):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" fill="{bg}"/>'
        f'{body}</svg>'
    )


def _line(x1, y1, x2, y2, stroke=INCISE, w=3):
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"/>'


def _dot(x, y, r=13, fill=NODE):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


def _frame(w, h, pad=14):
    return (
        f'<rect x="{pad}" y="{pad}" width="{w-2*pad}" height="{h-2*pad}" '
        f'fill="none" stroke="{INCISE}" stroke-width="6"/>'
        f'<rect x="{pad+10}" y="{pad+10}" width="{w-2*pad-20}" height="{h-2*pad-20}" '
        f'fill="none" stroke="{INCISE2}" stroke-width="2"/>'
    )


def _pack(w, h, body, pieceSize):
    return {"image": data_uri(_svg(w, h, body)), "aspect": round(w / h, 4),
            "color": STONE, "pieceSize": round(pieceSize, 4)}


# ---------------------------------------------------------------------------
# coordinate helper: centre of a full-bleed grid cell, normalised to [0,1]
# ---------------------------------------------------------------------------
def cellnorm(cols, rows):
    return lambda c, r: (round((c + 0.5) / cols, 4), round((r + 0.5) / rows, 4))


# ===========================================================================
# BOARD GENERATORS  (every board is a generated inline SVG — no binary assets)
# ===========================================================================
def board_grid(cols, rows, cell=86, checker=False, light=FIELD, dark=FIELD2):
    """A cols x rows board of squares (latrunculorum, petteia, draughts)."""
    w, h = cols * cell, rows * cell
    body = []
    if checker:
        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2:
                    body.append(f'<rect x="{c*cell}" y="{r*cell}" width="{cell}" height="{cell}" fill="{dark}"/>')
    for c in range(cols + 1):
        body.append(_line(c * cell, 0, c * cell, h, INCISE, 3))
    for r in range(rows + 1):
        body.append(_line(0, r * cell, w, r * cell, INCISE, 3))
    body.append(_frame(w, h, 0))
    return _pack(w, h, "".join(body), 0.82 / cols)


def board_go(n=19, cell=44):
    """Go / Weiqi — stones on the intersections of an n x n line grid + star points."""
    pad = cell
    span = (n - 1) * cell
    w = h = span + 2 * pad
    body = []
    for i in range(n):
        x = pad + i * cell
        body.append(_line(x, pad, x, pad + span, INCISE, 2))
        body.append(_line(pad, x, pad + span, x, INCISE, 2))
    body.append(f'<rect x="{pad}" y="{pad}" width="{span}" height="{span}" fill="none" stroke="{INCISE}" stroke-width="4"/>')
    stars = [3, 9, 15] if n == 19 else ([3, n // 2, n - 4] if n >= 13 else [n // 2])
    for sr in stars:
        for sc in stars:
            body.append(_dot(pad + sc * cell, pad + sr * cell, 6, INCISE))
    return _pack(w, h, "".join(body), 0.92 / (n + 1))


def board_xiangqi(cell=70):
    """Xiangqi — 9 files x 10 ranks of intersections, with the river and two palaces."""
    cols, rows = 9, 10
    pad = cell
    w = pad * 2 + (cols - 1) * cell
    h = pad * 2 + (rows - 1) * cell
    x0, y0 = pad, pad
    river_top = y0 + 4 * cell
    river_bot = y0 + 5 * cell
    body = []
    # horizontal ranks
    for r in range(rows):
        y = y0 + r * cell
        body.append(_line(x0, y, x0 + (cols - 1) * cell, y, INCISE, 2))
    # vertical files: outer two run full height; inner ones break at the river
    for c in range(cols):
        x = x0 + c * cell
        if c in (0, cols - 1):
            body.append(_line(x, y0, x, y0 + (rows - 1) * cell, INCISE, 2))
        else:
            body.append(_line(x, y0, x, river_top, INCISE, 2))
            body.append(_line(x, river_bot, x, y0 + (rows - 1) * cell, INCISE, 2))
    # the two palaces (diagonals across files 3..5)
    for (ra, rb) in ((0, 2), (7, 9)):
        xa, xb = x0 + 3 * cell, x0 + 5 * cell
        ya, yb = y0 + ra * cell, y0 + rb * cell
        body.append(_line(xa, ya, xb, yb, INCISE, 2))
        body.append(_line(xb, ya, xa, yb, INCISE, 2))
    body.append(f'<rect x="{x0}" y="{y0}" width="{(cols-1)*cell}" height="{(rows-1)*cell}" fill="none" stroke="{INCISE}" stroke-width="4"/>')
    body.append(
        f'<text x="{w/2}" y="{(river_top+river_bot)/2+10}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="34" letter-spacing="10" '
        f'fill="{INCISE}" opacity="0.4">楚河    漢界</text>')
    return _pack(w, h, "".join(body), 0.85 / (cols + 1))


def board_alquerque(n=5, cell=120):
    """An n x n lattice of points joined orthogonally + diagonally (alquerque, bagh-chal).
    Returns (board, norm) where norm(c, r) gives the normalised point coordinate."""
    pad = cell
    w = h = pad * 2 + (n - 1) * cell
    pts = [[(pad + c * cell, pad + r * cell) for c in range(n)] for r in range(n)]
    body = []
    # orthogonal lines
    for r in range(n):
        body.append(_line(pts[r][0][0], pts[r][0][1], pts[r][n - 1][0], pts[r][n - 1][1], INCISE, 3))
    for c in range(n):
        body.append(_line(pts[0][c][0], pts[0][c][1], pts[n - 1][c][0], pts[n - 1][c][1], INCISE, 3))
    # diagonals on alternate cells -> the classic alquerque weave
    for r in range(n - 1):
        for c in range(n - 1):
            if (r + c) % 2 == 0:
                body.append(_line(*pts[r][c], *pts[r + 1][c + 1], INCISE, 3))
                body.append(_line(*pts[r][c + 1], *pts[r + 1][c], INCISE, 3))
    for r in range(n):
        for c in range(n):
            body.append(_dot(*pts[r][c], 11, NODE))
    norm = lambda c, r: (round((pad + c * cell) / w, 4), round((pad + r * cell) / h, 4))
    return _pack(w, h, "".join(body), 0.9 / (n + 1)), norm


def board_tafl(n=9, cell=86):
    """An n x n tafl board (hnefatafl / tablut): grid + central throne + corner refuges."""
    w, h = n * cell, n * cell
    mid = n // 2
    body = []
    for cc, rr in [(0, 0), (n - 1, 0), (0, n - 1), (n - 1, n - 1), (mid, mid)]:
        body.append(f'<rect x="{cc*cell+4}" y="{rr*cell+4}" width="{cell-8}" height="{cell-8}" '
                    f'fill="{FIELD2}" stroke="{INCISE2}" stroke-width="2"/>')
    body.append(f'<circle cx="{mid*cell+cell/2}" cy="{mid*cell+cell/2}" r="{cell*0.28:.0f}" '
                f'fill="none" stroke="{ROSETTE}" stroke-width="3"/>')
    for c in range(n + 1):
        body.append(_line(c * cell, 0, c * cell, h, INCISE, 3))
    for r in range(n + 1):
        body.append(_line(0, r * cell, w, r * cell, INCISE, 3))
    body.append(_frame(w, h, 0))
    return _pack(w, h, "".join(body), 0.82 / n)


def board_cross():
    """A 33-point plus-shaped board (fox & geese / solitaire) with central diagonals.
    Returns (board, norm) over a 7x7 logical grid."""
    cell = 92
    pad = 56
    n = 7
    w = h = pad * 2 + (n - 1) * cell
    inplus = lambda c, r: (2 <= c <= 4) or (2 <= r <= 4)
    pos = lambda c, r: (pad + c * cell, pad + r * cell)
    body = []
    # outline of the cross
    body.append(f'<path d="M{pad+2*cell},{pad} h{2*cell} v{2*cell} h{2*cell} v{2*cell} '
                f'h-{2*cell} v{2*cell} h-{2*cell} v-{2*cell} h-{2*cell} v-{2*cell} h{2*cell} z" '
                f'fill="none" stroke="{INCISE}" stroke-width="5"/>')
    # orthogonal connections
    for r in range(n):
        for c in range(n):
            if not inplus(c, r):
                continue
            if c + 1 < n and inplus(c + 1, r):
                body.append(_line(*pos(c, r), *pos(c + 1, r), INCISE, 2))
            if r + 1 < n and inplus(c, r + 1):
                body.append(_line(*pos(c, r), *pos(c, r + 1), INCISE, 2))
    # diagonals through the centre arms (the fox's leaping lines)
    for (c, r) in [(2, 2), (3, 2), (2, 3), (3, 3)]:
        body.append(_line(*pos(c, r), *pos(c + 1, r + 1), INCISE2, 2))
        body.append(_line(*pos(c + 1, r), *pos(c, r + 1), INCISE2, 2))
    pts = []
    for r in range(n):
        for c in range(n):
            if inplus(c, r):
                body.append(_dot(*pos(c, r), 12, NODE))
                pts.append((c, r))
    norm = lambda c, r: (round((pad + c * cell) / w, 4), round((pad + r * cell) / h, 4))
    return _pack(w, h, "".join(body), 0.07), norm


def board_senet():
    """Senet — 3 rows of 10 squares (boustrophedon), the last five marked 'houses'."""
    cols, rows, cell = 10, 3, 110
    w, h = cols * cell, rows * cell
    body = []
    for c in range(cols + 1):
        body.append(_line(c * cell, 0, c * cell, h, INCISE, 3))
    for r in range(rows + 1):
        body.append(_line(0, r * cell, w, r * cell, INCISE, 3))
    # the five named end houses on the bottom row (squares 26-30 of the S-path):
    # House of Beauty (nfr), of Water, of the Three, of the Two Truths, of Horus/Re.
    # Renderer-safe glyphs (Egyptian-hieroglyph codepoints have no common web font).
    marks = {5: "★", 6: "≈", 7: "III", 8: "II", 9: "◉"}
    for c, gl in marks.items():
        cx, cy = c * cell + cell / 2, 2 * cell + cell / 2
        body.append(f'<rect x="{c*cell+4}" y="{2*cell+4}" width="{cell-8}" height="{cell-8}" '
                    f'fill="{FIELD2}" opacity="0.6"/>')
        body.append(f'<text x="{cx}" y="{cy+13}" text-anchor="middle" font-family="Georgia,serif" '
                    f'font-size="36" fill="{INCISE}" opacity="0.75">{gl}</text>')
    body.append(_frame(w, h, 0))
    return _pack(w, h, "".join(body), 0.045)


def board_ur():
    """The Royal Game of Ur — the 20-square 'twenty squares' board with five rosettes."""
    cell = 110
    cols, rows = 8, 3
    w, h = cols * cell, rows * cell
    # the board occupies a 4-wide block (cols 0-3), a 2-wide tail (cols 6-7),
    # joined by a 2-square bridge on the middle row (cols 4-5).
    present = set()
    for r in range(3):
        for c in range(4):
            present.add((c, r))
    for r in range(3):
        for c in (6, 7):
            present.add((c, r))
    present.add((4, 1))
    present.add((5, 1))
    rosettes = {(0, 0), (0, 2), (3, 1), (6, 0), (6, 2)}
    body = []
    for (c, r) in sorted(present):
        x, y = c * cell, r * cell
        body.append(f'<rect x="{x+3}" y="{y+3}" width="{cell-6}" height="{cell-6}" '
                    f'fill="{FIELD}" stroke="{INCISE}" stroke-width="3"/>')
        if (c, r) in rosettes:
            cx, cy = x + cell / 2, y + cell / 2
            for k in range(8):
                a = k * math.pi / 4
                body.append(_line(cx, cy, cx + 34 * math.cos(a), cy + 34 * math.sin(a), ROSETTE, 4))
            body.append(f'<circle cx="{cx}" cy="{cy}" r="14" fill="{FIELD}" stroke="{ROSETTE}" stroke-width="4"/>')
    norm = lambda c, r: (round((c * cell + cell / 2) / w, 4), round((r * cell + cell / 2) / h, 4))
    return _pack(w, h, "".join(body), 0.05), norm


def board_points(per_side=12):
    """A backgammon-style board of 24 elongated points in two tables (tabula, nard)."""
    w, h = 1320, 760
    pad, bar = 30, 60
    half = (w - 2 * pad - bar) / 2
    pw = half / 6
    ph = 250
    body = [f'<rect x="{pad}" y="{pad}" width="{w-2*pad}" height="{h-2*pad}" fill="{FIELD}" stroke="{INCISE}" stroke-width="6"/>']
    body.append(f'<rect x="{w/2-bar/2}" y="{pad}" width="{bar}" height="{h-2*pad}" fill="{FIELD2}" stroke="{INCISE}" stroke-width="4"/>')

    def point(px, top, idx):
        col = ROSETTE if idx % 2 == 0 else NIGER
        if top:
            return f'<polygon points="{px},{pad+6} {px+pw},{pad+6} {px+pw/2},{pad+6+ph}" fill="{col}" opacity="0.78"/>'
        return f'<polygon points="{px},{h-pad-6} {px+pw},{h-pad-6} {px+pw/2},{h-pad-6-ph}" fill="{col}" opacity="0.78"/>'

    for i in range(6):
        lx = pad + i * pw
        rx = pad + half + bar + i * pw
        body.append(point(lx, True, i))
        body.append(point(rx, True, i + 6))
        body.append(point(lx, False, i))
        body.append(point(rx, False, i + 6))
    return _pack(w, h, "".join(body), 0.038)


def board_cross_circle():
    """Pachisi — a cross of four arms, each three squares wide, around a central charkoni."""
    arm_w, arm_l = 3, 6      # squares
    cell = 64
    span = arm_l * cell           # length of one arm
    centre = arm_w * cell
    w = h = 2 * span + centre
    body = []

    def cells(x0, y0, cols, rows):
        for r in range(rows):
            for c in range(cols):
                body.append(f'<rect x="{x0+c*cell}" y="{y0+r*cell}" width="{cell}" height="{cell}" '
                            f'fill="none" stroke="{INCISE}" stroke-width="2"/>')

    cells(span, 0, arm_w, arm_l)                 # top arm
    cells(span, span + centre, arm_w, arm_l)     # bottom arm
    cells(0, span, arm_l, arm_w)                 # left arm
    cells(span + centre, span, arm_l, arm_w)     # right arm
    # central home square (charkoni)
    body.append(f'<rect x="{span}" y="{span}" width="{centre}" height="{centre}" '
                f'fill="{FIELD2}" stroke="{INCISE}" stroke-width="4"/>')
    body.append(f'<text x="{w/2}" y="{h/2+10}" text-anchor="middle" font-family="Georgia,serif" '
                f'font-size="30" fill="{INCISE}" opacity="0.55" letter-spacing="4">CHARKONI</text>')
    # castle (safe) squares: the rosette-marked middle of each arm's middle column
    for (cx, cy) in [(span + cell * 1.5, cell * 1.5), (span + cell * 1.5, span + centre + cell * 4.5),
                     (cell * 1.5, span + cell * 1.5), (span + centre + cell * 4.5, span + cell * 1.5)]:
        body.append(f'<circle cx="{cx}" cy="{cy}" r="12" fill="{ROSETTE}" opacity="0.8"/>')
    return _pack(w, h, "".join(body), 0.03)


def board_patolli():
    """Patolli — the Aztec cross: four arms of squares meeting at a central plaza."""
    arm = 8         # squares per half-arm pair (each arm is 2 columns wide)
    cell = 58
    span = arm * cell
    centre = 2 * cell
    w = h = 2 * span + centre
    body = []

    def strip(x0, y0, cols, rows):
        for r in range(rows):
            for c in range(cols):
                fill = FIELD2 if (r + c) % 2 == 0 else FIELD
                body.append(f'<rect x="{x0+c*cell}" y="{y0+r*cell}" width="{cell}" height="{cell}" '
                            f'fill="{fill}" stroke="{INCISE}" stroke-width="2"/>')

    strip(span, 0, 2, arm)                    # top
    strip(span, span + centre, 2, arm)        # bottom
    strip(0, span, arm, 2)                    # left
    strip(span + centre, span, arm, 2)        # right
    body.append(f'<rect x="{span}" y="{span}" width="{centre}" height="{centre}" '
                f'fill="{ROSETTE}" opacity="0.18" stroke="{INCISE}" stroke-width="4"/>')
    # the four arm-tip cells carry a diagonal cross (where pieces enter and leave)
    for (x0, y0, rw, rh) in [(span, 0, 2 * cell, cell), (span, 2 * span + centre - cell, 2 * cell, cell),
                             (0, span, cell, 2 * cell), (2 * span + centre - cell, span, cell, 2 * cell)]:
        body.append(_line(x0, y0, x0 + rw, y0 + rh, INCISE2, 2))
        body.append(_line(x0 + rw, y0, x0, y0 + rh, INCISE2, 2))
    return _pack(w, h, "".join(body), 0.028)


def board_goose():
    """Game of the Goose — a 63-square inward spiral on a 9x7 grid."""
    cols, rows, cell = 9, 7, 78
    w, h = cols * cell, rows * cell
    # inward clockwise spiral order
    order = []
    top, bottom, left, right = 0, rows - 1, 0, cols - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            order.append((c, top))
        top += 1
        for r in range(top, bottom + 1):
            order.append((right, r))
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                order.append((c, bottom))
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                order.append((left, r))
            left += 1
    geese = {5, 9, 14, 18, 23, 27, 32, 36, 41, 45, 50, 54, 59}
    hazards = {6: "≈", 19: "I", 31: "O", 42: "%", 52: "#", 58: "X", 63: "★"}
    body = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="{FIELD}"/>']
    for i, (c, r) in enumerate(order):
        n = i + 1
        x, y = c * cell, r * cell
        fill = FIELD2 if n in geese else FIELD
        body.append(f'<rect x="{x+2}" y="{y+2}" width="{cell-4}" height="{cell-4}" '
                    f'fill="{fill}" stroke="{INCISE}" stroke-width="2"/>')
        body.append(f'<text x="{x+cell/2}" y="{y+16}" text-anchor="middle" font-family="Georgia,serif" '
                    f'font-size="13" fill="{INCISE}" opacity="0.65">{n}</text>')
        if n in geese:
            body.append(f'<polygon points="{x+cell/2},{y+cell*0.5} {x+cell*0.66},{y+cell*0.78} '
                        f'{x+cell*0.34},{y+cell*0.78}" fill="{GREEN}" opacity="0.75"/>')
        elif n in hazards:
            body.append(f'<text x="{x+cell/2}" y="{y+cell*0.72}" text-anchor="middle" '
                        f'font-family="Georgia,serif" font-size="26" fill="{ROSETTE}" opacity="0.8">{hazards[n]}</text>')
    body.append(_frame(w, h, 0))
    return _pack(w, h, "".join(body), 0.03)


def board_mancala(cols=6, rows=2, stores=True, special=None):
    """A sowing board: `rows` rows of `cols` round pits, optional end stores (kalaha).
    `special` = set of (col, row) holes to ring (e.g. the bao nyumba)."""
    special = special or set()
    pit = 96
    gap = 22
    store_w = 130 if stores else 0
    pad = 30
    board_w = cols * pit + (cols + 1) * gap
    w = pad * 2 + 2 * store_w + board_w
    h = pad * 2 + rows * pit + (rows + 1) * gap
    body = [f'<rect x="{pad/2}" y="{pad/2}" width="{w-pad}" height="{h-pad}" rx="46" '
            f'fill="{FIELD2}" stroke="{INCISE}" stroke-width="6"/>']
    if stores:
        for sx in (pad, w - pad - store_w):
            body.append(f'<rect x="{sx}" y="{pad}" width="{store_w}" height="{h-2*pad}" rx="{store_w/2}" '
                        f'fill="{FIELD}" stroke="{INCISE}" stroke-width="4"/>')
    x0 = pad + store_w + gap
    y0 = pad + gap
    for r in range(rows):
        for c in range(cols):
            cx = x0 + c * (pit + gap) + pit / 2
            cy = y0 + r * (pit + gap) + pit / 2
            body.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{pit/2:.0f}" fill="{FIELD}" '
                        f'stroke="{INCISE}" stroke-width="4"/>')
            if (c, r) in special:
                body.append(f'<rect x="{cx-pit*0.32:.0f}" y="{cy-pit*0.32:.0f}" width="{pit*0.64:.0f}" '
                            f'height="{pit*0.64:.0f}" fill="none" stroke="{ROSETTE}" stroke-width="3"/>')
    return _pack(w, h, "".join(body), 0.022)


def board_nine_morris():
    """Nine men's morris — three concentric squares joined at the side midpoints (24 points)."""
    s = 640
    rings = [60, 170, 280]          # inset of each square from the edge
    body = [_frame(s, s, 24)]
    for ins in rings:
        body.append(f'<rect x="{ins}" y="{ins}" width="{s-2*ins}" height="{s-2*ins}" '
                    f'fill="none" stroke="{INCISE}" stroke-width="4"/>')
    mid = s / 2
    o, m, i = rings
    # the four connectors joining the side midpoints across the rings
    body.append(_line(mid, o, mid, i, INCISE, 4))
    body.append(_line(mid, s - o, mid, s - i, INCISE, 4))
    body.append(_line(o, mid, i, mid, INCISE, 4))
    body.append(_line(s - o, mid, s - i, mid, INCISE, 4))
    for ins in rings:
        lo, hi = ins, s - ins
        for (x, y) in [(lo, lo), (mid, lo), (hi, lo), (lo, mid), (hi, mid), (lo, hi), (mid, hi), (hi, hi)]:
            body.append(_dot(x, y, 12, NODE))
    return _pack(s, s, "".join(body), 0.055)


def board_morris():
    """Three men's morris — a 3x3 lattice of points joined by rows, columns, diagonals."""
    s = 600
    pad = 90
    g = (s - 2 * pad) / 2
    pts = [(pad + c * g, pad + r * g) for r in range(3) for c in range(3)]
    lines = []
    for r in range(3):
        lines.append((pts[r * 3], pts[r * 3 + 2]))
    for c in range(3):
        lines.append((pts[c], pts[c + 6]))
    lines.append((pts[0], pts[8]))
    lines.append((pts[2], pts[6]))
    body = [_frame(s, s, 24)]
    for a, b in lines:
        body.append(_line(a[0], a[1], b[0], b[1], INCISE, 4))
    for (x, y) in pts:
        body.append(_dot(x, y, 13, NODE))
    return _pack(s, s, "".join(body), 0.12)


def board_wheel():
    """Rota — a wheel of eight rim points + a hub, joined by four diameters."""
    s = 600
    cx = cy = s / 2
    R = 230
    rim = []
    for k in range(8):
        a = math.pi / 2 + k * math.pi / 4
        rim.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    body = [f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{INCISE}" stroke-width="5"/>']
    for k in range(4):
        a, b = rim[k], rim[k + 4]
        body.append(_line(a[0], a[1], b[0], b[1], INCISE, 4))
    for (x, y) in rim + [(cx, cy)]:
        body.append(_dot(x, y, 14, NODE))
    return _pack(s, s, "".join(body), 0.11)


def board_mu_torere():
    """Mu Torere — eight kewai points around a star, joined to a central putahi."""
    s = 600
    cx = cy = s / 2
    R = 220
    pts = []
    for k in range(8):
        a = math.pi / 2 + k * math.pi / 4
        pts.append((cx + R * math.cos(a), cy - R * math.sin(a)))
    body = []
    # star outline through the eight kewai
    poly = " ".join(f"{x:.1f},{y:.1f}" for (x, y) in pts)
    body.append(f'<polygon points="{poly}" fill="none" stroke="{INCISE}" stroke-width="4"/>')
    for (x, y) in pts:
        body.append(_line(cx, cy, x, y, INCISE, 3))
        body.append(_dot(x, y, 15, NODE))
    body.append(_dot(cx, cy, 17, ROSETTE))
    return _pack(s, s, "".join(body), 0.1)


def board_table(word="ALEA"):
    """A bare gaming table for the dice / guessing games — a parchment field."""
    w, h = 900, 620
    body = [_frame(w, h, 22)]
    body.append(f'<ellipse cx="{w/2}" cy="{h/2}" rx="250" ry="160" fill="none" stroke="{INCISE2}" stroke-width="3" opacity="0.5"/>')
    body.append(
        f'<text x="{w/2}" y="{h/2+22}" text-anchor="middle" '
        f'font-family="Georgia,serif" font-size="84" letter-spacing="12" '
        f'fill="{INCISE}" opacity="0.22">{word}</text>')
    return _pack(w, h, "".join(body), 0.06)


# ---------------------------------------------------------------------------
# piece / setup helpers
# ---------------------------------------------------------------------------
def disc(t, label, fill, glyph=""):
    return {"type": t, "label": label, "glyph": glyph, "bg": fill}


def gp(t, label, glyph, color=None, bg=None):
    p = {"type": t, "label": label, "glyph": glyph}
    if color:
        p["color"] = color
    if bg:
        p["bg"] = bg
    return p


def row(t, n, y, x0=0.12, x1=0.88):
    if n == 1:
        return [{"type": t, "x": round((x0 + x1) / 2, 4), "y": y}]
    step = (x1 - x0) / (n - 1)
    return [{"type": t, "x": round(x0 + i * step, 4), "y": y} for i in range(n)]


def at(t, norm, c, r):
    x, y = norm(c, r)
    return {"type": t, "x": x, "y": y}


# ---------------------------------------------------------------------------
# categories (ordered; each carries a pigment used by the frontend)
# ---------------------------------------------------------------------------
CATEGORIES = [
    {"key": "war",       "label": "War & strategy", "pigment": "#7a8a3a",
     "note": "Capture, position and territory — soldiers, stones and kings on a grid of squares or lines."},
    {"key": "hunt",      "label": "Hunt & siege",   "pigment": "#9c5a2e",
     "note": "Asymmetric games: a few strong pieces against a swarm of weak ones."},
    {"key": "race",      "label": "Race & tables",  "pigment": "#b4472e",
     "note": "Dice-driven race games — counters around a track, ancestors of backgammon and ludo."},
    {"key": "sowing",    "label": "Sowing",         "pigment": "#3f7a55",
     "note": "The mancala family — sow and capture seeds around a board of pits."},
    {"key": "alignment", "label": "Alignment",      "pigment": "#3a6ea5",
     "note": "Make a line of three — the morris and merels games scratched the world over."},
    {"key": "dice",      "label": "Dice & lots",    "pigment": "#caa05a",
     "note": "Gambling with knucklebones, cubes, marked beans and spinning tops."},
    {"key": "guessing",  "label": "Hand & guess",   "pigment": "#8a5a8a",
     "note": "Quick wagering games of the hand — nothing needed but nimble fingers."},
]

OHM_FOOTER = "Made with <3 in Bologna by OpenHistoryMap"

# pre-built boards that also hand back a coordinate normaliser
_alq5, _alq5n = board_alquerque(5)
_baghchal, _baghchaln = board_alquerque(5)
_cross, _crossn = board_cross()
_ur, _urn = board_ur()
_senet_norm = cellnorm(10, 3)
_tablut_norm = cellnorm(9, 9)
_petteia_norm = cellnorm(8, 8)
_lat_norm = cellnorm(12, 8)


# ---------------------------------------------------------------------------
# THE ROSTER
# ---------------------------------------------------------------------------
GAMES = [

    # =================== WAR & STRATEGY ====================================
    {
        "id": "go", "name": "Go", "native": "圍棋 Wéiqí · 囲碁 Igo · 바둑 Baduk",
        "aka": ["Weiqi", "Igo", "Baduk"], "category": "war",
        "origin": "China (Zhou dynasty)", "region": "East Asia", "era": "by c. 6th c. BCE",
        "players": "2", "duration": "30–90 min", "wp": "Go (game)", "reconstruction": False,
        "tagline": "The oldest game still played by its original rules — surround territory with stones.",
        "rules": {
            "objective": "Control more of the board than your opponent by surrounding empty intersections and capturing enemy stones.",
            "setup": "An empty grid of 19×19 lines (smaller 9×9 and 13×13 boards are common for learning). Black plays first. Stones are placed on the intersections, not the squares.",
            "howToPlay": [
                "Players alternate placing one stone of their colour on any empty intersection. Placed stones do not move.",
                "A stone or solidly-connected group is captured and removed when it has no adjacent empty point (no 'liberties') left.",
                "You may not play a stone that would immediately have no liberties (suicide), nor repeat the whole board position (the ko rule).",
                "Either player may pass; two passes in a row end the game.",
            ],
            "winning": "Count each player's surrounded territory plus captures (or stones on the board, by ruleset). The larger score wins; a handicap of extra stones lets unequal players meet fairly.",
            "variants": [
                "9×9 and 13×13 boards for shorter games.",
                "Handicap stones (2–9) placed for the weaker player on the star points.",
            ],
        },
        "context": {
            "period": "China, attested by the 6th c. BCE; spread to Korea and Japan",
            "blurb": (
                "Go — weiqi in China, igo in Japan, baduk in Korea — is the oldest board game "
                "still played in essentially its original form. Legend credits the sage-emperor "
                "Yao; it is named in the Analects and the Zuo Zhuan by the 6th–4th c. BCE. Two "
                "players lay black and white stones on the intersections of a 19×19 grid, each "
                "trying to surround more territory. From a trivially simple rule grows a game of "
                "such depth that it was the last classic board game in which computers surpassed "
                "human champions, only in 2016."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Fairbairn, J. (1995). Go in Ancient China.",
            ],
        },
        "board": board_go(19),
        "pieces": [disc("b", "Black stone (黑)", "#1c1714"), disc("w", "White stone (白)", "#efe7d2")],
        "setup": [],
        "turns": {"players": ["Black", "White"], "track": True},
    },
    {
        "id": "chaturanga", "name": "Chaturanga", "native": "चतुरङ्ग",
        "aka": ["The four limbs", "Ancestor of chess"], "category": "war",
        "origin": "India (Gupta empire)", "region": "South Asia", "era": "by c. 6th c. CE",
        "players": "2", "duration": "20–45 min", "wp": "Chaturanga", "reconstruction": True,
        "tagline": "The Indian root of chess, shogi and xiangqi — the four arms of an ancient army.",
        "rules": {
            "objective": "Capture or trap the enemy rājā (king).",
            "setup": "An 8×8 board (ashtāpada), unchequered in origin. Each side lines up a back row — chariot, horse, elephant, king and counsellor, elephant, horse, chariot — with eight foot-soldiers in front.",
            "howToPlay": [
                "Players alternate, moving one piece. The rājā steps one square any direction.",
                "The ratha (chariot) moves like the rook; the ashva (horse) like the knight.",
                "The gaja (elephant) and the mantri (counsellor) are weak short-range pieces in the old game — the powerful bishop and queen are later medieval inventions.",
                "The padāti (foot-soldier) advances one square and captures diagonally, much like a pawn.",
            ],
            "winning": "Checkmating or capturing the rājā wins. Some texts also award the game for stripping the enemy of every piece but the king.",
            "variants": [
                "Chaturaji — a four-handed dice version for four players.",
                "Exact powers of the elephant and counsellor vary between reconstructions and regions.",
            ],
        },
        "context": {
            "period": "India, by the 6th–7th c. CE (Gupta period)",
            "blurb": (
                "Chaturanga — 'four limbs', the four divisions of an Indian army: infantry, "
                "cavalry, elephants and chariots — is the common ancestor of chess, of Persian "
                "shatranj, of Chinese xiangqi and Japanese shogi. It first appears clearly in "
                "Sanskrit sources around the 6th–7th c. CE. The exact movement of some pieces is "
                "debated; the version below follows the standard scholarly reconstruction, which "
                "is why we flag it — the medieval queen and bishop are NOT part of this older game."
            ),
            "sources": [
                "Murray, H. J. R. (1913). A History of Chess. Oxford.",
                "Bidev, P. (1986). Chess — A Mathematical Mystery Tour.",
            ],
        },
        "board": board_grid(8, 8, checker=True),
        "pieces": [
            gp("w-raja", "Rājā (white king)", "♔", color=NIGER, bg=ALBUM),
            gp("w-mantri", "Mantri (counsellor)", "♕", color=NIGER, bg=ALBUM),
            gp("w-ratha", "Ratha (chariot)", "♖", color=NIGER, bg=ALBUM),
            gp("w-gaja", "Gaja (elephant)", "♗", color=NIGER, bg=ALBUM),
            gp("w-ashva", "Ashva (horse)", "♘", color=NIGER, bg=ALBUM),
            gp("w-padati", "Padāti (foot)", "♙", color=NIGER, bg=ALBUM),
            gp("b-raja", "Rājā (black king)", "♚", color=ALBUM, bg=NIGER),
            gp("b-mantri", "Mantri (counsellor)", "♛", color=ALBUM, bg=NIGER),
            gp("b-ratha", "Ratha (chariot)", "♜", color=ALBUM, bg=NIGER),
            gp("b-gaja", "Gaja (elephant)", "♝", color=ALBUM, bg=NIGER),
            gp("b-ashva", "Ashva (horse)", "♞", color=ALBUM, bg=NIGER),
            gp("b-padati", "Padāti (foot)", "♟", color=ALBUM, bg=NIGER),
        ],
        "setup": [],
        "turns": {"players": ["White", "Black"], "track": True},
    },
    {
        "id": "xiangqi", "name": "Xiangqi", "native": "象棋",
        "aka": ["Chinese chess", "Elephant game"], "category": "war",
        "origin": "China (by Song dynasty)", "region": "East Asia", "era": "by c. 11th c. CE",
        "players": "2", "duration": "20–40 min", "wp": "Xiangqi", "reconstruction": False,
        "tagline": "Chess across a river — generals confined to their palaces, cannons that leap to capture.",
        "rules": {
            "objective": "Checkmate the enemy general (將/帥).",
            "setup": "Pieces stand on the intersections of a 9×10 board split by a central 'river'. Each side has a general and two advisors in a 3×3 'palace', plus elephants, horses, chariots, cannons and five soldiers.",
            "howToPlay": [
                "The general moves one point orthogonally and may never leave the palace — nor face the enemy general down an open file.",
                "Chariots (車) move like rooks; horses (馬) move like knights but can be 'hobbled' by a blocking piece.",
                "Elephants (象) move two points diagonally and cannot cross the river; advisors (士) move one point diagonally inside the palace.",
                "The cannon (砲) moves like a chariot but captures only by jumping exactly one piece (a 'screen').",
                "Soldiers (兵) advance one point; after crossing the river they may also move sideways.",
            ],
            "winning": "Trap the enemy general so it cannot escape capture, exactly as in chess.",
            "variants": [
                "Blind and odds games are popular; many regional opening conventions exist.",
            ],
        },
        "context": {
            "period": "China, in its modern form by the 11th–12th c. CE",
            "blurb": (
                "Xiangqi — 'the elephant game' — is the chess of the Chinese-speaking world, "
                "played in its present shape since the Song dynasty. Two armies meet across a "
                "river painted down the middle of the board (楚河漢界, the Chu–Han frontier of the "
                "2nd c. BCE civil war). Its distinctive pieces — generals penned in a palace, "
                "cannons that capture only by leaping a screen — give it a character all its own. "
                "It remains one of the most-played games on earth."
            ),
            "sources": [
                "Murray, H. J. R. (1913). A History of Chess. Oxford.",
                "Li, D. H. (1998). The Genealogy of Chess.",
            ],
        },
        "board": board_xiangqi(),
        "pieces": [
            gp("r-gen", "General 帥", "帥", color=RUBER, bg=ALBUM),
            gp("r-adv", "Advisor 仕", "仕", color=RUBER, bg=ALBUM),
            gp("r-ele", "Elephant 相", "相", color=RUBER, bg=ALBUM),
            gp("r-hor", "Horse 傌", "傌", color=RUBER, bg=ALBUM),
            gp("r-cha", "Chariot 俥", "俥", color=RUBER, bg=ALBUM),
            gp("r-can", "Cannon 炮", "炮", color=RUBER, bg=ALBUM),
            gp("r-sol", "Soldier 兵", "兵", color=RUBER, bg=ALBUM),
            gp("b-gen", "General 將", "將", color=NIGER, bg="#cbb98f"),
            gp("b-adv", "Advisor 士", "士", color=NIGER, bg="#cbb98f"),
            gp("b-ele", "Elephant 象", "象", color=NIGER, bg="#cbb98f"),
            gp("b-hor", "Horse 馬", "馬", color=NIGER, bg="#cbb98f"),
            gp("b-cha", "Chariot 車", "車", color=NIGER, bg="#cbb98f"),
            gp("b-can", "Cannon 砲", "砲", color=NIGER, bg="#cbb98f"),
            gp("b-sol", "Soldier 卒", "卒", color=NIGER, bg="#cbb98f"),
        ],
        "setup": [],
        "turns": {"players": ["Red (帥)", "Black (將)"], "track": True},
    },
    {
        "id": "latrunculi", "name": "Ludus latrunculorum", "native": "Ludus latrunculorum",
        "aka": ["Latrunculi", "Latrones", "The game of little soldiers"], "category": "war",
        "origin": "Ancient Rome", "region": "Europe", "era": "c. 2nd c. BCE – 4th c. CE",
        "players": "2", "duration": "20–40 min", "wp": "Ludus latrunculorum", "reconstruction": True,
        "tagline": "Rome's game of soldiers — surround and capture on a grid of squares.",
        "rules": {
            "objective": "Capture your opponent's soldiers by trapping them, and corner their commander.",
            "setup": "Each player takes a row of soldiers (the latrones) of one colour plus a single commander (the dux). Boards of many sizes survive — 8×8, 8×12, 9×10; this pack uses 12×8.",
            "howToPlay": [
                "Players alternate, moving one piece per turn.",
                "A soldier moves any number of empty squares straight along a rank or file (like a rook) — not diagonally.",
                "Capture by custodia: bracket a single enemy soldier between two of yours on opposite sides. The bracketed soldier is removed.",
                "Moving your own piece into a gap between two enemies is safe — you are only captured when the enemy closes the bracket.",
            ],
            "winning": "Reduce the enemy until they cannot resist, or blockade the enemy dux so it cannot move (ad incitas redactus — 'driven to a standstill').",
            "variants": [
                "Board size is a house choice — the smaller the board, the sharper the game.",
                "Play without a dux for a pure surround-capture game.",
            ],
        },
        "context": {
            "period": "Roman Republic & Empire, c. 2nd c. BCE – 4th c. CE",
            "blurb": (
                "Ludus latrunculorum — 'the game of little robbers/soldiers' — was Rome's game of "
                "military skill, praised by Varro, Ovid and Martial as a contest of strategy "
                "without luck. Soldiers were captured by being flanked on two sides. The exact "
                "rules were never written down: what is played today is a careful modern "
                "reconstruction (notably by Ulrich Schädler) from scattered literary hints and "
                "surviving boards. Treat the moves below as one well-argued reading, not gospel."
            ),
            "sources": [
                "Schädler, U. (1994). Latrunculi — ein verlorenes strategisches Brettspiel der Römer.",
                "Austin, R. G. (1934). 'Roman Board Games.' Greece & Rome 4(11).",
            ],
        },
        "board": board_grid(12, 8),
        "pieces": [
            disc("rome", "Roman soldier", ALBUM),
            disc("host", "Opposing soldier", NIGER),
            gp("dux-r", "Roman dux", "✪", color=ROSETTE, bg=ALBUM),
            gp("dux-h", "Opposing dux", "✪", color=GOLD, bg=NIGER),
        ],
        "setup": (
            row("rome", 12, 0.94) + row("rome", 11, 0.81, 0.16, 0.84)
            + row("host", 12, 0.06) + row("host", 11, 0.19, 0.16, 0.84)
            + [{"type": "dux-r", "x": 0.5, "y": 0.94}, {"type": "dux-h", "x": 0.5, "y": 0.06}]
        ),
        "turns": {"players": ["Roma", "Hostes"], "track": True},
    },
    {
        "id": "petteia", "name": "Petteia", "native": "πεττεία",
        "aka": ["Poleis", "Polis", "Cities"], "category": "war",
        "origin": "Ancient Greece", "region": "Europe", "era": "c. 5th c. BCE",
        "players": "2", "duration": "15–30 min", "wp": "Petteia", "reconstruction": True,
        "tagline": "The Greek war of pebbles that Plato compared to philosophy — and Rome turned into latrunculi.",
        "rules": {
            "objective": "Capture the enemy stones by flanking them; leave your opponent unable to move.",
            "setup": "An 8×8 board. Each player ranges a row of stones (psephoi) of one colour along their back line.",
            "howToPlay": [
                "Players alternate, moving one stone any number of empty squares orthogonally (like a rook).",
                "A stone is captured when the enemy brackets it between two of theirs along a line — custodial capture.",
                "A stone safely moved between two enemies is not captured; only the enemy closing the trap captures.",
            ],
            "winning": "Capture enough stones, or pin the enemy so that no legal move remains.",
            "variants": [
                "Boards of 6×6 to 12×12 are all attested; agree a size first.",
                "Some reconstructions allow capture of a whole flanked line at once.",
            ],
        },
        "context": {
            "period": "Greek world, by the 5th c. BCE",
            "blurb": (
                "Petteia (also 'poleis', cities) was the Greek game of strategic capture, "
                "mentioned by Plato, who has Socrates liken skill at it to skill in argument, and "
                "by Homer's scholiasts, who imagined Penelope's suitors playing it. Stones were "
                "taken by being bracketed between two enemies. It is the direct forerunner of "
                "Rome's ludus latrunculorum; as with that game no rulebook survives, so the moves "
                "here are a reasoned reconstruction."
            ),
            "sources": [
                "Plato, Republic 333b; Lysis 206e.",
                "Kurke, L. (1999). Coins, Bodies, Games, and Gold.",
            ],
        },
        "board": board_grid(8, 8),
        "pieces": [disc("w", "Leukoi (white)", ALBUM), disc("b", "Melanes (black)", NIGER)],
        "setup": [at("w", _petteia_norm, c, 7) for c in range(8)] + [at("b", _petteia_norm, c, 0) for c in range(8)],
        "turns": {"players": ["Leukoi", "Melanes"], "track": True},
    },
    {
        "id": "alquerque", "name": "Alquerque", "native": "al-qirq / qirkat",
        "aka": ["Qirkat", "Quirkat"], "category": "war",
        "origin": "Islamic world & al-Andalus", "region": "West Asia", "era": "by c. 10th c. CE",
        "players": "2", "duration": "10–20 min", "wp": "Alquerque", "reconstruction": False,
        "tagline": "The medieval ancestor of draughts — leap and capture along a five-by-five lattice.",
        "rules": {
            "objective": "Capture all of your opponent's pieces.",
            "setup": "A board of 25 points joined by lines, orthogonal and diagonal. Each player has 12 pieces filling their two-and-a-half rows; the central point starts empty.",
            "howToPlay": [
                "Players alternate. A piece moves one step along any line to the adjacent empty point.",
                "Capture by jumping: hop over an adjacent enemy piece to the empty point directly beyond, along a line, and remove it.",
                "Multiple jumps may be chained in a single turn.",
            ],
            "winning": "Take all the enemy pieces, or leave them with no legal move.",
            "variants": [
                "Many versions require ('huffing') a capture when one is available.",
                "Alquerque is the parent of draughts/checkers once play moved onto the squares of a chessboard.",
            ],
        },
        "context": {
            "period": "Medieval Islamic world; recorded in Iberia, 13th c.",
            "blurb": (
                "Alquerque — from the Arabic al-qirq, the game qirkat described by the 10th-century "
                "scholar al-Mas'udi — is a capture-by-leaping game on a 5×5 lattice. It reached "
                "western Europe through al-Andalus and was illustrated in Alfonso X of Castile's "
                "Libro de los juegos (1283). When players later moved the same game onto the dark "
                "squares of a chessboard and added promotion, draughts (checkers) was born. Boards "
                "identical to alquerque's are cut into temple roofs in Egypt and across Asia."
            ),
            "sources": [
                "Alfonso X (1283). Libro de los juegos.",
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
            ],
        },
        "board": _alq5,
        "pieces": [disc("w", "White", ALBUM), disc("b", "Black", NIGER)],
        "setup": (
            [at("w", _alq5n, c, 0) for c in range(5)] + [at("w", _alq5n, c, 1) for c in range(5)]
            + [at("w", _alq5n, 0, 2), at("w", _alq5n, 1, 2)]
            + [at("b", _alq5n, c, 4) for c in range(5)] + [at("b", _alq5n, c, 3) for c in range(5)]
            + [at("b", _alq5n, 3, 2), at("b", _alq5n, 4, 2)]
        ),
        "turns": {"players": ["White", "Black"], "track": True},
    },

    # =================== HUNT & SIEGE ======================================
    {
        "id": "hnefatafl", "name": "Hnefatafl", "native": "hnefatafl / tablut",
        "aka": ["Tafl", "Tablut", "The king's table", "Viking chess"], "category": "hunt",
        "origin": "Norse & Sámi northern Europe", "region": "Europe", "era": "c. 4th–12th c. CE",
        "players": "2", "duration": "15–30 min", "wp": "Tafl games", "reconstruction": True,
        "tagline": "A king and his guard break out as twice their number close in — the Viking game of escape.",
        "rules": {
            "objective": "The king's side: get the king to a corner refuge. The attackers: capture the king first.",
            "setup": "This pack uses the well-documented 9×9 tablut layout: the king on the central throne with 8 defenders around him in a cross, and 16 attackers in a block of four on each edge.",
            "howToPlay": [
                "All pieces move any number of empty squares orthogonally, like a rook. Only the king may rest on the throne or a corner.",
                "Capture an ordinary piece by flanking it between two of yours (or a piece and the throne/corner) along a line — it is taken when you close the bracket.",
                "The king is captured when the attackers surround him on all four sides (or against the throne).",
            ],
            "winning": "The king wins by reaching any corner square; the attackers win by capturing the king before he escapes.",
            "variants": [
                "Larger boards (11×11 hnefatafl, 13×13 alea evangelii, 7×7 brandubh) change the balance.",
                "Some rules let the king escape to any edge rather than a corner.",
            ],
        },
        "context": {
            "period": "Northern Europe, Migration period through the Viking Age",
            "blurb": (
                "The tafl games — hnefatafl, 'the king's table' — were the great board games of "
                "the Norse and Germanic world before chess arrived. Uniquely, the two sides are "
                "unequal: a king and his guard, outnumbered two to one, try to break through a "
                "ring of besiegers to freedom. The rules were lost, but in 1732 Carl Linnaeus, "
                "travelling in Lapland, recorded a living Sámi version called tablut — the single "
                "best evidence we have, and the basis of the 9×9 game here. It is still a partial "
                "reconstruction, so we flag it."
            ),
            "sources": [
                "Linnaeus, C. (1732). Iter Lapponicum (Lachesis Lapponica).",
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
            ],
        },
        "board": board_tafl(9),
        "pieces": [
            disc("def", "Defender (Swede)", ALBUM),
            disc("att", "Attacker (Muscovite)", NIGER),
            gp("king", "The King", "♚", color=GOLD, bg=ALBUM),
        ],
        "setup": (
            [{"type": "king", **dict(zip(("x", "y"), _tablut_norm(4, 4)))}]
            + [{"type": "def", **dict(zip(("x", "y"), _tablut_norm(c, r)))}
               for (c, r) in [(4, 2), (4, 3), (4, 5), (4, 6), (2, 4), (3, 4), (5, 4), (6, 4)]]
            + [{"type": "att", **dict(zip(("x", "y"), _tablut_norm(c, r)))}
               for (c, r) in [(3, 0), (4, 0), (5, 0), (4, 1), (3, 8), (4, 8), (5, 8), (4, 7),
                              (0, 3), (0, 4), (0, 5), (1, 4), (8, 3), (8, 4), (8, 5), (7, 4)]]
        ),
        "turns": {"players": ["Attackers", "King's side"], "track": True},
    },
    {
        "id": "bagh-chal", "name": "Bagh-Chal", "native": "बाघचाल",
        "aka": ["Tigers and goats", "Moving tigers"], "category": "hunt",
        "origin": "Nepal", "region": "South Asia", "era": "traditional",
        "players": "2", "duration": "10–20 min", "wp": "Bagh-Chal", "reconstruction": False,
        "tagline": "Four tigers hunt; twenty goats try to pen them in — a perfectly uneven duel.",
        "rules": {
            "objective": "Tigers: capture five goats. Goats: block all four tigers so none can move.",
            "setup": "A 5×5 lattice (the alquerque grid). The four tigers begin on the corner points; the goats are all off the board, held in hand.",
            "howToPlay": [
                "The goat player goes first and, while goats remain in hand, must place one goat on an empty point each turn (goats cannot move yet).",
                "A tiger moves one step along a line to an adjacent empty point, or captures by jumping a single adjacent goat to the empty point beyond.",
                "Once all twenty goats are placed, goats may also move one step along a line.",
            ],
            "winning": "Tigers win by capturing five goats; goats win by trapping every tiger with no legal move.",
            "variants": [
                "Aadu puli aatam (South India) and similar tiger games use the same idea on different grids.",
            ],
        },
        "context": {
            "period": "Nepal, traditional (still widely played)",
            "blurb": (
                "Bagh-Chal — 'moving tigers' — is the national board game of Nepal, one of a great "
                "family of Asian hunt games in which a few powerful predators face a swarm of prey. "
                "Played on the same 5×5 alquerque lattice found from Egypt to India, it is a study "
                "in asymmetry: the tigers are strong but few, the goats weak but many, and good play "
                "on each side feels completely different. Brass bagh-chal boards are a common Nepali "
                "craft."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Parlett, D. (1999). The Oxford History of Board Games.",
            ],
        },
        "board": _baghchal,
        "pieces": [gp("tiger", "Tiger (bagh)", "🐅"), disc("goat", "Goat (bakhra)", ALBUM)],
        "setup": [at("tiger", _baghchaln, c, r) for (c, r) in [(0, 0), (4, 0), (0, 4), (4, 4)]],
        "turns": {"players": ["Goats", "Tigers"], "track": True},
    },
    {
        "id": "fox-and-geese", "name": "Fox and Geese", "native": "Fox and Geese",
        "aka": ["Fox game", "Halatafl"], "category": "hunt",
        "origin": "Medieval northern Europe", "region": "Europe", "era": "by c. 14th c. CE",
        "players": "2", "duration": "10–15 min", "wp": "Fox games", "reconstruction": False,
        "tagline": "One fox against a gaggle of geese — can the flock corner the predator?",
        "rules": {
            "objective": "Fox: eat enough geese to break the flock. Geese: hem the fox in so it cannot move.",
            "setup": "A cross-shaped board of 33 points. The fox starts on the central point; the thirteen geese fill the lower arm and the bottom of the crossbar.",
            "howToPlay": [
                "Geese move one step along a line to an adjacent empty point, but never backwards toward their own end — they advance to surround.",
                "The fox moves one step along a line in any direction, and captures by jumping an adjacent goose to the empty point beyond, removing it (jumps may chain).",
                "Players alternate; the geese move as a flock, one goose per turn.",
            ],
            "winning": "The fox wins if it captures so many geese that they can no longer trap it; the geese win by penning the fox so it has no move.",
            "variants": [
                "Flocks of 13, 15 or 17 geese tune the balance; more geese favour the flock.",
                "Asalto / officers-and-sepoys is a 19th-century military restyling of the same game.",
            ],
        },
        "context": {
            "period": "Northern Europe, medieval onward",
            "blurb": (
                "Fox and geese is the western survivor of the asymmetric hunt games, kin to "
                "hnefatafl and named (as halatafl) in the 14th-century Icelandic Grettis saga. A "
                "single fox tries to thin a flock of geese by leaping them, while the geese, who "
                "cannot capture at all, must use their numbers to corner it. Edward IV of England "
                "owned silver foxes and geese; the cross-shaped board is the same one later used "
                "for peg solitaire."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
            ],
        },
        "board": _cross,
        "pieces": [gp("fox", "Fox", "🦊"), disc("goose", "Goose", ALBUM)],
        "setup": (
            [at("fox", _crossn, 3, 3)]
            + [at("goose", _crossn, c, r) for (c, r) in
               [(2, 5), (3, 5), (4, 5), (2, 6), (3, 6), (4, 6),
                (0, 4), (1, 4), (5, 4), (6, 4), (2, 4), (3, 4), (4, 4)]]
        ),
        "turns": {"players": ["Geese", "Fox"], "track": True},
    },

    # =================== RACE & TABLES =====================================
    {
        "id": "senet", "name": "Senet", "native": "znt",
        "aka": ["Passing", "The game of thirty squares"], "category": "race",
        "origin": "Ancient Egypt", "region": "Africa", "era": "by c. 3100 BCE",
        "players": "2", "duration": "15–30 min", "wp": "Senet", "reconstruction": True,
        "tagline": "Humanity's oldest board game — race your pieces past the houses of the dead.",
        "rules": {
            "objective": "Be the first to move all your pieces along the thirty squares and bear them off the board.",
            "setup": "Three rows of ten squares, run in a boustrophedon S. Each player has five pieces (cones vs spools), placed alternately on the opening squares. Throw four casting sticks for movement.",
            "howToPlay": [
                "Cast the four two-sided sticks: count the light faces up (0–4); a throw of 0 counts as 5 and grants another throw, as do 1 and 4 in most reconstructions.",
                "Move one piece forward by the throw along the S-path. You may not land on your own piece.",
                "Landing on a lone enemy piece swaps places with it. Two friendly pieces in a row are a blockade; three cannot be passed.",
                "The marked 'houses' near the end are special: the House of Water (square 27) sends a piece back; the last squares require exact or favourable throws to exit.",
            ],
            "winning": "The first player to bear off all five pieces wins — and, the Egyptians believed, passes safely into the afterlife.",
            "variants": [
                "The number of starting pieces (five or seven) and the exact powers of the end squares differ between reconstructions.",
            ],
        },
        "context": {
            "period": "Egypt, Predynastic to the end of the New Kingdom (c. 3100–1100 BCE)",
            "blurb": (
                "Senet — 'passing' — is the oldest known board game, played in Egypt for over "
                "three thousand years. Boards appear in Predynastic graves and painted on tomb "
                "walls; Queen Nefertari is shown playing alone in her tomb. By the New Kingdom it "
                "had become a journey of the soul through the underworld, the squares standing for "
                "perils of the afterlife. No rulebook survives, so the play below is a modern "
                "reconstruction (chiefly Timothy Kendall's and R. C. Bell's) — honest guesswork "
                "built on the boards and the funerary texts."
            ),
            "sources": [
                "Kendall, T. (1978). Passing Through the Netherworld: The Meaning and Play of Senet.",
                "Piccione, P. A. (1980). 'In Search of the Meaning of Senet.' Archaeology 33.",
            ],
        },
        "board": board_senet(),
        "pieces": [gp("cone", "Cone (player 1)", "▲", color=ALBUM, bg=NIGER),
                   gp("spool", "Spool (player 2)", "●", color=NIGER, bg=ALBUM)],
        "setup": ([at("cone", _senet_norm, c, 0) for c in range(0, 10, 2)]
                  + [at("spool", _senet_norm, c, 0) for c in range(1, 10, 2)]),
        "dice": [{"id": "sticks", "label": "Casting sticks", "glyph": "🥢", "count": 4,
                  "faces": [{"label": "▽ dark", "value": 0}, {"label": "△ light", "value": 1}]}],
        "turns": {"players": ["Cones", "Spools"], "track": True},
    },
    {
        "id": "royal-game-of-ur", "name": "The Royal Game of Ur", "native": "Twenty Squares",
        "aka": ["Game of Twenty Squares", "Aseb"], "category": "race",
        "origin": "Sumer (Ur, Mesopotamia)", "region": "West Asia", "era": "c. 2600 BCE",
        "players": "2", "duration": "15–30 min", "wp": "Royal Game of Ur", "reconstruction": True,
        "tagline": "A 4,600-year-old race whose rules were read off a Babylonian clay tablet.",
        "rules": {
            "objective": "Race all seven of your pieces along the track and off the board before your opponent.",
            "setup": "The 20-square board: a block of twelve squares, a tail of six, joined by a bridge of two, with five rosette squares. Each player has seven pieces, entering from off the board. Roll four tetrahedral dice.",
            "howToPlay": [
                "Roll the four pyramidal dice and count the marked corners that land up (0–4). That is your move.",
                "Bring a new piece on, or advance one already on the track, by the dice count.",
                "Land on a rosette square to be safe and to roll again. Land on a lone enemy piece on the shared middle lane to send it back to the start.",
                "Two pieces cannot share a square; you must be able to make the full move or forfeit it.",
            ],
            "winning": "The first player to bear all seven pieces off the far end wins.",
            "variants": [
                "Finkel's tablet records a richer scoring game with lettered squares; the race above is the popular streamlined form.",
            ],
        },
        "context": {
            "period": "Mesopotamia, Early Dynastic period, c. 2600 BCE",
            "blurb": (
                "The Royal Game of Ur takes its name from the spectacular inlaid boards Leonard "
                "Woolley dug from the royal cemetery of Ur in the 1920s. For decades nobody knew "
                "how it was played — until Irving Finkel of the British Museum deciphered a "
                "Babylonian clay tablet of c. 177 BCE written by the scribe Itti-Marduk-balāṭu, "
                "which lays out the rules. It is a race game of two sets of seven pieces on four "
                "tetrahedral dice, with lucky rosette squares. We still flag it 'reconstruction': "
                "the tablet is late and leaves room for interpretation."
            ),
            "sources": [
                "Finkel, I. L. (2007). 'On the Rules for the Royal Game of Ur', in Ancient Board Games in Perspective. British Museum.",
                "Woolley, C. L. (1934). Ur Excavations II: The Royal Cemetery.",
            ],
        },
        "board": _ur,
        "pieces": [disc("w", "White piece", ALBUM), disc("b", "Black piece", NIGER)],
        "setup": [],
        "dice": [{"id": "pyramids", "label": "Tetrahedral dice", "glyph": "🔺", "count": 4,
                  "faces": [{"label": "• marked", "value": 1}, {"label": "○ plain", "value": 0}]}],
        "turns": {"players": ["White", "Black"], "track": True},
    },
    {
        "id": "tabula", "name": "Tabula", "native": "Tabula",
        "aka": ["Alea"], "category": "race",
        "origin": "Late Roman Empire", "region": "Europe", "era": "c. 1st–6th c. CE",
        "players": "2", "duration": "15–30 min", "wp": "Tabula (game)", "reconstruction": False,
        "tagline": "The direct ancestor of backgammon — race fifteen men home on three dice.",
        "rules": {
            "objective": "Be the first to move all fifteen of your men around the board and bear them all off.",
            "setup": "A board of twenty-four points in two tables. Each player has fifteen men, entered at the start point and travelling the same direction around the board.",
            "howToPlay": [
                "Roll the three dice (tesserae). Move men forward by each die value — three separate moves.",
                "More than one of your own men may share (and so hold) a point.",
                "A point held by two or more enemy men is blocked; you cannot land there.",
                "Land a single man alone on a point and an arriving enemy can hit it — the hit man re-enters.",
                "Once all your men are in the final quarter, you may bear them off.",
            ],
            "winning": "The first player to bear off all fifteen men wins. The emperor Zeno is recorded losing a famously bad throw mid-game in 480 CE.",
            "variants": [
                "Two dice instead of three for a faster, backgammon-like game.",
            ],
        },
        "context": {
            "period": "Later Roman Empire, c. 1st–6th c. CE",
            "blurb": (
                "Tabula ('the board') is the immediate ancestor of backgammon: two players, "
                "fifteen men each, three six-sided dice, racing around twenty-four points. We "
                "know it unusually well because of a single game — an epigram in the Greek "
                "Anthology records the exact disastrous throw the emperor Zeno made around "
                "480 CE, point by point, the best-attested individual game from antiquity."
            ),
            "sources": [
                "Austin, R. G. (1934). 'Zeno's Game of τάβλη.' Journal of Hellenic Studies 54.",
                "Becq de Fouquières, L. (1873). Les Jeux des Anciens.",
            ],
        },
        "board": board_points(),
        "pieces": [disc("w", "Albus (white)", ALBUM), disc("b", "Ruber (red)", RUBER)],
        "setup": row("w", 15, 0.9, 0.06, 0.45) + row("b", 15, 0.1, 0.55, 0.94),
        "dice": [{"id": "tesserae", "label": "Tesserae", "glyph": "🎲", "sides": 6, "count": 3}],
        "turns": {"players": ["Albus", "Ruber"], "track": True},
    },
    {
        "id": "backgammon", "name": "Backgammon", "native": "نرد Nard · تخته Tavla",
        "aka": ["Nard", "Tavli", "Tric-trac"], "category": "race",
        "origin": "Persia & the medieval world", "region": "West Asia", "era": "c. 800 CE onward",
        "players": "2", "duration": "15–30 min", "wp": "Backgammon", "reconstruction": False,
        "tagline": "Tabula's descendant, perfected in Persia — two dice, the doubling cube, and centuries of taverns.",
        "rules": {
            "objective": "Move all fifteen of your checkers into your home board and bear them off before your opponent.",
            "setup": "Twenty-four points in four quarters, the checkers in the standard opening array (use 'Load sample layout'). The two players move their checkers in opposite directions.",
            "howToPlay": [
                "Roll two dice; move one checker for each die, or one checker by both in turn. Doubles are played four times.",
                "You may only land on an open point — one not held by two or more enemy checkers.",
                "Land alone on a 'blot' and the enemy can hit it, sending your checker to the bar to re-enter.",
                "When all your checkers are home, bear them off by exact or higher rolls.",
            ],
            "winning": "First to bear off all fifteen checkers wins; a 'gammon' or 'backgammon' doubles or triples the stake, raised further by the doubling cube.",
            "variants": [
                "Nard, tavla and tric-trac are regional cousins with their own opening rules.",
            ],
        },
        "context": {
            "period": "Sasanian Persia onward; modern doubling cube added in 1920s New York",
            "blurb": (
                "Backgammon descends straight from Roman tabula by way of Sasanian Persia, where "
                "the game nard (nard-shir) is celebrated in the Middle Persian text 'The Explanation "
                "of Chess and the Invention of Backgammon' as a model of fate and free will. It "
                "spread under Islam as an, in Spain as tablas (in Alfonso X's book of games), and "
                "across Europe as tric-trac and tables. The doubling cube, the one truly modern "
                "addition, was invented in 1920s New York."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Alfonso X (1283). Libro de los juegos.",
            ],
        },
        "board": board_points(),
        "pieces": [disc("w", "White checker", ALBUM), disc("b", "Black checker", NIGER)],
        "setup": row("w", 15, 0.9, 0.06, 0.45) + row("b", 15, 0.1, 0.55, 0.94),
        "dice": [{"id": "dice", "label": "Dice", "glyph": "🎲", "sides": 6, "count": 2}],
        "turns": {"players": ["White", "Black"], "track": True},
    },
    {
        "id": "pachisi", "name": "Pachisi", "native": "पचीसी",
        "aka": ["Chaupar", "Twenty-five", "Royal Ludo"], "category": "race",
        "origin": "India (Mughal era and earlier)", "region": "South Asia", "era": "by c. 6th c. CE",
        "players": "2–4", "duration": "30–60 min", "wp": "Pachisi", "reconstruction": False,
        "tagline": "India's great cross-and-circle race — Akbar is said to have played it with living pieces.",
        "rules": {
            "objective": "Race your four pieces out from home, around the cross-shaped track, and back into the central charkoni before your partners' opponents do.",
            "setup": "A cloth cross of four arms around a central home square. Four players (often as two partnerships) each take four pieces. Throw six or seven cowrie shells for movement.",
            "howToPlay": [
                "Throw the cowries and count the shells that fall mouth-up; special counts (e.g. all up) grant a bonus move and another throw.",
                "Move a piece down its arm, anticlockwise around the outer track, and up the middle of its own arm to home.",
                "Two of your pieces on a square form a block; landing on an enemy on an unprotected square sends it back to start.",
                "The rosette 'castle' squares are safe — no piece may be captured there.",
            ],
            "winning": "The first player (or partnership) to bring all their pieces home wins.",
            "variants": [
                "Chaupar uses three long dice instead of cowries; the modern board game Ludo is a simplified pachisi.",
            ],
        },
        "context": {
            "period": "India, medieval through Mughal era",
            "blurb": (
                "Pachisi — from pachīs, 'twenty-five', the best throw of the cowries — is the "
                "national cross-and-circle race game of India and the ancestor of Ludo and Parcheesi. "
                "The Mughal emperor Akbar is famously said to have laid out a giant pachisi court "
                "at Fatehpur Sikri and played with sixteen slave girls as the pieces. Played on an "
                "embroidered cloth, with partners sitting crosswise, it is as much a social ritual "
                "as a race."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Culin, S. (1898). Chess and Playing Cards.",
            ],
        },
        "board": board_cross_circle(),
        "pieces": [disc("y", "Yellow", "#d8a73a"), disc("g", "Green", GREEN),
                   disc("r", "Red", RUBER), disc("k", "Black", NIGER)],
        "setup": [],
        "dice": [{"id": "cowries", "label": "Cowrie shells", "glyph": "🐚", "count": 6,
                  "faces": [{"label": "◡ up", "value": 1}, {"label": "● down", "value": 0}]}],
        "turns": {"players": ["Yellow", "Green", "Red", "Black"], "track": True},
    },
    {
        "id": "patolli", "name": "Patolli", "native": "patōlli",
        "aka": ["The bean game"], "category": "race",
        "origin": "Mesoamerica (Aztec, Maya)", "region": "Mesoamerica", "era": "by c. 200 CE",
        "players": "2–4", "duration": "20–40 min", "wp": "Patolli", "reconstruction": True,
        "tagline": "The Aztec race played for stakes — and watched over by Macuilxochitl, god of games.",
        "rules": {
            "objective": "Race your six stones around the X-shaped track from your entry to the far end and back, before your opponent — winning the other's wagered goods.",
            "setup": "A cross/X board of squares with marked entry and exit squares. Each player has six coloured stones and a stake of beans, jade or blankets. Throw five marked beans for movement.",
            "howToPlay": [
                "Throw the five pierced beans and count the marked faces up (1–5); a throw of zero marks (all blank) is special, often forfeiting the turn.",
                "Enter and advance a stone along your arms of the cross by the count.",
                "Landing on certain squares wins a stake from each opponent or sends a stone back; the central and end squares are dangerous.",
            ],
            "winning": "The first to run all six stones home takes the pot. Aztecs bet heavily — sometimes their own freedom — on the result.",
            "variants": [
                "Boards of differing arm lengths and bean counts appear across Mesoamerica; the exact path and scoring are reconstructed.",
            ],
        },
        "context": {
            "period": "Mesoamerica, Classic period through the Aztec empire",
            "blurb": (
                "Patolli was the great gambling race game of Mesoamerica, played from at least the "
                "Classic Maya period and described by Spanish chroniclers — Diego Durán, Sahagún — "
                "at the Aztec court, where players invoked Macuilxochitl, the god of games, and "
                "carried their marked beans in a special pouch. Stakes were real and ruinous. The "
                "Spanish suppressed it as idolatrous, burning boards and beans, so its exact rules "
                "are partly reconstructed from the codices and chronicles — hence our flag."
            ),
            "sources": [
                "Durán, D. (1581). Historia de las Indias de Nueva España.",
                "Tylor, E. B. (1879). 'On the Game of Patolli in Ancient Mexico.' JRAI.",
            ],
        },
        "board": board_patolli(),
        "pieces": [disc("a", "Blue stones", BLUE), disc("b", "Red stones", RUBER),
                   disc("c", "Green stones", GREEN), disc("d", "Yellow stones", "#d8a73a")],
        "setup": [],
        "dice": [{"id": "beans", "label": "Marked beans", "glyph": "🫘", "count": 5,
                  "faces": [{"label": "• marked", "value": 1}, {"label": "blank", "value": 0}]}],
        "turns": {"players": ["Blue", "Red", "Green", "Yellow"], "track": True},
    },
    {
        "id": "game-of-the-goose", "name": "The Game of the Goose", "native": "Gioco dell'Oca",
        "aka": ["Juego de la Oca", "Jeu de l'Oie"], "category": "race",
        "origin": "Renaissance Italy", "region": "Europe", "era": "by c. 1580 CE",
        "players": "2–6", "duration": "15–30 min", "wp": "Game of the Goose", "reconstruction": False,
        "tagline": "The first commercial board game — a spiral of sixty-three squares, pure luck and peril.",
        "rules": {
            "objective": "Be the first to land exactly on square 63, the garden at the centre of the spiral.",
            "setup": "A spiral track of 63 numbered squares. Each player has one marker and starts off the board. Two dice drive the race.",
            "howToPlay": [
                "Roll the two dice and advance your marker by the total.",
                "Land on a goose square and move forward again by the same throw — geese speed you on.",
                "Beware the hazards: the bridge (6) jumps you ahead, but the well (31), the maze (42), the prison (52) and death (58) hold you, send you back, or restart you.",
                "Square 63 must be reached exactly; overshoot and you count back from the end.",
            ],
            "winning": "The first marker to rest exactly on square 63 wins the pot.",
            "variants": [
                "Countless themed re-skins exist (royal, geographic, moral); the structure is always the spiral and the geese.",
            ],
        },
        "context": {
            "period": "Italy, later 16th century, then all of Europe",
            "blurb": (
                "The Game of the Goose is the prototype of the published board game. A spiral race "
                "of 63 squares driven purely by dice, it spread across Europe after Francesco I "
                "de' Medici reportedly sent a set to Philip II of Spain around 1580. Cheap printed "
                "sheets made it the first mass-market game, and its skeleton — a numbered track "
                "with shortcuts and penalties — underlies Snakes and Ladders and a thousand "
                "children's games since."
            ),
            "sources": [
                "Seville, A. (2019). The Cultural Legacy of the Royal Game of the Goose.",
                "Whitehouse, F. R. B. (1951). Table Games of Georgian and Victorian Days.",
            ],
        },
        "board": board_goose(),
        "pieces": [disc("a", "Red marker", RUBER), disc("b", "Blue marker", BLUE),
                   disc("c", "Green marker", GREEN), disc("d", "Gold marker", GOLD)],
        "setup": [],
        "dice": [{"id": "dice", "label": "Dice", "glyph": "🎲", "sides": 6, "count": 2}],
        "turns": {"players": ["Red", "Blue", "Green", "Gold"], "track": True},
    },

    # =================== SOWING (MANCALA) ==================================
    {
        "id": "oware", "name": "Oware", "native": "Oware / Awalé",
        "aka": ["Wari", "Awalé", "Ayò", "Awele"], "category": "sowing",
        "origin": "Akan peoples (Ghana)", "region": "Africa", "era": "traditional",
        "players": "2", "duration": "10–20 min", "wp": "Oware", "reconstruction": False,
        "tagline": "West Africa's great game of sowing — scatter seeds and reap your opponent's row.",
        "rules": {
            "objective": "Capture more than half of the 48 seeds.",
            "setup": "Two rows of six pits, with a store at each end. Each of the twelve pits starts with four seeds.",
            "howToPlay": [
                "On your turn, lift all the seeds from one of your own pits and 'sow' them one by one into the following pits, going anticlockwise.",
                "If your last seed drops into an enemy pit making its count two or three, you capture those seeds — and any unbroken run of twos and threes behind it in the enemy row.",
                "You must, where possible, play a move that leaves the opponent at least one seed (you may not starve them).",
            ],
            "winning": "When seeds run low or a position repeats, each player takes the seeds on their side; whoever holds more than 24 wins.",
            "variants": [
                "Regional rules differ on capturing, 'grand slams', and starvation; agree yours first.",
            ],
        },
        "context": {
            "period": "West Africa, traditional (and across the diaspora)",
            "blurb": (
                "Oware — awalé in French-speaking West Africa, wari in the Caribbean — is the best "
                "known of the hundreds of mancala 'sowing' games played across Africa and Asia. "
                "Among the Akan of Ghana it carries proverbs and rituals; carved oware boards are a "
                "signature craft. Despite its bare equipment — two rows of holes and forty-eight "
                "seeds — it is a game of deep calculation, and one of the very few traditional games "
                "to have been weakly solved by computer."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Russ, L. (2000). The Complete Mancala Games Book.",
            ],
        },
        "board": board_mancala(6, 2),
        "pieces": [disc("seed", "Seed", "#6b4a2a")],
        "setup": [],
        "turns": {"players": ["South", "North"], "track": True},
    },
    {
        "id": "bao", "name": "Bao", "native": "Bao la Kiswahili",
        "aka": ["Bawo", "Bao la kiswahili"], "category": "sowing",
        "origin": "Swahili coast (East Africa)", "region": "Africa", "era": "traditional",
        "players": "2", "duration": "20–45 min", "wp": "Bao (game)", "reconstruction": False,
        "tagline": "The deepest mancala of all — four rows, a special house, and a master's reputation at stake.",
        "rules": {
            "objective": "Empty your opponent's front row, or leave them with no legal move.",
            "setup": "Four rows of eight pits — two rows each side. Each player has a special pit, the nyumba ('house'). The opening (the namua phase) feeds seeds in from a reserve in a prescribed way.",
            "howToPlay": [
                "Lift the seeds from a pit and sow them around your two rows; a sowing that ends in a non-empty pit continues, relay-fashion.",
                "When a sowing ends in an occupied front-row pit facing enemy seeds, you capture the opposing seeds and re-sow them on your own side.",
                "The nyumba and the two-phase structure (namua, then mtaji) give bao its famous depth.",
            ],
            "winning": "You win by capturing or starving the opponent's front row so they cannot move.",
            "variants": [
                "Bao la kiswahili (the full game) vs the simpler bao la kujifunza ('bao for learning').",
            ],
        },
        "context": {
            "period": "East Africa, Swahili coast, traditional",
            "blurb": (
                "Bao — Swahili for 'board' — is the prestige mancala of the East African coast, "
                "Zanzibar, Tanzania and the Comoros, played on a four-row board often beautifully "
                "carved. It is widely regarded as the most complex traditional sowing game: a relay "
                "of cascading captures across two phases that masters (bingwa) study for years. "
                "Tournaments and a respected oral theory surround it; to be a great bao player is a "
                "mark of real standing."
            ),
            "sources": [
                "Townshend, P. (1979). 'Bao (Mankala): The Swahili Ethic in African Idiom.'",
                "de Voogt, A. (1995). Limits of the Mind: Towards a Characterisation of Bao Mastership.",
            ],
        },
        "board": board_mancala(8, 4, stores=False, special={(3, 1), (4, 2)}),
        "pieces": [disc("seed", "Seed (kete)", "#6b4a2a")],
        "setup": [],
        "turns": {"players": ["South", "North"], "track": True},
    },
    {
        "id": "toguz-korgool", "name": "Toguz Korgool", "native": "тогуз коргоол",
        "aka": ["Toguz kumalak", "Nine pebbles"], "category": "sowing",
        "origin": "Kyrgyz & Kazakh Central Asia", "region": "Central Asia", "era": "traditional",
        "players": "2", "duration": "20–40 min", "wp": "Toguz korgool", "reconstruction": False,
        "tagline": "The steppe's national mancala — nine pits, nine pebbles, and a 'mother hole' you can seize.",
        "rules": {
            "objective": "Gather more than half of the 162 pebbles into your kazan (store).",
            "setup": "Two rows of nine pits, each starting with nine pebbles, plus a large kazan for each player.",
            "howToPlay": [
                "Lift a pit's pebbles and sow them one per pit anticlockwise; the first pebble drops in the SAME pit you lifted from (unless it held one pebble, which simply moves on).",
                "If your last pebble lands in an enemy pit making its count even, you capture all the pebbles in it to your kazan.",
                "If it makes an enemy pit hold exactly three, you may claim that pit as a tuz ('mother hole') — thereafter every pebble that lands there is yours.",
            ],
            "winning": "When the board empties, whoever has more than 81 pebbles in their kazan wins.",
            "variants": [
                "Kazakh toguz kumalak is the same game; both have national federations and tournaments.",
            ],
        },
        "context": {
            "period": "Central Asia, traditional (Kyrgyzstan, Kazakhstan)",
            "blurb": (
                "Toguz korgool ('nine pebbles') — toguz kumalak in Kazakh — is the national mancala "
                "of the Central Asian steppe, an old herders' game now backed by state federations, "
                "world championships and even satellite-broadcast matches. Its signature is the tuz, "
                "a captured 'mother hole' that keeps paying out, and a count deep enough that strong "
                "players calculate long sowing chains in their heads. It is inscribed on UNESCO's "
                "intangible-heritage lists."
            ),
            "sources": [
                "Russ, L. (2000). The Complete Mancala Games Book.",
                "UNESCO (2020). Togyzqumalaq / Toguz korgool, intangible cultural heritage nomination.",
            ],
        },
        "board": board_mancala(9, 2),
        "pieces": [disc("seed", "Pebble (korgool)", "#6b4a2a")],
        "setup": [],
        "turns": {"players": ["South", "North"], "track": True},
    },

    # =================== ALIGNMENT (MORRIS) ================================
    {
        "id": "nine-mens-morris", "name": "Nine Men's Morris", "native": "Merels / Mühle",
        "aka": ["Merels", "Mühle", "Cowboy checkers"], "category": "alignment",
        "origin": "Roman & medieval Europe", "region": "Europe", "era": "by c. 1st c. CE",
        "players": "2", "duration": "10–20 min", "wp": "Nine men's morris", "reconstruction": False,
        "tagline": "Form a mill of three and pluck an enemy off — the great medieval line game.",
        "rules": {
            "objective": "Reduce your opponent to two pieces, or leave them unable to move.",
            "setup": "Three concentric squares joined at the side midpoints — 24 points in all. Each player has nine pieces, all off the board to start.",
            "howToPlay": [
                "First, take turns placing your nine pieces one at a time on empty points.",
                "Then take turns moving a piece along a line to an adjacent empty point.",
                "Whenever you form a 'mill' — three of your pieces in a line — remove one enemy piece not itself in a mill.",
                "A player reduced to three pieces may 'fly' to any empty point.",
            ],
            "winning": "Win by reducing the opponent to two pieces or by blocking all their moves.",
            "variants": [
                "Three, six and twelve men's morris vary the board and piece count; twelve adds the diagonals.",
            ],
        },
        "context": {
            "period": "Roman world onward; ubiquitous in medieval Europe",
            "blurb": (
                "Nine men's morris — merels, mill, mühle — is the classic line-and-capture game of "
                "the western world. Boards are cut into Roman tiles, into the cloister seats of "
                "English cathedrals, into ship timbers and tavern benches across medieval Europe. "
                "Shakespeare names it: 'the nine men's morris is filled up with mud.' Simple to "
                "learn and sharp to master, it has been weakly solved — perfect play is a draw."
            ),
            "sources": [
                "Murray, H. J. R. (1952). A History of Board-Games Other Than Chess. Oxford.",
                "Shakespeare, W. A Midsummer Night's Dream II.i.",
            ],
        },
        "board": board_nine_morris(),
        "pieces": [disc("w", "White", ALBUM), disc("b", "Black", NIGER)],
        "setup": [],
        "turns": {"players": ["White", "Black"], "track": True},
    },
    {
        "id": "terni-lapilli", "name": "Terni Lapilli", "native": "Terni lapilli",
        "aka": ["Three men's morris", "Roman three-in-a-row", "Tic-tac-toe's elder"], "category": "alignment",
        "origin": "Ancient Rome (and worldwide)", "region": "Europe", "era": "1st–5th c. CE",
        "players": "2", "duration": "5 min", "wp": "Three men's morris", "reconstruction": False,
        "tagline": "Three pebbles in a row, scratched on a thousand steps from Rome to China.",
        "rules": {
            "objective": "Make a straight line of your three pieces along any row, column or diagonal.",
            "setup": "An empty board of nine points. Each player has three pieces.",
            "howToPlay": [
                "Take turns placing one of your three pieces on any empty point.",
                "When all six pieces are down, take turns moving one piece along a line to an adjacent empty point.",
                "Keep manoeuvring until someone lines up three.",
            ],
            "winning": "Three of your pieces in a straight line wins at once.",
            "variants": [
                "Allow a piece to move to any empty point for a faster game.",
                "Played without the moving phase it becomes simple noughts and crosses.",
            ],
        },
        "context": {
            "period": "Roman Empire, ubiquitous 1st–5th c. CE",
            "blurb": (
                "Terni lapilli — 'three little stones' — is Rome's three men's morris, mentioned by "
                "Ovid as a game a fashionable woman should know. Its boards are among the commonest "
                "ancient graffiti, scratched into the steps of the Forum and pavements across the "
                "empire. Near-identical three-in-a-row games appear independently worldwide, from "
                "the Chinese luk tsut k'i to boards in Sri Lanka and the Americas — perhaps the most "
                "universal board game of all."
            ),
            "sources": [
                "Ovid, Ars Amatoria III.365–366.",
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
            ],
        },
        "board": board_morris(),
        "pieces": [disc("a", "Album (bone)", ALBUM), disc("r", "Ruber (terracotta)", RUBER)],
        "setup": [],
        "turns": {"players": ["Album", "Ruber"], "track": True},
    },
    {
        "id": "mu-torere", "name": "Mū Tōrere", "native": "Mū tōrere",
        "aka": ["Maori star game"], "category": "alignment",
        "origin": "Māori (Aotearoa / New Zealand)", "region": "Pacific", "era": "traditional",
        "players": "2", "duration": "5–10 min", "wp": "Mū tōrere", "reconstruction": False,
        "tagline": "The only board game the Māori are known to have played — block your foe on an eight-pointed star.",
        "rules": {
            "objective": "Leave your opponent with no legal move.",
            "setup": "An eight-pointed star: eight outer points (kewai) around a central point (putahi). Each player has four pieces; one player's four fill four adjacent kewai, the other's the opposite four.",
            "howToPlay": [
                "On your turn move one piece to an empty adjacent point — along the star to a neighbouring kewai, in to the putahi, or out from the putahi.",
                "A piece may only move to the centre if at least one of its neighbours is an enemy piece (a rule that keeps the game from stalling).",
                "There is no capture; the whole game is the squeeze.",
            ],
            "winning": "You win when your opponent cannot move on their turn.",
            "variants": [
                "Larger stars (more kewai) are sometimes used to lengthen the game.",
            ],
        },
        "context": {
            "period": "Aotearoa / New Zealand, pre-European and traditional",
            "blurb": (
                "Mū tōrere is the one board game indigenous to the Māori, played on an eight-pointed "
                "star carved in wood or scratched on the ground, with pebbles or beans for pieces. "
                "Ethnographer Elsdon Best recorded it among the Ngāti Porou and other east-coast "
                "iwi. It looks trivial and is not: a small, elegant blocking game that has attracted "
                "mathematical analysis showing the first player cannot force a win on the standard "
                "board."
            ),
            "sources": [
                "Best, E. (1925). Games and Pastimes of the Maori.",
                "Straffin, P. D. (1995). 'Position Graphs for Pong Hau K'i and Mu Torere.'",
            ],
        },
        "board": board_mu_torere(),
        "pieces": [disc("a", "Player one", ALBUM), disc("b", "Player two", NIGER)],
        "setup": [],
        "turns": {"players": ["Tahi", "Rua"], "track": True},
    },
    {
        "id": "rota", "name": "Rota", "native": "Rota",
        "aka": ["The wheel", "Roman round merels"], "category": "alignment",
        "origin": "Ancient Rome", "region": "Europe", "era": "late antiquity",
        "players": "2", "duration": "5 min", "wp": "Rota (game)", "reconstruction": True,
        "tagline": "A wheel of eight spokes — the round cousin of three-in-a-row.",
        "rules": {
            "objective": "Line up your three pieces through the hub of the wheel.",
            "setup": "A wheel with eight points on the rim and one at the centre, joined by spokes. Each player has three pieces.",
            "howToPlay": [
                "Take turns placing your three pieces on empty points.",
                "Then take turns sliding a piece along a line (spoke or rim) to the next empty point.",
                "A line of three must pass through the central hub to count.",
            ],
            "winning": "Three in a row through the centre wins.",
            "variants": [
                "A common handicap lets only the second player occupy the centre first, balancing the strong opening.",
            ],
        },
        "context": {
            "period": "Roman Empire, late antiquity",
            "blurb": (
                "Rota — Latin for 'wheel' — is a circular three-in-a-row game known from "
                "wheel-shaped boards scratched in Roman pavements, including at Ostia. Eight rim "
                "points and a central hub make it a round relative of terni lapilli. As with most "
                "of these scratched games no rulebook survives, so the moves here are a sensible "
                "modern reconstruction."
            ),
            "sources": [
                "Bell, R. C. (1979). Board and Table Games from Many Civilizations. Dover.",
            ],
        },
        "board": board_wheel(),
        "pieces": [disc("a", "Album (bone)", ALBUM), disc("r", "Ruber (terracotta)", RUBER)],
        "setup": [],
        "turns": {"players": ["Album", "Ruber"], "track": True},
    },

    # =================== DICE & LOTS =======================================
    {
        "id": "tali", "name": "Tali", "native": "Tali / ἀστράγαλοι",
        "aka": ["Astragali", "Knucklebones"], "category": "dice",
        "origin": "Greece & Rome", "region": "Europe", "era": "archaic through late antiquity",
        "players": "2+", "duration": "10 min", "wp": "Astragalus (game)", "reconstruction": False,
        "tagline": "Four knucklebones, four faces — throw for the Venus and avoid the Dog.",
        "rules": {
            "objective": "Throw the best combination of the four tali — and win the stakes.",
            "setup": "Four tali (sheep or goat knucklebones). Each lands on one of four faces, valued 1, 3, 4 and 6 (the two narrow ends never settle). Put up a wager.",
            "howToPlay": [
                "Each player in turn throws all four tali, from the hand or a fritillus (dice-cup).",
                "Read the four faces. Special named throws beat any plain total.",
                "The Venus (iactus Venereus) — all four faces different (1·3·4·6) — is the best throw of all.",
                "The Dog (canis) — all four showing 1 — is the worst.",
            ],
            "winning": "Best throw takes the pot; play to an agreed number of rounds or until the stakes run out.",
            "variants": [
                "Children played a skill version (like jacks): toss and catch the bones on the back of the hand.",
            ],
        },
        "context": {
            "period": "Greek & Roman, archaic through late antiquity",
            "blurb": (
                "Tali (Greek astragaloi) were knucklebones — the small ankle bones of sheep or "
                "goats — used as four-sided dice valued 1, 3, 4 and 6. The throw of four different "
                "faces was the 'Venus', the luckiest; four ones the 'Dog', the worst. Augustus "
                "mentions losing happily at tali in a letter quoted by Suetonius. Bronze, glass and "
                "crystal tali survive, and children played a skill game of toss-and-catch with the "
                "same bones across the ancient world."
            ),
            "sources": [
                "Suetonius, Divus Augustus 71.",
                "Becq de Fouquières, L. (1873). Les Jeux des Anciens.",
            ],
        },
        "board": board_table("VENVS"),
        "pieces": [gp("stake", "Denarius (stake)", "✸", color=GOLD, bg="#3a2c1a")],
        "setup": [],
        "dice": [{"id": "tali", "label": "Tali", "glyph": "🦴", "count": 4,
                  "faces": [{"label": "I", "value": 1}, {"label": "III", "value": 3},
                            {"label": "IV", "value": 4}, {"label": "VI", "value": 6}]}],
        "turns": {"track": True},
    },
    {
        "id": "hazard", "name": "Hazard", "native": "Hazard / az-zahr",
        "aka": ["Hasard", "Ancestor of craps"], "category": "dice",
        "origin": "Medieval Arabic & European world", "region": "West Asia", "era": "by c. 14th c. CE",
        "players": "2+", "duration": "10 min", "wp": "Hazard (game)", "reconstruction": False,
        "tagline": "The great gambling dice game of the medieval tavern — Chaucer's 'bones' and the parent of craps.",
        "rules": {
            "objective": "As the caster, win against the table by hitting your point before you 'throw out'.",
            "setup": "Two dice and a ring of bettors around the caster (the thrower). Stakes are placed.",
            "howToPlay": [
                "The caster first chooses or rolls a 'main' (a number from 5 to 9).",
                "He then throws: rolling the main is an instant win ('nick'); rolling 2 or 3 (or certain numbers) is an instant loss ('throws out').",
                "Otherwise the thrown total becomes his 'chance'; he keeps throwing until he repeats the chance (he wins) or repeats the main (he loses).",
            ],
            "winning": "The caster wins the stakes on a nick or by hitting his chance; the table wins when he throws out.",
            "variants": [
                "American sailors simplified hazard into craps; the odds language ('main', 'chance') survives in casino play.",
            ],
        },
        "context": {
            "period": "Medieval Arabic world and Europe; named in England by the 14th c.",
            "blurb": (
                "Hazard is the most important dice game of the European Middle Ages and the direct "
                "ancestor of craps. Its very name comes from the Arabic az-zahr, 'the die', and the "
                "game seems to have reached Europe from the Islamic world during the Crusades. "
                "Chaucer's Pardoner rails against the 'hazardours' who swear on the bones; for "
                "centuries it was THE game of soldiers, sailors and gentlemen's clubs alike, with an "
                "elaborate vocabulary of mains and chances."
            ),
            "sources": [
                "Chaucer, G. The Canterbury Tales, The Pardoner's Tale.",
                "Hoyle, E. (1750s). Hoyle's Games (rules of Hazard).",
            ],
        },
        "board": board_table("HAZARD"),
        "pieces": [gp("stake", "Stake", "✸", color=GOLD, bg="#3a2c1a")],
        "setup": [],
        "dice": [{"id": "dice", "label": "Dice", "glyph": "🎲", "sides": 6, "count": 2}],
        "turns": {"track": True},
    },
    {
        "id": "dreidel", "name": "Dreidel", "native": "סביבון Sevivon",
        "aka": ["Sevivon", "Put-and-take top"], "category": "dice",
        "origin": "Ashkenazi Jewish Europe", "region": "Europe", "era": "by c. 19th c. CE",
        "players": "2+", "duration": "10–20 min", "wp": "Dreidel", "reconstruction": False,
        "tagline": "A four-sided top spun at Hanukkah — nun, gimel, hey, shin: nothing, all, half, put in.",
        "rules": {
            "objective": "Win the whole pot of tokens (coins, nuts or chocolate gelt).",
            "setup": "A four-sided spinning top lettered נ ג ה ש. Each player antes one token into the centre pot.",
            "howToPlay": [
                "Spin the dreidel on your turn and act on the letter that lands up:",
                "נ Nun — nothing happens. ג Gimel — take the whole pot. ה Hey — take half the pot. ש Shin — put one token in.",
                "When the pot is empty or low, everyone antes again.",
            ],
            "winning": "Play until one player has won all the tokens.",
            "variants": [
                "The letters stand for nes gadol haya sham — 'a great miracle happened there' (in Israel, po, 'here').",
            ],
        },
        "context": {
            "period": "Ashkenazi Europe, popularised in the 19th century",
            "blurb": (
                "The dreidel (Yiddish; Hebrew sevivon) is a four-sided spinning top played at "
                "Hanukkah, a Jewish version of the European teetotum 'put-and-take' gambling tops "
                "(the German letters N-G-H-S once stood for Nichts, Ganz, Halb, Stell-ein). "
                "Reinterpreted as the initials of nes gadol haya sham — 'a great miracle happened "
                "there' — it became a children's holiday game, the chance of the spin standing in "
                "for the wonder of the festival."
            ),
            "sources": [
                "Trachtenberg, J. (1939). Jewish Magic and Superstition.",
                "Parlett, D. (1999). The Oxford History of Board Games.",
            ],
        },
        "board": board_table("נ ג ה ש"),
        "pieces": [gp("gelt", "Gelt (token)", "✸", color=GOLD, bg="#3a2c1a"),
                   gp("nut", "Nut", "🌰")],
        "setup": [],
        "dice": [{"id": "dreidel", "label": "Dreidel", "glyph": "🔄", "count": 1,
                  "faces": [{"label": "נ Nun — nothing"}, {"label": "ג Gimel — all"},
                            {"label": "ה Hey — half"}, {"label": "ש Shin — put in"}]}],
        "turns": {"track": True},
    },

    # =================== HAND & GUESS ======================================
    {
        "id": "morra", "name": "Morra", "native": "Morra / micatio",
        "aka": ["Micatio", "Mora", "Finger-flashing"], "category": "guessing",
        "origin": "Ancient Mediterranean", "region": "Europe", "era": "antiquity to today",
        "players": "2", "duration": "2 min", "wp": "Morra (game)", "reconstruction": False,
        "tagline": "Throw out fingers and shout the sum — the oldest hand game still played, from Rome to today.",
        "rules": {
            "objective": "Call the exact total of fingers both players will throw.",
            "setup": "Nothing but two hands. Players face off; agree the stake or the target score.",
            "howToPlay": [
                "On a count, both players simultaneously thrust out some fingers (0–5) and each shouts a number aloud — their guess at the sum of both hands.",
                "Reveal and add the fingers shown.",
                "A player who shouted the correct total scores a point (if both are right, or both wrong, no one scores).",
            ],
            "winning": "First to the agreed score (often 16) wins. The Romans had a proverb for an honest man: 'one you could play morra with in the dark'.",
            "variants": [
                "The Chinese drinking game huāquán and the Italian morra are essentially the same game.",
            ],
        },
        "context": {
            "period": "Mediterranean antiquity to the present day",
            "blurb": (
                "Morra — Roman micatio, 'flashing (the fingers)' — is one of the oldest games still "
                "played, shown on Egyptian tomb paintings and Greek vases and named throughout Latin "
                "literature. Two players simultaneously throw out fingers and call the total; "
                "lightning reflexes and bluff decide it. Cicero's test of an honest dealer was a man "
                "'with whom you could play micatio in the dark' — dignus quicum in tenebris mices. "
                "It is still played, loudly, across the Mediterranean."
            ),
            "sources": [
                "Cicero, De Officiis III.77.",
                "Becq de Fouquières, L. (1873). Les Jeux des Anciens.",
            ],
        },
        "board": board_table("MORRA"),
        "pieces": [gp("h1", "Player one's hand", "✋"), gp("h2", "Player two's hand", "🖐"),
                   gp("fist", "Fist (zero)", "✊")],
        "setup": [],
        "turns": {"players": ["Primus", "Secundus"], "track": True},
    },
    {
        "id": "par-impar", "name": "Par Impar", "native": "Par impar ludere",
        "aka": ["Odds and evens"], "category": "guessing",
        "origin": "Ancient Rome", "region": "Europe", "era": "all periods",
        "players": "2", "duration": "2 min", "wp": "Odds and evens (hand game)", "reconstruction": False,
        "tagline": "Odd or even? A fistful of nuts and a guess — the simplest wager of all.",
        "rules": {
            "objective": "Guess whether the hidden number of counters is odd or even.",
            "setup": "A handful of small counters — nuts, knucklebones or coins. One player is the hider.",
            "howToPlay": [
                "The hider conceals some counters in a closed fist.",
                "The guesser calls 'par!' (even) or 'impar!' (odd).",
                "Open the hand and count.",
                "A correct guess wins the counters or the stake; a wrong guess loses it. Swap roles and repeat.",
            ],
            "winning": "Play to an agreed pot or number of rounds; the richer hand wins.",
            "variants": [
                "Guess the exact number for a bigger payout.",
                "Roman children played it with walnuts.",
            ],
        },
        "context": {
            "period": "Roman, all periods — a children's and tavern game",
            "blurb": (
                "Par impar ludere — 'to play odds and evens' — needed nothing but a hand and a few "
                "nuts or coins. One player hid a number of counters in a fist and the other guessed "
                "odd or even. Suetonius lists it among the emperor Augustus' easy amusements, and it "
                "appears on wall paintings and in children's games with walnuts. It is the most "
                "minimal of all games — pure luck and a quick wager — and versions are played the "
                "world over."
            ),
            "sources": [
                "Suetonius, Divus Augustus 71.",
                "Ovid, Nux; Martial, Epigrams V.84.",
            ],
        },
        "board": board_table("PAR · IMPAR"),
        "pieces": [
            gp("nut", "Nut (counter)", "🌰"),
            gp("fist", "Closed fist", "✊"),
            gp("coin", "As (coin)", "✸", color=GOLD, bg="#3a2c1a"),
        ],
        "setup": [],
        "turns": {"players": ["Celator (hider)", "Coniector (guesser)"], "track": True},
    },
]


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------
def curated_records():
    out = []
    cat_labels = {c["key"]: c["label"] for c in CATEGORIES}
    for g in GAMES:
        rec = dict(g)
        rec["category_label"] = cat_labels.get(g["category"], g["category"])
        rules = dict(rec["rules"])
        rules.setdefault("players", rec.get("players", ""))
        rules.setdefault("duration", rec.get("duration", ""))
        rec["rules"] = rules
        out.append(rec)
    return out


def finalize():
    return {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "title": "Games of the Past",
        "categories": CATEGORIES,
        "footer": OHM_FOOTER,
        "games": curated_records(),
    }


def write_seed():
    SEED.parent.mkdir(parents=True, exist_ok=True)
    data = finalize()
    SEED.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {SEED.relative_to(ROOT)} — {len(data['games'])} games, "
          f"{len(data['categories'])} categories")
    by_cat = {}
    for g in data["games"]:
        by_cat.setdefault(g["category"], []).append(g)
    for c in CATEGORIES:
        gs = by_cat.get(c["key"], [])
        print(f"  {c['label']} ({len(gs)}):")
        for g in gs:
            flag = " [reconstruction]" if g.get("reconstruction") else ""
            print(f"    · {g['id']:<20} {g['origin']}{flag}")
    return data


if __name__ == "__main__":
    write_seed()
