"""Static graphics sweep (docs/re/graphics.md): render every unique image in every PAC/BIN file to numbered sheets.

    python -X utf8 tools/gfxdump.py OUTDIR [--per 24]
Writes OUTDIR/sheet_NNN.png (each tile labelled with its index) and OUTDIR/index.tsv
(index, sha1, first file:entry, type, bpp, w x h, VRAM x,y, other copies). 4bpp/8bpp drawn as a grey ramp of the
pixel index (the palette is a separate entry), 16bpp as colour. Every skipped entry is printed with the reason.
"""
import argparse
import hashlib
import struct
from pathlib import Path

from PIL import Image, ImageDraw

import lzss
import pac

ROOT = Path(__file__).resolve().parents[1]
TREE = ROOT / 'work/disc/tree'


def render(raw):
    magic, flags, size, x, y, w, h = struct.unpack_from('<IIIHHHH', raw, 0)
    data = raw[20:20 + size - 12]
    bpp = (4, 8, 16, 24)[flags & 3]
    if bpp == 4:
        px = bytearray()
        for b in data[:w * 2 * h]:
            px += bytes(((b & 15) * 17, (b >> 4) * 17))
        im = Image.frombytes('L', (w * 4, h), bytes(px))
    elif bpp == 8:
        im = Image.frombytes('L', (w * 2, h), bytes(data[:w * 2 * h]))
    elif bpp == 16:
        im = Image.new('RGB', (w, h))
        p = im.load()
        for i in range(w * h):
            c = struct.unpack_from('<H', data, i * 2)[0]
            p[i % w, i // w] = ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3)
    else:
        raise ValueError('24bpp')
    return im, bpp, x, y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--per', type=int, default=24)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    seen, order = {}, []
    files = sorted(p for p in TREE.rglob('*') if p.suffix in ('.PAC',) and p.is_file())
    for p in files:
        d = p.read_bytes()
        for i, (o, s, t) in enumerate(pac.entries(d)):
            if not s:
                continue
            b = d[o:o + s]
            if t & 0x10000:
                b = lzss.decompress(b)[0]
            if len(b) < 20 or struct.unpack_from('<I', b, 0)[0] != 0x12 and struct.unpack_from('<I', b, 0)[0] != 0x10:
                continue
            name = f'{p.relative_to(TREE).as_posix()}:{i}'
            h = hashlib.sha1(b).hexdigest()
            if h in seen:
                seen[h][1].append(name)
                continue
            try:
                im, bpp, x, y = render(b)
            except Exception as ex:  # noqa: BLE001 - report every skip
                print('skip', name, hex(t), ex)
                continue
            seen[h] = (len(order), [name])
            order.append((h, name, t, bpp, im, x, y))
    with open(out / 'index.tsv', 'w', encoding='utf-8', newline='\n') as f:
        for k, (h, name, t, bpp, im, x, y) in enumerate(order):
            f.write(f'{k}\t{h[:12]}\t{name}\t{t:#x}\t{bpp}\t{im.width}x{im.height}\t{x},{y}\t{" ".join(seen[h][1][1:])}\n')
    cell = 260
    for s in range(0, len(order), a.per):
        chunk = order[s:s + a.per]
        cols = 6
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cell, rows * (cell + 14)), (60, 0, 60))
        dr = ImageDraw.Draw(sheet)
        for j, (h, name, t, bpp, im, x, y) in enumerate(chunk):
            im = im.convert('RGB')
            im.thumbnail((cell - 4, cell - 4))
            cx, cy = j % cols * cell, j // cols * (cell + 14)
            sheet.paste(im, (cx + 2, cy + 14))
            dr.text((cx + 2, cy), f'{s + j} {name.split("/")[-1]}', fill=(255, 255, 0))
        sheet.save(out / f'sheet_{s // a.per:03d}.png')
    print(len(order), 'unique images,', sum(len(v[1]) for v in seen.values()), 'total')


if __name__ == '__main__':
    main()
