"""Collectible cards (CR_PG01-99.PAC, docs/re/graphics.md): 297 cards of 96x136 8bpp, card n at entry
(n-1)%3*2 of CR_PG<(n-1)//3+1>, its CLUT in the next entry.

    python -X utf8 tools/cards.py templates   # work/cards/template_<k>.png: clean background per card family

Cards of one family share a background (pink swirls for monsters, cream for villagers...); the per-pixel mode of
the family's colours is that background without names, art or labels (each card's own art is in the minority).
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

import extract
import gfx

ROOT = Path(__file__).resolve().parents[1]
W, H = 96, 136
MIN_FAMILY = 20                 # smaller families (boss cards with their own art) get no template


def loc(n):
    return f'30EV/CR_PG{(n - 1) // 3 + 1:02d}.PAC:{(n - 1) % 3 * 2}'


def card(n):
    """(palette RGB list, pixel indices) of card n."""
    path, e = loc(n).rsplit(':', 1)
    pal = [c[:3] for c in gfx.palette(gfx.entry(f'{path}:{int(e) + 1}'))]
    return pal, gfx.indices(gfx.entry(loc(n)))[3]


def names():
    """English card names, card 1..297 (HMAP8500_18 "<name>カード" strings, " Card" dropped)."""
    doc = extract.load(next((ROOT / 'script').rglob('HMAP8500_18.json')))
    out = [s['en'] for s in doc['strings'] if (s.get('jp') or '').endswith('カード')]
    assert len(out) == 297 and all(e.endswith(' Card') for e in out)
    return [e[:-5] for e in out]


def key(pal, px):
    return pal[px[133 * W + 60]]                # bottom border colour: one per background family


def families():
    fam = {}
    for n in range(1, 298):
        pal, px = card(n)
        fam.setdefault(key(pal, px), []).append(n)
    return {k: v for k, v in fam.items() if len(v) >= MIN_FAMILY}


def glyphish(c):
    """Any grey (white, black and the antialiasing between): lettering colours, never a card background's."""
    return max(c) - min(c) < 16


def templates():
    """{family key: [RGB per pixel]} by per-pixel mode over the family's cards, lettering colours outvoted."""
    out = {}
    for k, ns in families().items():
        cols = [card(n) for n in ns]
        t = []
        for i in range(W * H):
            votes = Counter(pal[px[i]] for pal, px in cols)
            bg = [c for c, _ in votes.most_common() if not glyphish(c)]
            t.append(bg[0] if bg else votes.most_common(1)[0][0])
        out[k] = t
    return out


def main(argv):
    if argv[:1] == ['templates']:
        dst = ROOT / 'work/cards'
        dst.mkdir(parents=True, exist_ok=True)
        for i, (k, t) in enumerate(templates().items()):
            im = Image.new('RGB', (W, H))
            im.putdata(t)
            im.resize((W * 3, H * 3), Image.NEAREST).save(dst / f'template_{i}.png')
            print(dst / f'template_{i}.png', k, len(families()[k]), 'cards')


if __name__ == '__main__':
    main(sys.argv[1:])
