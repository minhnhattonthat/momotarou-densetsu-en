"""Reviewer pairs file (docs/reviewer-brief.md): JP and English of translation batches, in game order.

    python -X utf8 tools/pairs.py NAME bNNN ...    -> work/tl/review/NAME.txt
"""
import sys

import batches


def main(argv):
    name, names = argv[0], argv[1:]
    us = {u['id']: u for u in batches.units().values()}
    out = []
    for b in names:
        out.append(f'## {b}')
        en = dict(r for r in batches.read_tsv(batches.TL / f'{b}.out.tsv'))
        for row in batches.read_tsv(batches.TL / f'{b}.tsv'):
            i = row[0]
            out.append(f'>> {i} | {batches.show_jp(us[i]["jp"]) if i in us else row[4]}')
            out.append(f'   {en.get(i, "(missing)")}')
    path = batches.TL / 'review' / f'{name}.txt'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(out) + '\n', encoding='utf-8', newline='\n')
    print(path)


if __name__ == '__main__':
    main(sys.argv[1:])
