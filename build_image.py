#!/usr/bin/env python3
"""Front page for the news-image-20261120 edition: one 1024x1024 sheet that
sums up Friday 20 November 2026 in pictures and short type.

Layout, top to bottom: an eyebrow line, a serif masthead with a
four-story deck, a six-number stat strip, a seven-segment region strip,
one dominant Kyiv lead (a night panorama of the Dnipro with the three
damaged bridges named on it), twelve illustrated feature tiles in three
rows of four, a light pin map next to twenty-four one-line briefs, a
DATE CHECK box that keeps Thursday stories off Friday's page, and a
footer line.

The picture is fully deterministic: a fixed seed drives every random
choice (paper grain, stars, skyline windows, rain, texture dots), no
clock and no network are consulted, and the same code writes the same
bytes on every run. Pillow is only needed by this renderer; the
entrypoint main.py stays stdlib-only so the grading image can run it.
"""
import os
import random
from math import cos, radians, sin

from PIL import Image, ImageDraw, ImageFont

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 16                        # side margin
CONTENT_W = PAGE_W - 2 * MARGIN    # 992 content width

PAGE_BG = (247, 242, 231)
TEXT_INK = (20, 20, 20)
ACCENT_RED = (178, 32, 44)
DEEP_NAVY = (18, 40, 74)
MUTED_GRAY = (90, 86, 78)

SEED = 20261120
dice = random.Random(SEED)

# ---------------------------------------------------------------- fonts
SERIF_BOLD_FILES = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"]
SERIF_ITALIC_FILES = ["/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
                      "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"]
SANS_BOLD_FILES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                   "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"]
SANS_FILES = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
_FONT_CACHE = {}


def _load_font(files, size):
    key = (tuple(files), size)
    if key not in _FONT_CACHE:
        for path in files:
            if os.path.exists(path):
                try:
                    _FONT_CACHE[key] = ImageFont.truetype(path, size)
                    break
                except OSError:
                    continue
        else:
            _FONT_CACHE[key] = ImageFont.load_default()
    return _FONT_CACHE[key]


def serif_bold(size):
    return _load_font(SERIF_BOLD_FILES, size)


def serif_italic(size):
    return _load_font(SERIF_ITALIC_FILES, size)


def sans_bold(size):
    return _load_font(SANS_BOLD_FILES, size)


def sans_plain(size):
    return _load_font(SANS_FILES, size)


# ---------------------------------------------------------------- helpers
def text_width(font, text):
    return font.getlength(text)


def wrap_text(font, text, max_w):
    words = text.split(" ")
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(font, trial) <= max_w or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(canvas, x, y, font, text, max_w, fill, leading=None):
    step = leading or int(font.size * 1.18)
    for line in wrap_text(font, text, max_w):
        canvas.text((x, y), line, font=font, fill=fill)
        y += step
    return y


def paint_gradient(canvas, box, top, bottom):
    x0, y0, x1, y1 = box
    height = max(1, y1 - y0)
    for i in range(height):
        t = i / height
        colour = tuple(int(top[k] + (bottom[k] - top[k]) * t) for k in range(3))
        canvas.line([(x0, y0 + i), (x1, y0 + i)], fill=colour)


def draw_outlined_text(canvas, xy, text, font, fill, outline, off=1):
    x, y = xy
    for dx, dy in ((-off, 0), (off, 0), (0, -off), (0, off),
                   (-off, -off), (off, -off), (-off, off), (off, off)):
        canvas.text((x + dx, y + dy), text, font=font, fill=outline)
    canvas.text((x, y), text, font=font, fill=fill)


