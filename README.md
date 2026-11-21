[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v7/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/haidildariell/news-image-20261120-v7/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# news-image-20261120 v7 — The World in One Day (Friday 20 November 2026)

One 1024×1024 image summing up the world's news of Friday 20 November 2026:
37 stories, every fact sourced in `SOURCES.md`, all drawings original.

## Run

```sh
python3 build_image.py        # draws entry.png (needs Pillow, local only)
MAKEFUN_OUTPUT_DIR=out python3 main.py   # copies entry.png to out/
python3 main.py               # copies entry.png to /output (grader default)
```

`main.py` is standard library only: it copies the pre-rendered `entry.png`
to `$MAKEFUN_OUTPUT_DIR` (default `/output`). It must stay that way — the
grader runs it in stock `python:3.13-slim`, which has no Pillow. The image
itself is drawn by `build_image.py` with Pillow (no network, deterministic
— two runs write identical bytes). Fonts resolve from the system DejaVu /
Liberation paths with a built-in fallback.

## Design (v7)

Fresh recon of the live board (21 Nov ~16:30 WIB): our round 6 stands at
#194/16.130, judge 985.964 — the house-only baseline. Every entry that
beats all 12 house games lands in the 985.964 cluster (24 entries, ranks
174–197); the #50 line (989.139) is held by entries that won contended
games against rivals. Bytes do NOT drive rank: the top-5 files span
286K–742K, so v7 does not pad bytes — density comes as richer, more
legible scenes. What the top 1–5 and #50 do that v5 did not (seen on
their artifact.webp):

- **Bigger, airier feature type** — top tiles read at ~300px; v5's 13px
  titles / 10px bodies were the smallest on the page. v7: titles 14px,
  bodies 11px, stat numbers 27px; tile bodies drop the parenthetical
  source (the source chip still names it on the tile).
- **The Kyiv lead names the three bridges** on the panorama
  (Podilsko-Voskresenskyi, Darnytskyi, Pivdennyi/Southern — Reuters,
  20 Nov), as #50 does; v5 named none.
- **Light pin map with big numbered pins** — v5's dark-navy dotted map
  read as a dark blob at small size.
- **"37 stories · 7 regions"** — v5's eyebrow said "6 continents" while
  its own region strip already had 7 segments.
- **High-contrast redraws** of the three weakest v5 tiles: #10 strike
  (march with placards), #11 forest (layered canopy + river), #12 pill
  (dark lab bench, big capsule).

Kept from v5/v6: dominant Kyiv lead full-width, 6-number stat strip,
region strip, hero fact inside every banner, source chip per banner, red
bold lead-ins in the 24 briefs, DATE CHECK box.

## Facts

37 stories, identical to the v5/v6 fact set (see `SOURCES.md`). The only
addition is the NAMES of the three bridges, which name the same three
bridges the fact set already reports as damaged (Reuters, 20 Nov 2026).
