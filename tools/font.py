"""Text font (docs/re/text.md): FONT.PAC entries 2-3, 4bpp 256x256 TIMs, 12x12 cells, 21 per row, 21 rows.

Each bit plane of a sheet is its own 1bpp page. Text code = plane << 12 | sheet << 9 | cell (cell 0-440, row-major),
sheet 0 = FONT.PAC entry 2, sheet 1 = entry 3: verified on 昔 (0x2AE), 々 (0x1078), 回復 (0x101E-F), kana (0x2B..).

    python -X utf8 tools/font.py sheet OUT.png [FROM TO]   # labelled cell sheet over linear cell index (0-1763)
"""
import sys
from pathlib import Path

import numpy as np

import lzss
import pac
import tim

ROOT = Path(__file__).resolve().parents[1]
FONT_PAC = ROOT / 'work/disc/tree/0/03FONT/FONT.PAC'
CELL, PER_ROW, PER_PAGE = 12, 21, 441
PAGES = ((2, 0), (2, 1), (3, 0), (3, 1))


def pages(path=FONT_PAC):
    return pages_from(path.read_bytes())


def pages_from(data):
    ent = pac.entries(data)
    out = []
    for idx, plane in PAGES:
        o, s, _ = ent[idx]
        *_, w, h, raw = tim.block(lzss.decompress(data[o:o + s])[0])
        px = np.frombuffer(raw, np.uint8).reshape(h, w * 2)
        nib = np.empty((h, w * 4), np.uint8)
        nib[:, 0::2], nib[:, 1::2] = px & 15, px >> 4
        out.append((nib >> plane) & 1)
    return out


def code_to_index(code):
    """Text code -> linear cell index (page * 441 + cell), page order as PAGES."""
    plane, sheet, c = code >> 12 & 1, code >> 9 & 1, code & 0x1FF
    assert c < PER_PAGE and not code & ~0x13FF, hex(code)
    return ((sheet << 1) | plane) * PER_PAGE + c


def index_to_code(n):
    p, c = divmod(n, PER_PAGE)
    return (p & 1) << 12 | (p >> 1) << 9 | c


def cell(pg, n):
    p, c = divmod(n, PER_PAGE)
    y, x = divmod(c, PER_ROW)
    return pg[p][y * CELL:(y + 1) * CELL, x * CELL:(x + 1) * CELL]


def sheet(out, lo=0, hi=PER_PAGE * len(PAGES), zoom=3, cols=16):
    from PIL import Image, ImageDraw
    pg = pages()
    codes = list(range(lo, hi))
    cw, ch = (CELL + 2) * zoom, (CELL + 2) * zoom + 10
    rows = (len(codes) + cols - 1) // cols
    im = Image.new('RGB', (cols * cw, rows * ch), (40, 40, 60))
    dr = ImageDraw.Draw(im)
    for i, n in enumerate(codes):
        x, y = i % cols * cw, i // cols * ch
        g = Image.fromarray(cell(pg, n) * 255).resize((CELL * zoom, CELL * zoom), Image.NEAREST)
        im.paste(g, (x + zoom, y + 10))
        dr.text((x + 1, y), f'{n:03x}', fill=(255, 220, 80))
    im.save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        sheet(sys.argv[2], *(int(a, 16) for a in sys.argv[3:5]))
