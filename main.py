#!/usr/bin/env python3
"""news-image-20261117: one image summing up the world news of
Tuesday 17 November 2026, drawn procedurally with the standard library
only (no network, no external assets, fully deterministic).

The image is a one-page newspaper front page: masthead with the date,
a markets ticker, a lead story, a dotted world map with numbered
story markers, four more stories, and an IN BRIEF strip. It writes
the image to /output/entry.png ($MAKEFUN_OUTPUT_DIR outside the
grader). Running it twice writes byte-identical output.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (245, 240, 225)
INK = (20, 20, 20)
RED = (163, 22, 33)
NAVY = (31, 58, 95)
GRAY = (110, 108, 96)
SEA = (214, 226, 230)
LAND = (96, 88, 70)
WHITE = (255, 255, 255)

# ---------------------------------------------------------------- font
# Hand-built 5x7 bitmap capitals, digits and punctuation. Each glyph is
# 7 rows of 5 characters ('#' = ink, '.' = blank). All page text is set
# in capitals, which suits a newspaper front page.

FONT = {
    'A': ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '&': (".###.", "#...#", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    '=': (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    if not text:
        return 0
    return (len(text) * 6 - 1) * scale


# ---------------------------------------------------------------- image
class Image:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        r, g, b = color
        row = bytes([r, g, b]) * (x1 - x0)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + len(row)] = row

    def disc(self, cx, cy, radius, color):
        r, g, b = color
        rr = radius * radius
        for yy in range(cy - radius, cy + radius + 1):
            dy = yy - cy
            dx = int((rr - dy * dy) ** 0.5)
            x0 = max(0, cx - dx)
            x1 = min(self.w - 1, cx + dx)
            if yy < 0 or yy >= self.h or x1 < x0:
                continue
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0 + 1) * 3] = bytes([r, g, b]) * (x1 - x0 + 1)

    def ring(self, cx, cy, radius, thickness, color):
        for t in range(thickness):
            rr = radius - t
            steps = max(24, rr * 8)
            for i in range(steps):
                a = 2 * math.pi * i / steps
                x = int(cx + rr * 0.999 * math.cos(a) + 0.5)
                y = int(cy + rr * 0.999 * math.sin(a) + 0.5)
                if 0 <= x < self.w and 0 <= y < self.h:
                    base = (y * self.w + x) * 3
                    self.px[base:base + 3] = bytes(color)

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def draw_text(self, text, x, y, scale, color):
        """Draw text with its top-left corner at (x, y). Unknown chars
        are skipped (treated as spaces)."""
        cx = x
        for ch in text:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row, line in enumerate(glyph):
                for col, bit in enumerate(line):
                    if bit == '#':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, color)
            cx += 6 * scale

    def draw_text_centered(self, text, cx, y, scale, color):
        self.draw_text(text, cx - text_width(text, scale) // 2, y, scale, color)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns a list of lines fitting max_width."""
        words = text.split(' ')
        lines = []
        cur = ''
        for word in words:
            trial = word if not cur else cur + ' ' + word
            if text_width(trial, scale) <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def draw_wrapped(self, text, x, y, max_width, scale, color, leading=None):
        lines = self.wrap(text, max_width, scale)
        step = (leading if leading is not None else 10 * scale)
        for i, line in enumerate(lines):
            self.draw_text(line, x, y + i * step, scale, color)
        return y + len(lines) * step


def write_png(img, path):
    """Encode the RGB buffer as a PNG (filter 0 scanlines, zlib level 9).
    Fully deterministic: same pixels always give the same bytes."""
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        out += struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', img.w, img.h, 8, 2, 0, 0, 0)
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', ihdr)
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- map
# A coarse dotted world map: land is a list of (row, col_start, col_end)
# spans on a 60 x 24 equirectangular grid (lon -180..180, lat 75..-55).
# Stylised on purpose; the numbered discs mark the story places.

