"""Find lui/addiu (or ori) pairs that build a given EXE address: function pointers passed as callbacks.

    python -X utf8 tools/debug/xref.py 0x800d9050 0x800d92dc

Reports the address of the low-half instruction; pair matching is by immediate only (any register), so check the hit.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main(args):
    raw = (ROOT / 'work/disc/tree/SLPS_017.85').read_bytes()
    base = struct.unpack_from('<I', raw, 0x18)[0] - 0x800
    words = [struct.unpack_from('<I', raw, o)[0] for o in range(0x800, len(raw) - 3, 4)]
    for arg in args:
        target = int(arg, 0)
        lo = target & 0xFFFF
        hi = (target >> 16) + (1 if lo >= 0x8000 else 0)
        print(f'--- 0x{target:08x}')
        luis = {}
        for i, w in enumerate(words):
            op = w >> 26
            if op == 15 and w & 0xFFFF == hi:                     # lui rt, hi
                luis[(w >> 16) & 31] = i
            elif op in (9, 13) and w & 0xFFFF == lo:              # addiu / ori rt, rs, lo
                rs = (w >> 21) & 31
                if rs in luis and i - luis[rs] < 24:
                    print(f'  {base + 0x800 + 4 * i:08x}')
            # also catch the table form: the address stored as a data word
            if w == target:
                print(f'  data word at {base + 0x800 + 4 * i:08x}')


if __name__ == '__main__':
    main(sys.argv[1:])