def draw_dashed(canvas, points, fill, dash=7, gap=5, width=2):
    for i in range(len(points) - 1):
        x0, y0 = points[i]
        x1, y1 = points[i + 1]
        seg = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        if seg == 0:
            continue
        n = int(seg // (dash + gap))
        for k in range(n + 1):
            t0 = k * (dash + gap) / seg
            t1 = min(1.0, t0 + dash / seg)
            canvas.line([(x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0),
                         (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)],
                        fill=fill, width=width)


def bezier_points(p0, p1, p2, steps=24):
    out = []
    for i in range(steps + 1):
        t = i / steps
        out.append(((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
                    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]))
    return out


def add_grain(canvas, box, count):
    x0, y0, x1, y1 = box
    for _ in range(count):
        x = dice.randint(x0, x1)
        y = dice.randint(y0, y1)
        canvas.point((x, y), fill=(214, 205, 186) if dice.random() < 0.5
                     else (255, 250, 238))


def draw_chip(canvas, x, y, text, font, fg, bg):
    """Small filled label; returns width."""
    w = int(text_width(font, text)) + 12
    canvas.rectangle([x, y, x + w, y + font.size + 6], fill=bg)
    canvas.text((x + 6, y + 3), text, font=font, fill=fg)
    return w


# ---------------------------------------------------------------- data
# Each feature tile is one dict: num / place / field / title / body /
# hero (big fact on the dark strip) / hero_size / banner (art key) /
# chip (source label). Bodies are the v5 facts minus the parenthetical
# source, which the per-tile chip still carries; SOURCES.md keeps every
# attribution in full.
STORIES = [
    {"num": 1, "place": "ODISHA, INDIA", "field": "STORM",
     "title": "Cyclone Akvan makes landfall in eastern India",
     "body": "Gopalpur Friday morning; 370,000 evacuated, 423 rescue teams.",
     "hero": "370,000", "hero_size": 22, "banner": "cyclone", "chip": "IMD"},
    {"num": 3, "place": "ANTALYA, TÜRKIYE", "field": "CLIMATE",
     "title": "COP31 reaches final day deadlocked",
     "body": "Draft omits fossil-fuel phase-out and $120bn adaptation target.",
     "hero": "DEADLOCK", "hero_size": 20, "banner": "cop", "chip": "REUTERS"},
    {"num": 4, "place": "SEOUL · TOKYO", "field": "MARKETS",
     "title": "AI sell-off sinks Asia to worst week since 2020",
     "body": "Nikkei −4.5%, Kospi −4.7%, Taiex −6.4%; SoftBank −14.6%.",
     "hero": "−7%", "hero_size": 26, "banner": "market", "chip": "REUTERS"},
    {"num": 5, "place": "MERCURY", "field": "SPACE",
     "title": "BepiColombo reaches Mercury after 8 years",
     "body": "ESA/JAXA probe ends 6bn-mile trip; orbit insertion Saturday.",
     "hero": "6BN MILES", "hero_size": 20, "banner": "mercury", "chip": "ESA · BBC"},
    {"num": 6, "place": "BRUSSELS", "field": "EUROPE",
     "title": "Burnham holds second EU–UK reset summit",
     "body": "Deals on food, emissions trading, youth mobility for 100,000.",
     "hero": "RESET TALKS", "hero_size": 19, "banner": "flags", "chip": "AP"},
    {"num": 7, "place": "TOKYO", "field": "ECONOMY",
     "title": "Japan inflation hits 2.3%; BoJ hike eyed",
     "body": "Oct CPI 2.3%, up from 2.1%; core 2.2%.",
     "hero": "2.3%", "hero_size": 26, "banner": "bars", "chip": "STATISTICS BUREAU"},
    {"num": 8, "place": "BEIJING", "field": "RATES",
     "title": "China holds lending rates for 18th month",
     "body": "1-yr LPR 3.00%, 5-yr 3.50% as expected.",
     "hero": "3.00% · 3.50%", "hero_size": 17, "banner": "rates", "chip": "PBoC · REUTERS"},
    {"num": 9, "place": "WELLINGTON", "field": "CRICKET",
     "title": "Phillips makes history with 118 vs India",
     "body": "Centuries vs India in all 3 formats in one year; NZ 368.",
     "hero": "118", "hero_size": 28, "banner": "cricket", "chip": "ICC"},
    {"num": 10, "place": "ROME", "field": "LABOUR",
     "title": "Italy’s CGIL holds 24-hr general strike",
     "body": "Unions rally across ~100 squares against the 2027 budget.",
     "hero": "100 SQUARES", "hero_size": 18, "banner": "strike", "chip": "ANSA"},
    {"num": 11, "place": "MATO GROSSO, BRAZIL", "field": "LAND",
     "title": "Lula visits ailing Chief Raoni, 94",
     "body": "Kayapo and Yudja lands recognised (Kapot Nhinore).",
     "hero": "ANCESTRAL LANDS", "hero_size": 16, "banner": "forest", "chip": "ONE TURN"},
    {"num": 12, "place": "BARCELONA", "field": "HEALTH",
     "title": "Daraxonrasib + chemo shrinks tumours in 60.7%",
     "body": "Early trial, 61 patients, presented Friday at ENA.",
     "hero": "60.7%", "hero_size": 26, "banner": "pill", "chip": "EORTC"},
    {"num": 13, "place": "TURIN", "field": "TENNIS",
     "title": "Alcaraz–Cobolli & Medvedev–Tiafoe close ATP Finals groups",
     "body": "Group stage ends Friday; semi-finals Saturday.",
     "hero": "ATP FINALS", "hero_size": 18, "banner": "tennis", "chip": "ATP"},
]

# One line each — the same facts as v5 / SOURCES.md, stories 14-37.
BRIEF_ITEMS = [
    {"num": 14, "place": "SEOUL", "text": "Move to impeach Chief Justice Cho Hee-dae. (SBS)"},
    {"num": 15, "place": "BOUGAINVILLE", "text": "Rio Tinto pledges $370m Panguna repair. (ABC)"},
    {"num": 16, "place": "CANBERRA", "text": "CBO: AUKUS sales may shrink US fleet. (Reuters)"},
    {"num": 17, "place": "FLORIDA", "text": "St Johns River record 18.3 ft; schools shut. (AP)"},
    {"num": 18, "place": "IOWA", "text": "Army to detonate 68 unstable explosive barrels. (AP)"},
    {"num": 19, "place": "TONGA", "text": "El Niño drought bites. (RNZ)"},
    {"num": 20, "place": "COPENHAGEN", "text": "Greenland defence bill approved. (AFP)"},
    {"num": 21, "place": "GLOBAL", "text": "UN marks World Children’s Day. (UN News)"},
    {"num": 22, "place": "DAKAR", "text": "President Faye enacts budget by decree. (AFP)"},
    {"num": 23, "place": "HORMUZ", "text": "Attacks on vessels in 96 hours. (UKMTO)"},
    {"num": 24, "place": "NEW DELHI", "text": "Pakistan minister to lead SCO team. (The Hindu)"},
    {"num": 25, "place": "DOHA", "text": "U17 World Cup: Australia stuns Argentina 2–0. (FIFA)"},
    {"num": 26, "place": "HONG KONG", "text": "Badminton Open semifinals decided. (BWF)"},
    {"num": 27, "place": "TAIPEI", "text": "Short-sell curbs in; bombers tracked. (Reuters)"},
    {"num": 28, "place": "AL-DAHI, ISRAEL", "text": "Mosque torched; graffiti. (One Turn)"},
    {"num": 29, "place": "EUROPE", "text": "Youth strike in 25+ countries. (One Turn)"},
    {"num": 30, "place": "WASHINGTON", "text": "Trump: open to NATO-like Ukraine deal. (WTD)"},
    {"num": 31, "place": "BOGOTÁ", "text": "Protests over tax plans amid US row. (WTD)"},
    {"num": 32, "place": "LILONGWE", "text": "Malawi fuel crisis sparks chaos nationwide. (WTD)"},
    {"num": 33, "place": "GAZA", "text": "Civil Defence struggles as vehicles fail. (WTD)"},
    {"num": 34, "place": "BERLIN", "text": "Zelenskyy meets German, UK, French officials. (nhoq)"},
    {"num": 35, "place": "BRAZIL", "text": "Violent deaths at series low, −12.2%. (1stHeadlines)"},
    {"num": 36, "place": "ALGIERS", "text": "World Bank: Algeria growth at 3.7%. (1stHeadlines)"},
    {"num": 37, "place": "SANTIAGO", "text": "Fuel relief bill may cost $813m. (1stHeadlines)"},
]

STAT_CARDS = [
    {"value": "370,000+", "caption": "evacuated ahead of Akvan"},
    {"value": "3", "caption": "bridges hit in Kyiv barrage"},
    {"value": "−7%", "caption": "Asia’s worst week since 2020"},
    {"value": "2.3%", "caption": "Japan Oct CPI; BoJ hike eyed"},
    {"value": "118", "caption": "Phillips’ century vs India"},
    {"value": "60.7%", "caption": "shrunk by daraxonrasib+chemo"},
]

REGION_SEGMENTS = [
    {"label": "EUROPE 8", "colour": (31, 78, 121)},
    {"label": "AMERICAS 7", "colour": (122, 31, 31)},
    {"label": "ASIA-PACIFIC 8", "colour": (179, 84, 30)},
    {"label": "MIDEAST 5", "colour": (107, 79, 161)},
    {"label": "AFRICA 3", "colour": (46, 125, 50)},
    {"label": "OCEANIA 4", "colour": (0, 131, 143)},
    {"label": "WORLD / SPACE 2", "colour": (84, 110, 122)},
]


# ---------------------------------------------------------------- banners
# One painter per feature tile, alphabetical by art key. Each takes the
# tile box (x, y, w, h) and draws only inside it; the hero strip, the
# source chip and the tile outline are painted by the composer, not here.
def paint_bars(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(238, 240, 235))
    for gy in range(y + 8, y + h - 6, 9):
        canvas.line([(x + 6, gy), (x + w - 6, gy)], fill=(215, 218, 210))
    vals = [14, 20, 17, 26, 22, 32, 28]
    for i, v in enumerate(vals):
        bx = x + 12 + i * 30
        canvas.rectangle([bx, y + h - 6 - v, bx + 18, y + h - 6],
                         fill=(40, 90, 170))
    canvas.line([(x + 6, y + h - 6), (x + w - 6, y + h - 6)], fill=(60, 60, 60),
                width=2)
    canvas.line([(x + 6, y + 12), (x + w - 6, y + 12)], fill=(180, 40, 40), width=2)
    canvas.text((x + w - 56, y + 2), "2% TARGET", font=sans_bold(8),
                fill=(180, 40, 40))


def paint_cop(canvas, x, y, w, h):
    paint_gradient(canvas, (x, y, x + w, y + h), (120, 190, 170), (40, 110, 110))
    # globe with latitude lines
    canvas.ellipse([x + 8, y + 2, x + 50, y + 44], fill=(70, 140, 180))
    canvas.ellipse([x + 14, y + 8, x + 30, y + 24], fill=(120, 200, 120))
    canvas.ellipse([x + 30, y + 22, x + 44, y + 36], fill=(120, 200, 120))
    canvas.arc([x + 8, y + 2, x + 50, y + 44], 0, 360, fill=(200, 230, 240))
    canvas.line([(x + 8, y + 23), (x + 50, y + 23)], fill=(200, 230, 240))
    # thermometer
    canvas.rectangle([x + w - 24, y + 4, x + w - 16, y + 32],
                     outline=(255, 255, 255), width=2)
    canvas.rectangle([x + w - 23, y + 18, x + w - 17, y + 31], fill=(220, 60, 50))
    canvas.ellipse([x + w - 28, y + 30, x + w - 12, y + 46], fill=(220, 60, 50),
                   outline=(255, 255, 255))
    for k in range(3):
        canvas.line([(x + w - 30, y + 10 + k * 7), (x + w - 24, y + 10 + k * 7)],
                    fill=(255, 255, 255), width=2)


def paint_cricket(canvas, x, y, w, h):
    paint_gradient(canvas, (x, y, x + w, y + h), (60, 140, 70), (30, 100, 40))
    # outfield texture
    for _ in range(40):
        canvas.point((dice.randint(x + 2, x + w - 2),
                      dice.randint(y + 2, y + h - 2)), fill=(90, 170, 95))
    canvas.rectangle([x + w // 2 - 14, y + 4, x + w // 2 + 14, y + h - 4],
                     fill=(210, 190, 150))
    for k in range(3):
        canvas.line([(x + w // 2 - 14, y + 10 + k * 12),
                     (x + w // 2 + 14, y + 10 + k * 12)], fill=(255, 255, 255),
                    width=1)
    # stumps + bails
    for sx in (x + 14, x + 19, x + 24):
        canvas.rectangle([sx, y + 8, sx + 3, y + 26], fill=(240, 220, 120))
    canvas.rectangle([x + 14, y + 6, x + 27, y + 8], fill=(240, 220, 120))
    # bat + ball trail
    canvas.rectangle([x + w - 34, y + 12, x + w - 26, y + 36], fill=(190, 160, 110),
                     outline=(120, 90, 50))
    canvas.ellipse([x + w - 22, y + 30, x + w - 14, y + 38], fill=(200, 40, 40))
    canvas.arc([x + w - 60, y + 4, x + w - 10, y + 40], 300, 60,
               fill=(255, 255, 255), width=2)


def paint_cyclone(canvas, x, y, w, h):
    paint_gradient(canvas, (x, y, x + w, y + h), (38, 110, 160), (16, 60, 110))
    # coastline + Bay of Bengal
    canvas.polygon([(x, y + h), (x, y + 18), (x + 62, y + 8), (x + 74, y + h)],
                   fill=(214, 196, 150))
    canvas.polygon([(x, y + h), (x + 74, y + h), (x + 62, y + 8)],
                   fill=(190, 170, 120))
    # spiral bands
    for band in range(9):
        canvas.arc([x + 58, y - 6 + band * 3, x + 132, y + 44 + band * 3], 190, 350,
                   fill=(200, 225, 245))
    canvas.ellipse([x + 92, y + 10, x + 112, y + 30], outline=(255, 255, 255),
                   width=2)
    canvas.ellipse([x + 98, y + 16, x + 106, y + 24], fill=(255, 255, 255))
    # rain streaks
    for _ in range(26):
        rx = dice.randint(x + 70, x + w - 4)
        ry = dice.randint(y + 2, y + h - 10)
        canvas.line([(rx, ry), (rx - 3, ry + 7)], fill=(170, 205, 235))
    # landfall dot (label lives in the tile body text)
    canvas.ellipse([x + 56, y + 24, x + 64, y + 32], fill=(255, 70, 60),
                   outline=(255, 255, 255))


def paint_flags(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w // 2, y + h], fill=(20, 60, 160))
    cx, cy = x + w // 4, y + h // 2
    for k in range(12):
        ang = radians(k * 30)
        sx = cx + int(17 * cos(ang))
        sy = cy + int(14 * sin(ang))
        canvas.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 220, 60))
    canvas.rectangle([x + w // 2, y, x + w, y + h], fill=(200, 30, 45))
    canvas.rectangle([x + w // 2, y + h // 2 - 4, x + w, y + h // 2 + 4],
                     fill=(255, 255, 255))
    canvas.rectangle([x + w * 3 // 4 - 4, y, x + w * 3 // 4 + 4, y + h],
                     fill=(255, 255, 255))


def paint_forest(canvas, x, y, w, h):
    # v7 redraw: layered rainforest canopy, sun, river, birds
    paint_gradient(canvas, (x, y, x + w, y + h), (140, 200, 150), (40, 120, 60))
    canvas.ellipse([x + w - 36, y + 2, x + w - 10, y + 28], fill=(255, 220, 120))
    # back canopy
    for cx, cy, r in [(x + 30, y + 22, 20), (x + 80, y + 14, 24),
                      (x + 130, y + 24, 20), (x + 180, y + 16, 22),
                      (x + 220, y + 26, 18)]:
        canvas.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 70))
    # front canopy + trunks
    for cx, cy, r in [(x + 16, y + 34, 16), (x + 66, y + 30, 18),
                      (x + 118, y + 36, 16), (x + 168, y + 30, 18),
                      (x + 214, y + 36, 15)]:
        canvas.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(24, 100, 40))
        canvas.rectangle([cx - 3, cy + 4, cx + 3, y + h - 2], fill=(90, 60, 30))
    # river
    canvas.polygon([(x, y + h), (x + 60, y + h - 12), (x + 120, y + h),
                    (x + 200, y + h - 10), (x + w, y + h), (x + w, y + h),
                    (x, y + h)], fill=(90, 160, 200))
    # birds
    for bx, by in [(x + 90, y + 6), (x + 120, y + 10), (x + 150, y + 5)]:
        canvas.arc([bx - 5, by - 3, bx + 5, by + 3], 200, 340,
                   fill=(40, 40, 40), width=2)


def paint_market(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(24, 24, 28))
    # grid
    for gy in range(y + 8, y + h - 4, 10):
        canvas.line([(x + 4, gy), (x + w - 4, gy)], fill=(48, 48, 56))
    for i in range(9):
        bx = x + 10 + i * 24
        top = y + 6 + i * 3
        bot = top + 18 - i
        col = (215, 60, 55) if i % 2 == 0 else (235, 90, 70)
        canvas.rectangle([bx, top, bx + 14, bot], fill=col)
        canvas.line([(bx + 7, top - 5), (bx + 7, bot + 5)], fill=col, width=2)
    canvas.line([(x + 6, y + 8), (x + w - 6, y + h - 6)], fill=(255, 120, 110),
                width=3)


def paint_mercury(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(8, 8, 14))
    for _ in range(34):
        canvas.point((dice.randint(x + 2, x + w - 2),
                      dice.randint(y + 2, y + h - 2)), fill=(220, 220, 220))
    # orbit ring + probe
    canvas.ellipse([x - 6, y - 14, x + w + 6, y + h + 14], outline=(240, 200, 90))
    canvas.ellipse([x + 8, y + 6, x + 42, y + 40], fill=(150, 145, 135))
    canvas.ellipse([x + 14, y + 12, x + 22, y + 20], fill=(120, 115, 105))
    canvas.ellipse([x + 26, y + 26, x + 34, y + 34], fill=(120, 115, 105))
    canvas.ellipse([x + 18, y + 8, x + 26, y + 14], fill=(110, 105, 95))
    canvas.rectangle([x + w - 30, y + 6, x + w - 16, y + 14], fill=(220, 220, 220))
    canvas.rectangle([x + w - 34, y + 8, x + w - 30, y + 12], fill=(240, 200, 90))
    canvas.line([(x + w - 16, y + 10), (x + w - 6, y + 10)], fill=(240, 200, 90),
                width=2)


def paint_pill(canvas, x, y, w, h):
    # v7 redraw: dark lab bench, big capsule, molecule dots, high contrast
    canvas.rectangle([x, y, x + w, y + h], fill=(28, 32, 58))
    for _ in range(22):
        cx = dice.randint(x + 6, x + w - 6)
        cy = dice.randint(y + 4, y + h - 4)
        canvas.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], outline=(150, 120, 200))
        canvas.point((cx, cy), fill=(200, 160, 230))
    canvas.rounded_rectangle([x + 16, y + 12, x + 84, y + 32], radius=10,
                             fill=(220, 50, 70))
    canvas.rounded_rectangle([x + 50, y + 12, x + 84, y + 32], radius=10,
                             fill=(255, 255, 255))
    canvas.rounded_rectangle([x + 16, y + 12, x + 84, y + 32], radius=10,
                             outline=(255, 255, 255), width=2)
    canvas.ellipse([x + w - 34, y + 6, x + w - 18, y + 22], fill=(255, 220, 120))
    canvas.line([(x + w - 26, y + 22), (x + w - 26, y + 34)], fill=(255, 220, 120),
                width=2)
    canvas.rectangle([x, y + h - 4, x + w, y + h], fill=(200, 200, 210))


def paint_rates(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(240, 238, 230))
    for gy in range(y + 8, y + h - 4, 9):
        canvas.line([(x + 6, gy), (x + w - 6, gy)], fill=(218, 214, 204))
    pts1 = [(x + 10 + i * 32, y + 12 + (i % 3) * 4) for i in range(7)]
    pts2 = [(x + 10 + i * 32, y + 26 + (i % 2) * 3) for i in range(7)]
    canvas.line(pts1, fill=(40, 90, 170), width=4)
    canvas.line(pts2, fill=(200, 60, 50), width=4)
    for px, py in pts1:
        canvas.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255),
                       outline=(40, 90, 170))
    for px, py in pts2:
        canvas.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255),
                       outline=(200, 60, 50))