MAP_X, MAP_Y, MAP_W, MAP_H = 36, 402, 952, 170
LAND_SPANS = [
    (0, 20, 25), (0, 35, 59),
    (1, 3, 12), (1, 20, 25), (1, 35, 59),
    (2, 3, 14), (2, 20, 25), (2, 30, 34), (2, 35, 59),
    (3, 3, 15), (3, 30, 33), (3, 34, 59),
    (4, 4, 15), (4, 28, 35), (4, 36, 58),
    (5, 8, 18), (5, 28, 34), (5, 35, 37), (5, 40, 52), (5, 52, 53),
    (6, 8, 18), (6, 28, 34), (6, 35, 38), (6, 41, 44), (6, 44, 51),
    (6, 52, 53),
    (7, 8, 17), (7, 27, 35), (7, 36, 38), (7, 41, 44), (7, 45, 47),
    (7, 52, 53),
    (8, 8, 15), (8, 28, 35), (8, 36, 39), (8, 41, 43), (8, 45, 48),
    (9, 9, 14), (9, 28, 35), (9, 37, 38), (9, 42, 42), (9, 45, 48),
    (10, 10, 13), (10, 28, 35), (10, 46, 49),
    (11, 11, 13), (11, 16, 23), (11, 28, 34), (11, 46, 48),
    (12, 12, 13), (12, 16, 23), (12, 29, 34), (12, 45, 52),
    (13, 17, 22), (13, 29, 34), (13, 46, 51),
    (14, 17, 22), (14, 29, 34), (14, 47, 51),
    (15, 17, 21), (15, 30, 33), (15, 49, 54),
    (16, 18, 21), (16, 30, 33), (16, 49, 55),
    (17, 18, 20), (17, 30, 32), (17, 49, 55),
    (18, 18, 20), (18, 30, 32), (18, 50, 55),
    (19, 18, 19), (19, 30, 31), (19, 50, 54), (19, 57, 58),
    (20, 18, 19), (20, 30, 31), (20, 50, 53), (20, 57, 58),
    (21, 18, 19), (21, 57, 58),
    (22, 18, 18),
]

# Story number -> (longitude, latitude) of the place it happened.
MARKERS = {
    1: (33.5, 45.3),    # Crimea bridge
    2: (56.5, 26.5),    # Strait of Hormuz
    3: (114.0, 22.5),   # Shenzhen
    4: (-77.0, 38.9),   # Washington DC
    5: (139.7, 35.7),   # Tokyo
    6: (-0.1, 51.5),    # London
    7: (-84.4, 33.7),   # Atlanta (CDC)
    8: (-97.2, 25.9),   # Starbase, Texas
}


