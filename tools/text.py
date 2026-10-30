"""Decode game text (docs/re/text.md).

    python -X utf8 tools/text.py table FILE.PAC ENTRY      # 0x10d string table: one line per string
    python -X utf8 tools/text.py at FILE[.PAC ENTRY] OFF    # one string at a byte offset
"""
import sys
from pathlib import Path

import extract
import lzss
import pac
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
TBL = Table.load(ROOT / 'tbl/jp.tbl')


def entry(path, idx):
    data = Path(path).read_bytes()
    o, s, t = pac.entries(data)[idx]
    b = data[o:o + s]
    return lzss.decompress(b)[0] if t & 0x10000 else b


def table_offsets(b):
    """u32 offsets from the block start, table ends at the lowest offset (extract.parse_table)."""
    return extract.parse_table(b)


def decode(b, off):
    return TBL.decode(b, off)


def main(a):
    if a[0] == 'table':
        b = entry(a[1], int(a[2]))
        for i, o in enumerate(table_offsets(b)):
            print(f'{i:4d} {o:#06x} {decode(b, o)[0]}')
    elif a[0] == 'at':
        b = entry(a[1], int(a[2])) if len(a) == 4 else Path(a[1]).read_bytes()
        print(decode(b, int(a[-1], 16))[0])


if __name__ == '__main__':
    main(sys.argv[1:])