def paint_strike(canvas, x, y, w, h):
    # v7 redraw: high-contrast march - big figures, placards, red band
    canvas.rectangle([x, y, x + w, y + h], fill=(250, 244, 228))
    canvas.rectangle([x, y, x + w, y + 10], fill=(178, 32, 44))
    # back row of marchers (small, dark)
    for i in range(10):
        cx = x + 12 + i * 22
        cy = y + 18
        canvas.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(70, 70, 80))
        canvas.rectangle([cx - 5, cy + 4, cx + 5, cy + 14], fill=(90, 90, 100))
    # front row: three big figures with placards
    for i, px in enumerate((x + 34, x + 108, x + 182)):
        canvas.ellipse([px - 8, y + 18, px + 8, y + 34], fill=(40, 40, 50))
        canvas.rectangle([px - 9, y + 34, px + 9, y + h - 2],
                         fill=(150, 40, 40) if i == 1 else (50, 90, 150))
        canvas.rectangle([px - 14, y + 12, px + 14, y + 24],
                         fill=(255, 255, 255), outline=(40, 40, 50))
        canvas.line([(px, y + 24), (px, y + 32)], fill=(40, 40, 50), width=2)
    canvas.rectangle([x + w - 70, y + h - 16, x + w - 4, y + h - 4],
                     fill=(20, 20, 24))
    canvas.text((x + w - 66, y + h - 14), "24-HOUR", font=sans_bold(9),
                fill=(255, 255, 255))


