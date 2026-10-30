"""Find immediate label indices in EXE MIPS code for width-consumer tracing.

    python -X utf8 tools/debug/label_refs.py 577 578
    python -X utf8 tools/debug/label_refs.py --range 0x800dbe8c 0x130
    python -X utf8 tools/debug/label_refs.py --unmeasured  # exit 1 while width coverage is incomplete

Candidates are not automatically proven string references; inspect the surrounding call.
"""
import struct
import sys
from pathlib import Path

from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs

ROOT = Path(__file__).resolve().parents[2]


def main(args):
    if args == ['--unmeasured']:
        sys.path.insert(0, str(ROOT / 'tools'))
        import insert
        import layout
        missing = [s for _, d in insert.docs() for s in d['strings']
                   if s.get('en') and s.get('jp') and 'data' not in s
                   and layout.BOX[layout.box(s['id'], s['jp'])][0] is None]
        for s in missing:
            print(s['id'], repr(s['en']))
        print(f'{len(missing)} authored labels without a measured budget (docs/re/windows.md)')
        return int(bool(missing))
    raw = (ROOT / 'work/disc/tree/SLPS_017.85').read_bytes()
    base = struct.unpack_from('<I', raw, 0x18)[0] - 0x800
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    if args[:1] == ['--range']:
        start, size = int(args[1], 0), int(args[2], 0)
        for ins in cs.disasm(raw[start - base:start - base + size], start):
            print(f'{ins.address:08x}: {ins.mnemonic:7} {ins.op_str}')
        return
    for arg in args:
        index = int(arg, 0)
        print(f'--- index {index} (0x{index:x})')
        for off in range(0x800, len(raw) - 4, 4):
            w = struct.unpack_from('<I', raw, off)[0]
            if w >> 26 not in (9, 13) or w >> 21 & 31 or w & 0xFFFF != index:
                continue
            lo, hi = max(0x800, off - 32), off + 36
            for ins in cs.disasm(raw[lo:hi], base + lo):
                print(f'{">" if ins.address == base + off else " "} {ins.address:08x}: {ins.mnemonic:7} {ins.op_str}')


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]) or 0)
