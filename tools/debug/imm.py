"""List `addiu/ori rt, zero, N` immediates in a code file (EXE, SHOP.MMB, an overlay entry) with context: who passes a
string index. label_refs.py does the same for the EXE only.

    python -X utf8 tools/debug/imm.py work/disc/tree/0/03FONT/SHOP.MMB 0x80155000 259 260 [--ctx 8]
"""
import struct
import sys

from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs


def main(argv):
    ctx = int(argv[argv.index('--ctx') + 1]) if '--ctx' in argv else 0
    args = [a for i, a in enumerate(argv) if a != '--ctx' and (i == 0 or argv[i - 1] != '--ctx')]
    raw, base = open(args[0], 'rb').read(), int(args[1], 0)
    want = {int(a, 0) for a in args[2:]}
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    for off in range(0, len(raw) - 3, 4):
        w = struct.unpack_from('<I', raw, off)[0]
        if w >> 26 in (9, 13) and not w >> 21 & 31 and w & 0xFFFF in want:
            print(f'{base + off:08x}: index {w & 0xFFFF} -> r{(w >> 16) & 31}')
            if ctx:
                lo = max(0, off - 4 * ctx)
                for ins in cs.disasm(raw[lo:off + 4 * ctx], base + lo):
                    print(f'    {ins.address:08x}: {ins.mnemonic:7} {ins.op_str}')


if __name__ == '__main__':
    main(sys.argv[1:])
