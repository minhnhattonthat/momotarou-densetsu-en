"""Lint errors with each string's JP and English side by side, for reviewing glossary/honorific errors.

    python -X utf8 tools/lintview.py [ERROR-SUBSTRING]   # e.g. honorific, glossary:
"""
import contextlib
import io
import sys

import batches
import lint


def main(argv):
    want = argv[0] if argv else ''
    us = {u['id']: u for u in batches.units().values()}
    ds = batches.docs()
    by_id = {s['id']: s for _, d in ds for s in d['strings']}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        lint.run()
    seen = set()
    for line in buf.getvalue().splitlines():
        if not line.startswith('ERROR') or want not in line or line in seen:
            continue
        seen.add(line)
        i = line.split()[1].rstrip(':')
        u = us.get(i)
        print(line)
        if u:
            print('  JP', u['jp'].replace('{n}', ' '))
            print('  EN', by_id[i].get('en', '').replace('{n}', ' '))


if __name__ == '__main__':
    main(sys.argv[1:])
