"""Read-only MIPS overlay inspection: code.py FILE[:ENTRY] BASE [--calls ADDRESS ... | --range START SIZE].

Accepts compressed PAC entries and raw files; prints call-site context or a precise disassembly range.
"""
import argparse
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import extract
import pac


def read(location):
    path, sep, entry = location.rpartition(':')
    if sep and entry.isdigit():
        raw = Path(path).read_bytes()
        return extract.blob(raw, *pac.entries(raw)[int(entry)])
    return Path(location).read_bytes()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('file')
    p.add_argument('base', type=lambda s: int(s, 0))
    p.add_argument('--calls', nargs='+', type=lambda s: int(s, 0))
    p.add_argument('--range', nargs=2, type=lambda s: int(s, 0))
    p.add_argument('--refs', nargs='+', type=lambda s: int(s, 0))
    p.add_argument('--ctx', type=int, default=10)
    a = p.parse_args()
    raw = read(a.file)
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    cs.skipdata = True
    spans = [(a.range[0] - a.base, a.range[0] - a.base + a.range[1])] if a.range else []
    for target in a.refs or ():
        lo = target & 0xFFFF
        hi = (target >> 16) + (lo >= 0x8000)
        luis = {}
        for off in range(0, len(raw) - 3, 4):
            word = struct.unpack_from('<I', raw, off)[0]
            op = word >> 26
            if op == 15:
                luis[word >> 16 & 31] = (off, word & 0xFFFF)
            last, upper = luis.get(word >> 21 & 31, (-1000, 0))
            if word == target or (op in (9, 13) and word & 0xFFFF == lo
                                 and off - last < 96 and upper == (hi if op == 9 else target >> 16)):
                spans.append((max(0, off - 4 * a.ctx), min(len(raw), off + 16)))
    for off in range(0, len(raw) - 3, 4) if a.calls else ():
        word = struct.unpack_from('<I', raw, off)[0]
        if word >> 26 == 3 and (0x80000000 | ((word & 0x3FFFFFF) << 2)) in a.calls:
            spans.append((max(0, off - 4 * a.ctx), min(len(raw), off + 8)))
    for lo, hi in spans:
        print(f'-- {a.base + lo:08x}')
        for ins in cs.disasm(raw[lo:hi], a.base + lo):
            print(f'{ins.address:08x}: {ins.mnemonic:7} {ins.op_str}')


if __name__ == '__main__':
    main()