def paint_tennis(canvas, x, y, w, h):
    paint_gradient(canvas, (x, y, x + w, y + h), (40, 110, 70), (20, 80, 50))
    canvas.rectangle([x + 16, y + 6, x + w - 16, y + h - 6],
                     outline=(255, 255, 255), width=2)
    canvas.line([(x + w // 2, y + 6), (x + w // 2, y + h - 6)],
                fill=(255, 255, 255), width=2)
    canvas.line([(x + 16, y + h // 2), (x + w - 16, y + h // 2)],
                fill=(255, 255, 255), width=1)
    # net
    canvas.rectangle([x + 30, y + h - 16, x + w - 30, y + h - 10],
                     outline=(255, 255, 255))
    for nx in range(x + 34, x + w - 30, 10):
        canvas.line([(nx, y + h - 16), (nx, y + h - 10)], fill=(255, 255, 255))
    # ball + motion arc
    canvas.ellipse([x + w - 36, y + 6, x + w - 20, y + 22], fill=(200, 230, 60))
    canvas.arc([x + w - 36, y + 6, x + w - 20, y + 22], 20, 200,
               fill=(40, 60, 30), width=2)
    canvas.arc([x + w - 70, y + 2, x + w - 20, y + 34], 300, 60,
               fill=(255, 255, 255), width=2)


BANNER_PAINTS = {"cyclone": paint_cyclone, "cop": paint_cop, "market": paint_market,
                 "mercury": paint_mercury, "flags": paint_flags, "bars": paint_bars,
                 "rates": paint_rates, "cricket": paint_cricket, "strike": paint_strike,
                 "forest": paint_forest, "pill": paint_pill, "tennis": paint_tennis}


# ---------------------------------------------------------------- lead: Kyiv panorama
# The three bridges are named on the panorama (v7, from recon): Reuters,
# 20 Nov 2026 - Podilsko-Voskresenskyi, Darnytskyi and Pivdennyi (Southern).
# x0/x1 are offsets from the panorama's left edge.
BRIDGE_SPANS = [
    {"name": "PODILSKO-VOSKRESENSKYI", "x0": 90, "x1": 300},
    {"name": "DARNYTSKYI", "x0": 430, "x1": 640},
    {"name": "PIVDENNYI · SOUTHERN", "x0": 760, "x1": 960},
]


def _lead_sky(canvas, x, y, w, sky_h):
    paint_gradient(canvas, (x, y, x + w, y + sky_h), (8, 22, 48), (38, 74, 128))
    for _ in range(320):
        sx = dice.randint(x + 2, x + w - 2)
        sy = dice.randint(y + 2, y + sky_h - 40)
        r = dice.random()
        c = (255, 255, 255) if r > 0.7 else (200, 210, 235)
        canvas.point((sx, sy), fill=c)
        if r > 0.93:
            canvas.point((sx + 1, sy), fill=c)
    mx, my = x + 300, y + 20
    canvas.ellipse([mx - 16, my - 16, mx + 16, my + 16], outline=(220, 220, 200),
                   width=2)
    canvas.ellipse([mx - 11, my - 11, mx + 11, my + 11], fill=(235, 232, 210))
    canvas.ellipse([mx - 4, my - 6, mx + 3, my + 1], fill=(210, 206, 185))


def _lead_skyline(canvas, x, w, river_y):
    bx = x
    while bx < x + w - 30:
        bw = dice.randint(26, 58)
        bh = dice.randint(22, 62)
        canvas.rectangle([bx, river_y - bh, bx + bw, river_y], fill=(10, 18, 36))
        for _ in range(bw * bh // 70):
            wx = dice.randint(bx + 3, bx + bw - 4)
            wy = dice.randint(river_y - bh + 4, river_y - 4)
            canvas.rectangle([wx, wy, wx + 2, wy + 3], fill=(255, 200, 90))
        if dice.random() < 0.3:
            canvas.rectangle([bx + bw // 2 - 1, river_y - bh - 8, bx + bw // 2 + 1,
                              river_y - bh], fill=(10, 18, 36))
            canvas.point((bx + bw // 2, river_y - bh - 9), fill=(255, 60, 50))
        bx += bw + dice.randint(2, 10)


def _lead_river(canvas, x, y, w, h, river_y):
    paint_gradient(canvas, (x, river_y, x + w, y + h), (52, 110, 165),
                   (18, 58, 105))
    for _ in range(34):
        rx = dice.randint(x + 4, x + w - 40)
        ry = dice.randint(river_y + 4, y + h - 4)
        canvas.line([(rx, ry), (rx + dice.randint(12, 34), ry)],
                    fill=(140, 190, 235))


def _lead_bridges(canvas, x, y, w, h, river_y):
    for pos, bridge in enumerate(BRIDGE_SPANS):
        name = bridge["name"]
        bx0 = x + bridge["x0"]
        bx1 = x + bridge["x1"]
        mid = (bx0 + bx1) // 2
        canvas.rectangle([bx0, river_y + 2, bx1, river_y + 8], fill=(8, 16, 34))
        for px in range(bx0 + 12, bx1 - 8, 26):
            canvas.rectangle([px, river_y + 8, px + 5, y + h - 2],
                             fill=(8, 16, 34))
        canvas.arc([bx0, river_y - 14, bx1, river_y + 26], 180, 360,
                   fill=(8, 16, 34), width=3)
        if pos == 1:
            canvas.rectangle([mid - 14, river_y - 16, mid + 26, river_y + 2],
                             fill=(8, 16, 34))
            canvas.polygon([(mid + 26, river_y + 2), (mid + 44, river_y + 18),
                            (mid + 18, river_y + 18)], fill=(8, 16, 34))
            for sx, sy, sr in [(mid + 6, river_y - 22, 7),
                               (mid + 16, river_y - 32, 9),
                               (mid + 28, river_y - 42, 11)]:
                canvas.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                               fill=(150, 150, 155))
        # bridge-name label: dark pill at the foot of the panorama
        label_font = sans_bold(8)
        lw = int(text_width(label_font, name)) + 12
        lx = mid - lw // 2
        canvas.rectangle([lx, y + h - 16, lx + lw, y + h - 3], fill=(8, 16, 34))
        canvas.text((lx + 6, y + h - 13), name, font=label_font,
                    fill=(255, 255, 255))


def _lead_missiles(canvas, x, y, w, river_y):
    for tx, ty in [(x + 195, river_y - 6), (x + 535, river_y - 10),
                   (x + 860, river_y - 6)]:
        pts = bezier_points((tx + dice.randint(120, 260), y + dice.randint(2, 26)),
                            ((tx + x + w) // 2, y + 4), (tx, ty))
        draw_dashed(canvas, pts, (255, 200, 120))
        for r, c in [(16, (255, 120, 30)), (10, (255, 170, 60)),
                     (5, (255, 230, 150))]:
            canvas.ellipse([tx - r, ty - r, tx + r, ty + r], fill=c)


def _lead_labels(canvas, x, y, w, h, river_y):
    canvas.rectangle([x, y, x + 252, y + 20], fill=ACCENT_RED)
    canvas.text((x + 8, y + 4), "OVERNIGHT · BALLISTIC MISSILES",
                font=sans_bold(12), fill=(255, 255, 255))
    draw_outlined_text(canvas, (x + 12, river_y - 52), "KYIV", serif_bold(42),
                       (255, 255, 255), (8, 16, 34), off=2)
    canvas.text((x + 14, y + h - 18), "DNIPRO RIVER", font=serif_italic(11),
                fill=(220, 235, 250))
    canvas.rectangle([x + w - 168, y + 6, x + w - 8, y + 26], fill=(20, 20, 24))
    canvas.text((x + w - 160, y + 9), "3 BRIDGES HIT", font=sans_bold(13),
                fill=(255, 255, 255))
    canvas.rectangle([x + w - 168, y + 30, x + w - 8, y + 50], fill=(20, 20, 24))
    canvas.text((x + w - 160, y + 33), "110+ MISSILES", font=sans_bold(13),
                fill=(255, 200, 90))


def paint_lead(canvas, x, y, w, h):
    sky_h = int(h * 0.62)
    river_y = y + sky_h
    _lead_sky(canvas, x, y, w, sky_h)
    _lead_skyline(canvas, x, w, river_y)
    _lead_river(canvas, x, y, w, h, river_y)
    _lead_bridges(canvas, x, y, w, h, river_y)
    _lead_missiles(canvas, x, y, w, river_y)
    _lead_labels(canvas, x, y, w, h, river_y)


# ---------------------------------------------------------------- map (v7: light, big pins)
# Dot map drawn from text art: "#" marks land, everything else is sea.
# Rows are 52 columns wide; trailing space is irrelevant (rows are padded
# to 52 before drawing), only leading space and "#" positions matter.
MAP_ART = """
  ####    ######   ##    ###############
   ####  ########  #    ##################
    ###  #########       ##################
     ##############     #################
      #############     ################
      #############    ##############  ##
      ##############  #############  ###
      ##############  ##########   ###
       ############   ########    ###
        ##########   ########    ##
         ########    ########   ##
          ######     ########  ##
          ######     #######   ####
          ######     ######    #####
          ######     #####     ####
          #####      ####      #####
          #####      ####      ######
          ####       ####      ######
          ###        ###       #####
          ###        ###       ####       ##
          ##                               ##
          ##
          #
                                                    
""".strip("\n").split("\n")

MAP_PINS = [
    {"num": 1, "lon": 85, "lat": 20, "dx": 0, "dy": 0},
    {"num": 2, "lon": 30, "lat": 50, "dx": 8, "dy": -6},
    {"num": 3, "lon": 30, "lat": 36, "dx": 8, "dy": 6},
    {"num": 4, "lon": 133, "lat": 36, "dx": 0, "dy": 0},
    {"num": 6, "lon": 4, "lat": 50, "dx": -10, "dy": -8},
    {"num": 7, "lon": 139, "lat": 35, "dx": 2, "dy": 1},
    {"num": 8, "lon": 116, "lat": 39, "dx": 0, "dy": 0},
    {"num": 9, "lon": 174, "lat": -41, "dx": 0, "dy": 0},
    {"num": 10, "lon": 12, "lat": 41, "dx": 10, "dy": 4},
    {"num": 11, "lon": -55, "lat": -12, "dx": 0, "dy": 0},
    {"num": 12, "lon": 2, "lat": 41, "dx": -12, "dy": 2},
    {"num": 13, "lon": 7, "lat": 45, "dx": 6, "dy": -10},
]


def paint_map(canvas, x, y, w, h):
    canvas.rectangle([x, y, x + w, y + h], fill=(238, 234, 222))
    canvas.rectangle([x, y, x + w, y + h], outline=TEXT_INK, width=1)
    canvas.text((x + 8, y + 6), "WHERE IT HAPPENED", font=sans_bold(12),
                fill=TEXT_INK)
    mx, my = x + 6, y + 26
    mw, mh = w - 12, h - 62
    cols, rows = 52, 24
    cell_w, cell_h = mw / cols, mh / rows
    for r, row in enumerate(MAP_ART):
        for c, mark in enumerate(row.ljust(cols)):
            if mark == "#":
                cx = mx + c * cell_w + cell_w / 2
                cy = my + r * cell_h + cell_h / 2
                canvas.ellipse([cx - 1.8, cy - 1.8, cx + 1.8, cy + 1.8],
                               fill=(150, 138, 105))
    for pin in MAP_PINS:
        px = mx + (pin["lon"] + 180) / 360 * mw + pin["dx"]
        py = my + (72 - pin["lat"]) / 132 * mh + pin["dy"]
        canvas.ellipse([px - 9, py - 9, px + 9, py + 9], fill=ACCENT_RED,
                       outline=(255, 255, 255), width=2)
        f = sans_bold(9)
        s = str(pin["num"])
        canvas.text((px - text_width(f, s) / 2, py - 6), s, font=f,
                    fill=(255, 255, 255))
    canvas.text((x + 8, y + h - 30), "1–3 Lead · 4–13 Features.",
                font=sans_plain(9), fill=(70, 66, 58))
    canvas.text((x + 8, y + h - 18), "5 Mercury is in space — no pin.",
                font=sans_plain(9), fill=(70, 66, 58))


# ---------------------------------------------------------------- compose
def build_page(out_path):
    img = Image.new("RGB", (PAGE_W, PAGE_H), PAGE_BG)
    canvas = ImageDraw.Draw(img)
    add_grain(canvas, (0, 0, PAGE_W, PAGE_H), 150000)

    # ---- eyebrow
    canvas.text((MARGIN, 4), "THE WORLD IN ONE DAY", font=sans_bold(12),
                fill=ACCENT_RED)
    right = "FRIDAY’S NEWS • ONE PAGE • 37 STORIES • 7 REGIONS"
    canvas.text((PAGE_W - MARGIN - text_width(sans_bold(11), right), 5), right,
                font=sans_bold(11), fill=TEXT_INK)
    canvas.line([(MARGIN, 22), (PAGE_W - MARGIN, 22)], fill=TEXT_INK, width=2)

    # ---- masthead
    title = "Friday 20 November 2026"
    title_font = serif_bold(58)
    canvas.text(((PAGE_W - text_width(title_font, title)) / 2, 24), title,
                font=title_font, fill=TEXT_INK)
    deck = ("Cyclone Akvan strikes India • Ballistic missiles hit Kyiv • COP31 "
            "deadlocked on final day • Asian AI sell-off")
    deck_font = serif_italic(15)
    canvas.text(((PAGE_W - text_width(deck_font, deck)) / 2, 88), deck,
                font=deck_font, fill=TEXT_INK)
    canvas.line([(MARGIN, 106), (PAGE_W - MARGIN, 106)], fill=TEXT_INK, width=1)

    # ---- stat strip (6 numbers, bigger type than v5; captions one line)
    y0, y1 = 110, 152
    cell_w = CONTENT_W / 6
    for i, stat in enumerate(STAT_CARDS):
        cx = MARGIN + i * cell_w
        if i:
            canvas.line([(cx, y0 + 4), (cx, y1 - 4)], fill=(200, 192, 175),
                        width=1)
        canvas.text((cx + 8, y0 + 1), stat["value"], font=sans_bold(27),
                    fill=ACCENT_RED if i in (0, 1, 2) else TEXT_INK)
        canvas.text((cx + 8, y0 + 31), stat["caption"], font=sans_plain(9),
                    fill=MUTED_GRAY)
    canvas.line([(MARGIN, y1 + 2), (PAGE_W - MARGIN, y1 + 2)], fill=TEXT_INK,
                width=2)

    # ---- region strip (7 segments)
    ry0, ry1 = 156, 172
    seg_w = CONTENT_W / len(REGION_SEGMENTS)
    for i, region in enumerate(REGION_SEGMENTS):
        sx = MARGIN + i * seg_w
        canvas.rectangle([sx, ry0, sx + seg_w - 1, ry1], fill=region["colour"])
        reg_font = sans_bold(10)
        canvas.text((sx + (seg_w - text_width(reg_font, region["label"])) / 2,
                     ry0 + 3), region["label"], font=reg_font,
                    fill=(255, 255, 255))

    # ---- DOMINANT LEAD: Kyiv bridges
    lx, ly, lw, lh = MARGIN, 176, CONTENT_W, 140
    paint_lead(canvas, lx, ly, lw, lh)
    canvas.rectangle([lx, ly, lx + lw, ly + lh], outline=TEXT_INK, width=1)
    hy = ly + lh + 6
    canvas.text((lx, hy), "02 · KYIV, UKRAINE — WAR", font=sans_bold(12),
                fill=ACCENT_RED)
    canvas.text((lx, hy + 15), "Russian barrage hits three Kyiv bridges",
                font=serif_bold(36), fill=TEXT_INK)
    lead_body = ("Overnight ballistic-missile barrage kills 3, damages three "
                 "bridges across the Dnipro and sets fires in three districts; "
                 "110+ missiles fired. (Reuters, livefromeurope)")
    draw_wrapped(canvas, lx, hy + 58, sans_plain(14), lead_body, lw, TEXT_INK,
                 leading=17)

    # ---- features: 12 stories, 3 rows x 4 (titles 14px, bodies 11px)
    rows_y = [416, 534, 652]
    gap = 8
    cell_w = (CONTENT_W - 3 * gap) // 4
    for slot, story in enumerate(STORIES):
        r, c = divmod(slot, 4)
        fx = int(MARGIN + c * (cell_w + gap))
        fy = rows_y[r]
        BANNER_PAINTS[story["banner"]](canvas, fx, fy, cell_w, 44)
        # hero fact on a dark strip: guarantees contrast on any banner art
        hero_font = sans_bold(story["hero_size"])
        hw = int(text_width(hero_font, story["hero"])) + 12
        hy0 = fy + 44 - story["hero_size"] - 8
        canvas.rectangle([fx, hy0, fx + hw, fy + 44], fill=(10, 10, 14))
        canvas.text((fx + 6, hy0 + 3), story["hero"], font=hero_font,
                    fill=(255, 255, 255))
        chip_font = sans_bold(8)
        chw = text_width(chip_font, story["chip"])
        canvas.rectangle([fx + cell_w - chw - 10, fy + 3, fx + cell_w - 4, fy + 15],
                         fill=(15, 15, 18))
        canvas.text((fx + cell_w - chw - 7, fy + 5), story["chip"], font=chip_font,
                    fill=(255, 255, 255))
        canvas.rectangle([fx, fy, fx + cell_w, fy + 44], outline=TEXT_INK, width=1)
        ty = fy + 48
        kicker = "%02d · %s — %s" % (story["num"], story["place"], story["field"])
        canvas.text((fx, ty), kicker, font=sans_bold(10), fill=ACCENT_RED)
        title_lines = len(wrap_text(sans_bold(14), story["title"], cell_w))
        draw_wrapped(canvas, fx, ty + 13, sans_bold(14), story["title"], cell_w,
                     TEXT_INK, leading=16)
        draw_wrapped(canvas, fx, ty + 13 + 16 * title_lines,
                     sans_plain(11), story["body"], cell_w, (40, 40, 40),
                     leading=13)

    # ---- bottom: map + ALSO 24 briefs
    by0 = 774
    map_w = 220
    paint_map(canvas, MARGIN, by0, map_w, 184)
    ax = MARGIN + map_w + 8
    aw = PAGE_W - MARGIN - ax
    canvas.text((ax, by0), "ALSO ON FRIDAY 20 NOVEMBER — 24 MORE STORIES",
                font=sans_bold(13), fill=ACCENT_RED)
    legend = "■ Europe  ■ Asia-Pacific  ■ Americas  ■ Africa  ■ Middle East  ■ Sport & science"
    canvas.text((ax, by0 + 15), legend, font=sans_plain(9), fill=MUTED_GRAY)
    col_w = (aw - 10) / 2
    row_h = 13.2
    for i, brief in enumerate(BRIEF_ITEMS):
        col, row = divmod(i, 12)
        bx = ax + col * (col_w + 10)
        by = by0 + 28 + row * row_h
        lead = "%d %s — " % (brief["num"], brief["place"])
        for size in (12, 11, 10.5, 10):
            lead_font = sans_bold(int(size))
            body_font = sans_plain(size)
            if (text_width(lead_font, lead)
                    + text_width(body_font, brief["text"]) <= col_w):
                break
        canvas.text((bx, by), lead, font=lead_font, fill=ACCENT_RED)
        canvas.text((bx + text_width(lead_font, lead), by), brief["text"],
                    font=body_font, fill=TEXT_INK)

    # ---- DATE CHECK
    dy0 = 966
    canvas.rectangle([MARGIN, dy0, PAGE_W - MARGIN, dy0 + 38], outline=ACCENT_RED,
                     width=1)
    canvas.rectangle([MARGIN, dy0, MARGIN + 96, dy0 + 38], fill=ACCENT_RED)
    canvas.text((MARGIN + 8, dy0 + 5), "DATE", font=sans_bold(12),
                fill=(255, 255, 255))
    canvas.text((MARGIN + 8, dy0 + 20), "CHECK", font=sans_bold(12),
                fill=(255, 255, 255))
    date_note = ("First reported Thursday 19 Nov, so NOT shown as Friday’s "
                 "news: Trump–Xi–Putin Shenzhen talks + ‘peace declaration’ · "
                 "ICJ Myanmar Rohingya genocide verdict (9–6) · GTA VI midnight "
                 "launch · $190.4m Van Gogh sale · Voyager 1 one-light-day "
                 "confirmation · Senate 48–51 Iran war-powers vote.")
    draw_wrapped(canvas, MARGIN + 104, dy0 + 3, sans_plain(11), date_note,
                 PAGE_W - MARGIN - (MARGIN + 104) - 6, TEXT_INK, leading=13)

    # ---- footer
    foot = ("Every story here happened, or was first reported, on Friday 20 "
            "November 2026. Officials’ counts are attributed. Sources named "
            "per story · Full list in SOURCES.md · Original drawings.")
    canvas.text((MARGIN, 1007), foot, font=sans_plain(10), fill=MUTED_GRAY)

    img.save(out_path, "PNG")
    return out_path


def main():
    target = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if target:
        os.makedirs(target, exist_ok=True)
        out = os.path.join(target, "entry.png")
    else:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    build_page(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
