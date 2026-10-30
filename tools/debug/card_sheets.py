"""Compare all 297 original cards with the current redraw, nine pairs per sheet (JP left, EN right).

    python -X utf8 tools/debug/card_sheets.py --out work/qa/cards/assets

These source-image comparisons supplement the actual album captures from album.lua; they do not replace them.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cards  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=Path('work/qa/cards/assets'))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    templates, names = cards.templates(), cards.names()
    for start in range(1, 298, 9):
        sheet = Image.new('RGB', (588, 444), '#383838')
        draw = ImageDraw.Draw(sheet)
        for j, n in enumerate(range(start, min(start + 9, 298))):
            pal, original = cards.card(n)
            new = cards.redraw(n, templates.get(cards.key(pal, original)), names[n - 1])
            x, y = j % 3 * 196, j // 3 * 148
            draw.text((x, y), str(n), fill='white')
            for k, pixels in enumerate((original, new)):
                im = Image.new('RGB', (cards.W, cards.H))
                im.putdata([pal[i] for i in pixels])
                sheet.paste(im, (x + k * 98, y + 12))
        sheet.resize((1176, 888), Image.Resampling.NEAREST).save(args.out / f'cards_{start:03}.png')
    print('33 original/English comparison sheets:', args.out)


if __name__ == '__main__':
    main()
