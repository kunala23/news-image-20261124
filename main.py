"""news-image-20261124: one-page newspaper front page for Tuesday 24 Nov 2026.

Pure Python 3 standard library only: a tiny raster canvas, a hand-made
5x7 bitmap font, and a minimal PNG encoder (zlib + struct). No network,
no files read, fully deterministic: the same bytes on every run.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font -----
# 5-wide, 7-tall glyphs. Each glyph is 7 strings of 5 characters, '#' = ink.
GLYPHS = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '<': ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    '>': ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
}

# ------------------------------------------------------------- canvas ------
INK = (26, 26, 26)
PAPER = (250, 246, 236)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
TEAL = (14, 110, 110)
GOLD = (176, 124, 18)
GREEN = (34, 110, 58)
GREY = (110, 108, 100)
LIGHT = (232, 226, 212)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= r * r:
                    self.set(xx, yy, c)

    def triangle(self, pts, c):
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


# -------------------------------------------------------------- text -------
def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(cv, x, y, s, scale, c):
    cx = x
    for ch in s.upper():
        g = GLYPHS.get(ch, GLYPHS[' '])
        for row in range(7):
            for col in range(5):
                if g[row][col] == '1':
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_centered(cv, cx, y, s, scale, c):
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, c)


def wrap(s, width, scale):
    words = s.upper().split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, width, scale, c, leading=None):
    lh = leading or (9 * scale)
    for line in wrap(s, width, scale):
        draw_text(cv, x, y, line, scale, c)
        y += lh
    return y


# --------------------------------------------------------------- png -------
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * stride:(yy + 1) * stride]
    data = zlib.compress(bytes(raw), 9)

    def chunk(tag, payload):
        out = struct.pack(">I", len(payload)) + tag + payload
        out += struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", data) + chunk(b"IEND", b""))

# -------------------------------------------------------------- icons ------
def icon_chip(cv, x, y, s, c):
    # computer chip: square body, inner square, pins on four sides
    cv.rect(x + 8, y + 8, s - 16, s - 16, c)
    cv.rect(x + 18, y + 18, s - 36, s - 36, PAPER)
    cv.rect(x + 26, y + 26, s - 52, s - 52, c)
    for i in range(3):
        px = x + 16 + i * 16
        cv.rect(px, y, 6, 8, c)
        cv.rect(px, y + s - 8, 6, 8, c)
        cv.rect(x, y + 16 + i * 16, 8, 6, c)
        cv.rect(x + s - 8, y + 16 + i * 16, 8, 6, c)


def icon_ship(cv, x, y, s, c):
    # warship: hull, bow, mast, funnel, waves
    cv.triangle([(x + 4, y + 34), (x + s - 4, y + 34), (x + s - 12, y + 52)], c)
    cv.rect(x + 8, y + 22, s - 30, 12, c)
    cv.rect(x + 20, y + 8, 5, 16, c)
    cv.rect(x + 34, y + 14, 5, 10, c)
    cv.line(x + 6, y + s - 6, x + s - 6, y + s - 6, c, 3)
    cv.line(x + 14, y + s - 12, x + s - 14, y + s - 12, c, 2)


def icon_sun(cv, x, y, s, c):
    # sun over cracked earth: disc, rays, ground line
    cx, cy, r = x + s // 2, y + s // 2 - 6, 16
    cv.circle(cx, cy, r, c)
    for ang in range(0, 360, 45):
        a = math.radians(ang)
        x0 = cx + int((r + 4) * math.cos(a))
        y0 = cy + int((r + 4) * math.sin(a))
        x1 = cx + int((r + 12) * math.cos(a))
        y1 = cy + int((r + 12) * math.sin(a))
        cv.line(x0, y0, x1, y1, c, 3)
    cv.line(x + 6, y + s - 10, x + s - 6, y + s - 10, c, 3)


def icon_tanker(cv, x, y, s, c):
    # oil tanker with a mine bobbing beside it
    cv.rect(x + 4, y + 30, s - 16, 16, c)
    cv.rect(x + 12, y + 18, 18, 12, c)
    cv.rect(x + s - 30, y + 20, 12, 10, c)
    cv.line(x + 6, y + s - 6, x + s - 6, y + s - 6, c, 3)
    mx, my = x + s - 14, y + 8
    cv.circle(mx, my, 5, RED)
    cv.line(mx - 8, my, mx + 8, my, RED, 2)
    cv.line(mx, my - 8, mx, my + 8, RED, 2)


def icon_rocket(cv, x, y, s, c):
    # rocket rising: body, window, fins, flame
    cv.triangle([(x + s // 2, y + 2), (x + s // 2 - 12, y + 26),
                 (x + s // 2 + 12, y + 26)], c)
    cv.rect(x + s // 2 - 12, y + 24, 24, 22, c)
    cv.circle(x + s // 2, y + 34, 5, PAPER)
    cv.triangle([(x + s // 2 - 12, y + 44), (x + s // 2 - 22, y + 54),
                 (x + s // 2 - 12, y + 54)], c)
    cv.triangle([(x + s // 2 + 12, y + 44), (x + s // 2 + 22, y + 54),
                 (x + s // 2 + 12, y + 54)], c)
    cv.triangle([(x + s // 2 - 6, y + 46), (x + s // 2 + 6, y + 46),
                 (x + s // 2, y + 60)], GOLD)


def icon_flame(cv, x, y, s, c):
    # flame: outer teardrop, inner tongue, ground
    cx = x + s // 2
    cv.triangle([(cx, y + 2), (cx - 20, y + 34), (cx + 20, y + 34)], c)
    cv.circle(cx, y + 34, 20, c)
    cv.circle(cx, y + 40, 10, GOLD)
    cv.line(x + 6, y + s - 6, x + s - 6, y + s - 6, c, 3)


# -------------------------------------------------------------- layout -----
def story_box(cv, x, y, w, h, tag, tag_c, headline, body, icon):
    cv.rect(x, y, w, h, (255, 253, 247))
    cv.frame(x, y, w, h, INK, 2)
    pad = 16
    # tag ribbon
    tw = text_w(tag, 2) + 16
    cv.rect(x + pad, y + pad, tw, 24, tag_c)
    draw_text(cv, x + pad + 8, y + pad + 5, tag, 2, (255, 255, 255))
    # icon top-right
    icon(cv, x + w - 76, y + pad, 60, tag_c)
    # headline (kept clear of the icon in the top-right corner)
    hw = w - 2 * pad - 84
    hy = y + pad + 36
    draw_para(cv, x + pad, hy, headline, hw, 3, INK, 30)
    nlines = len(wrap(headline, hw, 3))
    by = hy + nlines * 30 + 6
    draw_para(cv, x + pad, by, body, w - 2 * pad, 2, (60, 58, 52), 19)


def build():
    cv = Canvas(W, H, PAPER)
    M = 28  # margin

    # masthead
    cv.rect(M, M, W - 2 * M, 96, INK)
    draw_centered(cv, W // 2, M + 12, "THE WORLD IN ONE PAGE", 5, (250, 246, 236))
    draw_centered(cv, W // 2, M + 58, "TUESDAY 24 NOVEMBER 2026  -  THE DAY'S WORLD NEWS",
                  2, (232, 226, 212))
    cv.rect(M, M + 104, W - 2 * M, 4, RED)

    # lead story: Nvidia
    lx, ly, lw, lh = M, M + 118, W - 2 * M, 214
    cv.rect(lx, ly, lw, lh, (255, 253, 247))
    cv.frame(lx, ly, lw, lh, INK, 3)
    cv.rect(lx + 16, ly + 16, text_w("LEAD  -  BUSINESS", 2) + 16, 24, RED)
    draw_text(cv, lx + 24, ly + 21, "LEAD  -  BUSINESS", 2, (255, 255, 255))
    icon_chip(cv, lx + lw - 128, ly + 14, 104, GREEN)
    draw_para(cv, lx + 16, ly + 52, "HUANG IS BACK AT NVIDIA", lw - 180, 5, INK, 48)
    draw_para(cv, lx + 16, ly + 106,
              "Nvidia reinstates founder Jensen Huang as chief executive "
              "after pressure from President Trump. Shares jump 31% in a "
              "day and the S&P 500 climbs 4.7% in its best day in a year.",
              lw - 170, 2, (60, 58, 52), 19)
    draw_text(cv, lx + 16, ly + lh - 30, "NEW YORK  -  THE BOARD ACTED DAYS AFTER HUANG QUIT",
              2, GREY)

    # story grid: two columns, two rows, then one wide row
    gy = ly + lh + 16
    cw = (W - 2 * M - 16) // 2
    ch = 210
    story_box(cv, M, gy, cw, ch, "CONFLICT", BLUE,
              "UKRAINE SAYS IT SANK A RUSSIAN WARSHIP",
              "Kyiv says seven naval drones sank the Russian corvette "
              "Merkury at Benghazi, Libya. The UN calls for a probe.",
              icon_ship)
    story_box(cv, M + cw + 16, gy, cw, ch, "CLIMATE", TEAL,
              "COP31 ENDS WITH NO DEAL",
              "UN climate talks in Antalya collapse after 44 hours "
              "overtime, with no agreement on fossil fuels.",
              icon_sun)
    story_box(cv, M, gy + ch + 16, cw, ch, "ENERGY", GOLD,
              "TANKERS HIT BY MINES IN THE STRAIT OF HORMUZ",
              "Iran says three tankers struck mines in the strait as "
              "tensions rise; the UK logs record Iranian attacks.",
              icon_tanker)
    story_box(cv, M + cw + 16, gy + ch + 16, cw, ch, "SPACE", BLUE,
              "PAKISTAN ASTRONAUT TO FLY TO CHINA'S SPACE STATION",
              "Zeeshan Ali is set to be the first foreign astronaut "
              "aboard Tiangong, on the Shenzhou-24 mission.",
              icon_rocket)

    # wide bottom story: Indonesia factory fire
    by = gy + 2 * ch + 32
    bw, bh = W - 2 * M, 118
    cv.rect(M, by, bw, bh, (255, 253, 247))
    cv.frame(M, by, bw, bh, INK, 2)
    cv.rect(M + 16, by + 14, text_w("DISASTER  -  INDONESIA", 2) + 16, 24, RED)
    draw_text(cv, M + 24, by + 19, "DISASTER  -  INDONESIA", 2, (255, 255, 255))
    icon_flame(cv, M + bw - 92, by + 14, 88, RED)
    draw_para(cv, M + 16, by + 48, "FACTORY FIRE KILLS 26 IN BANTEN",
              bw - 130, 3, INK, 30)
    draw_para(cv, M + 16, by + 82,
              "A fire at a factory in Banten kills 26 people, with dozens "
              "still missing, in one of Indonesia's worst industrial fires.",
              bw - 130, 2, (60, 58, 52), 19)

    # footer
    fy = by + bh + 14
    cv.rect(M, fy, W - 2 * M, 3, INK)
    draw_centered(cv, W // 2, fy + 12,
                  "SOURCES: THE GUARDIAN, BBC, CBS, REUTERS  -  ALL EVENTS REPORTED 24 NOVEMBER 2026",
                  2, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