def lonlat_to_xy(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (75.0 - lat) / 130.0 * MAP_H
    return int(x + 0.5), int(y + 0.5)


def draw_map(img):
    img.fill_rect(MAP_X, MAP_Y, MAP_W, MAP_H, SEA)
    img.hline(MAP_X, MAP_Y, MAP_W, INK, 2)
    img.hline(MAP_X, MAP_Y + MAP_H - 2, MAP_W, INK, 2)
    img.vline(MAP_X, MAP_Y, MAP_H, INK, 2)
    img.vline(MAP_X + MAP_W - 2, MAP_Y, MAP_H, INK, 2)
    cell_w = MAP_W / 60.0
    cell_h = MAP_H / 24.0
    land = set()
    for r, c0, c1 in LAND_SPANS:
        for c in range(c0, c1 + 1):
            land.add((r, c))
    for (r, c) in sorted(land):
        cx = int(MAP_X + (c + 0.5) * cell_w + 0.5)
        cy = int(MAP_Y + (r + 0.5) * cell_h + 0.5)
        img.disc(cx, cy, 3, LAND)
    for num in sorted(MARKERS):
        cx, cy = lonlat_to_xy(*MARKERS[num])
        img.disc(cx, cy, 11, RED)
        img.ring(cx, cy, 11, 2, WHITE)
        digit = str(num)
        img.draw_text(digit, cx - text_width(digit, 2) // 2, cy - 7, 2, WHITE)


# ---------------------------------------------------------------- stories
# Every fact below is an event of Tuesday 17 November 2026, as reported
# that day. Allegations are worded as reported, never as proven fact.

LEAD_KICKER = "WAR IN EUROPE"
LEAD_HEADLINE = "BRIDGES UNDER FIRE"
LEAD_TEXT = (
    "UKRAINE STRIKES THE CRIMEA BRIDGE FOR A SECOND DAY, COLLAPSING PART "
    "OF THE ROAD SPAN. RUSSIAN MISSILES HIT KYIV'S NORTH AND SOUTH "
    "BRIDGES, CUTTING HEAT, WATER AND POWER."
)

TICKER = "MARKETS: S&P 500 -1.34% - STOXX 600 -1.75% - BRENT $91.67 - GOLD UP"

# (number, headline, summary) — four stories in a 2x2 grid.
GRID = [
    (2, "MINES IN THE GULF",
     "TANKERS HIT BY MINES NEAR HORMUZ. A THIRD U.S. CARRIER ARRIVES; "
     "IRANIAN DRONES AIMED AT A U.S. RADAR BASE IN BAHRAIN ARE SHOT DOWN."),
    (3, "SHENZHEN SUMMIT",
     "CHINA CONFIRMS THE FIRST THREE-WAY MEETING OF XI, TRUMP AND PUTIN, "
     "THURSDAY IN SHENZHEN ON THE APEC SIDELINES."),
    (4, "AUDIT FAILS AGAIN",
     "NINTH STRAIGHT YEAR WITHOUT A CLEAN AUDIT. AUDITORS COULD NOT "
     "VERIFY ACCOUNTS COVERING MORE THAN $4.8 TRILLION IN ASSETS."),
    (5, "JETS SCRAMBLED",
     "JAPAN LAUNCHES FIGHTER JETS AND PROTESTS AFTER TWO SUSPECTED "
     "RUSSIAN AIRCRAFT VIOLATE ITS AIRSPACE."),
]

BRIEF = [
    "6. UK SANCTIONS SETTLEMENT BUILDERS; ALLIES URGE GAZA AID IN.",
    "7. CDC: 13 BABIES BORN WITH MEASLES AS U.S. CASES HIT THE HIGHEST SINCE 1991.",
    "8. SPACEX CATCHES ITS STARSHIP UPPER STAGE AFTER ORBIT.",
]


def draw_grid_story(img, num, headline, summary, x, y, w):
    img.fill_rect(x, y, 26, 26, RED)
    digit = str(num)
    img.draw_text(digit, x + 13 - text_width(digit, 3) // 2, y + 3, 3, WHITE)
    img.draw_text(headline, x + 36, y + 2, 4, INK)
    img.draw_wrapped(summary, x, y + 38, w, 2, INK, leading=16)


def build():
    img = Image(W, H, PAPER)
    # Outer frame.
    img.hline(16, 16, W - 32, INK, 2)
    img.hline(16, H - 18, W - 32, INK, 2)
    img.vline(16, 16, H - 32, INK, 2)
    img.vline(W - 18, 16, H - 32, INK, 2)

    # Masthead.
    img.draw_text_centered("THE WORLD", W // 2, 24, 10, INK)
    img.draw_text_centered("TUESDAY, 17 NOVEMBER 2026", W // 2, 100, 4, INK)
    img.draw_text_centered(TICKER, W // 2, 134, 2, GRAY)
    img.hline(36, 154, 952, INK, 3)
    img.hline(36, 159, 952, INK, 1)

    # Lead story.
    img.draw_text(LEAD_KICKER, 36, 172, 3, RED)
    img.draw_text(LEAD_HEADLINE, 36, 198, 6, INK)
    img.draw_wrapped(LEAD_TEXT, 36, 246, 952, 3, INK, leading=30)

    # Map.
    img.draw_text("WHERE IT HAPPENED", 36, 378, 3, INK)
    note = "EACH NUMBER IS A STORY BELOW"
    img.draw_text(note, 988 - text_width(note, 2), 382, 2, GRAY)
    draw_map(img)

    # Four grid stories, 2 x 2.
    col_w = 466
    row_y = (588, 728)
    col_x = (36, 522)
    for i, (num, headline, summary) in enumerate(GRID):
        draw_grid_story(img, num, headline, summary,
                        col_x[i % 2], row_y[i // 2], col_w)
    img.vline(512, 588, 278, GRAY, 1)
    img.hline(36, 720, 952, GRAY, 1)

    # In brief.
    img.hline(36, 884, 952, INK, 2)
    img.draw_text("IN BRIEF", 36, 896, 3, RED)
    for i, line in enumerate(BRIEF):
        img.draw_text(line, 36, 924 + i * 16, 2, INK)

    # Footer.
    img.hline(36, 972, 952, INK, 1)
    img.draw_text_centered(
        "ALL EVENTS OF TUESDAY 17 NOVEMBER 2026, AS REPORTED THAT DAY.",
        W // 2, 980, 2, GRAY)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    img = build()
    size = write_png(img, os.path.join(out_dir, "entry.png"))
    print("wrote %s/entry.png (%d bytes, %dx%d)" % (out_dir, size, W, H))


if __name__ == "__main__":
    main()
