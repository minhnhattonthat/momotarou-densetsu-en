"""English text engine (phase 5, docs/re/engine.md): VWF in the EXE's draw_string + English glyphs in the font.

    python -X utf8 tools/engine.py sheet OUT.png   # the English glyph cells as the game will draw them

English letters are glyph codes EN_BASE + (ord(c) - 0x20): cells 0xA0-0xFE of sheet 1 plane 1 (FONT.PAC entry 3),
blank and unused by the Japanese script. draw_string draws one 12x12 sprite per glyph and advanced x by 13; the hook
advances by a per-glyph width for these codes and by 13 for every other glyph, so Japanese text still draws as before.
"""
import struct
import sys
from pathlib import Path

import numpy as np

import lzss
import pac
from tbl import Table

ROOT = Path(__file__).resolve().parents[1]
FONT_TXT = ROOT / 'fonts/en12.txt'
EN_BASE = 0x12A0                 # code of ' ' (cell 0xA0 of sheet 1 plane 1)
FIRST, LAST = 0x20, 0x7E
SPACE_W = 4
TOP = 2                          # en12.txt rows go to cell rows 2..11
FONT_ENTRY, PLANE = 3, 1         # FONT.PAC entry 3 = sheet 1
EXE_BASE = 0x80010000 - 0x800    # RAM address of EXE file offset 0

# draw_string (0x8003E128) patch. The sheet 0 and sheet 1 glyph paths were the same code but for the cell base and
# the tpage (0x1D / 0x1E); sheet 1 now runs the sheet 0 path (cell = code & 0x1FF, tpage += code >> 9), which frees
# the old sheet 1 block at 0x8003E260-0x8003E307 for the hook and its width table.
HOOK = 0x8003E260
TAIL = 0x8003E3FC                # common tail: stores y, tpage, the new x (a0) at gp+0x3E4
TABLE = HOOK + 48
REGS = {'$v0': 2, '$t1': 9}
PATCH = [                        # (address, original, replacement)
    (0x8003E1BC, 'sltiu $v0, $a2, 0x200', 'sltiu $v0, $a2, 0x400'),
    (0x8003E1C0, 'beqz $v0, 0x8003e260', 'beqz $v0, 0x8003e308'),
    (0x8003E1C8, 'andi $a0, $v1, 0xffff', 'andi $a0, $a2, 0x1ff'),
    (0x8003E1DC, 'nop', 'srl $t5, $a2, 9'),
    (0x8003E258, 'j 0x8003e3fc', f'j {HOOK:#x}'),
    (0x8003E25C, 'addiu $a0, $a0, 0xd', 'addu $v0, $v0, $t5'),
]


def hook_asm():
    hi, lo = (TABLE + 0x8000) >> 16, (TABLE & 0xFFFF) - (0x10000 if TABLE & 0x8000 else 0)
    return [
        'lhu $t0, 0($s2)',                       # the glyph code (s2 = string pointer)
        f'lui $t2, {hi:#x}',                     # load delay slot: t0 isn't loaded yet
        f'addiu $t0, $t0, {-EN_BASE}',
        f'sltiu $t1, $t0, {LAST - FIRST + 1}',
        'beqz $t1, 0x8003e288',
        'addu $t2, $t2, $t0',
        f'lbu $t3, {lo}($t2)',
        'nop',                                   # load delay
        f'j {TAIL:#x}',
        'addu $a0, $a0, $t3',
        f'j {TAIL:#x}',                          # 0x8003E288: not an English glyph
        'addiu $a0, $a0, 0xd',
    ]


def glyphs(path=FONT_TXT):
    """{char: list of row strings ('#' ink)}."""
    out, cur = {}, None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.startswith('#') and cur is None or not line.strip():
            continue
        if line.startswith('= '):
            cur = out[line[2:]] = []
        else:
            cur.append(line)
    return out


def widths(g=None):
    """Advance in px for each code EN_BASE.. (FIRST..LAST)."""
    g = g or glyphs()
    return [SPACE_W if c == FIRST else max(len(r.rstrip('.')) for r in g[chr(c)]) + 1 for c in range(FIRST, LAST + 1)]


def table(jp=ROOT / 'tbl/jp.tbl'):
    """English codec: ASCII at EN_BASE (listed first, so it wins over the Japanese table's full-width A-Z), then the
    Japanese table for its control codes."""
    lines = [f'{struct.pack("<H", EN_BASE + c - FIRST).hex().upper()}={chr(c) if c != 0x20 else chr(92) + "s"}'
             for c in range(FIRST, LAST + 1)]
    return Table(lines + jp.read_text(encoding='utf-8-sig').splitlines())


def asm(lines, addr):
    from keystone import KS_ARCH_MIPS, KS_MODE_LITTLE_ENDIAN, KS_MODE_MIPS32, Ks
    ks = Ks(KS_ARCH_MIPS, KS_MODE_MIPS32 | KS_MODE_LITTLE_ENDIAN)
    out = bytearray()
    for i, line in enumerate(lines):
        pc = addr + 4 * i
        op, _, args = line.partition(' ')
        if op in ('j', 'beqz'):                  # keystone pads j with a nop and rejects absolute branch targets
            target = int(args.split()[-1], 16)
            word = (2 << 26 | target >> 2 & 0x3FFFFFF if op == 'j' else
                    4 << 26 | REGS[args.split(',')[0]] << 21 | (target - pc - 4) >> 2 & 0xFFFF)
            out += struct.pack('<I', word)
            continue
        enc, _ = ks.asm(line, pc)
        assert len(enc) == 4, (line, enc)        # one word each: keystone must not add delay-slot nops
        out += bytes(enc)
    return bytes(out)


def patch_exe(exe):
    from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    b = bytearray(exe)
    for addr, old, new in PATCH:
        o = addr - EXE_BASE
        ins = next(cs.disasm(bytes(b[o:o + 4]), addr))
        assert f'{ins.mnemonic} {ins.op_str}'.replace(' ', '') == old.replace(' ', ''), (hex(addr), ins.op_str)
        b[o:o + 4] = asm([new], addr)
    code = asm(hook_asm(), HOOK)
    w = bytes(widths())
    assert len(code) == TABLE - HOOK and TABLE + len(w) <= 0x8003E308
    o = HOOK - EXE_BASE
    b[o:o + len(code) + len(w)] = code + w
    return bytes(b)


def patch_font(font_pac):
    """FONT.PAC with the English glyphs drawn into sheet 1 plane 1 cells 0xA0.. (other planes untouched)."""
    items = pac.unpack(font_pac)
    typ, blob, extra = items[FONT_ENTRY]
    t = bytearray(lzss.decompress(blob)[0])
    w16, h = struct.unpack_from('<HH', t, 16)
    stride = w16 * 2
    g = glyphs()
    for c in range(FIRST, LAST + 1):
        cell = EN_BASE - 0x1200 + c - FIRST
        cx, cy = cell % 21 * 12, cell // 21 * 12
        rows = g.get(chr(c), [])
        for y in range(12):
            for x in range(12):
                ink = TOP <= y < TOP + len(rows) and x < len(rows[y - TOP]) and rows[y - TOP][x] == '#'
                o = 20 + (cy + y) * stride + (cx + x) // 2
                bit = 1 << (PLANE + 4 * ((cx + x) & 1))
                t[o] = t[o] | bit if ink else t[o] & ~bit
    items[FONT_ENTRY] = (typ, lzss.compress(bytes(t)) if typ & 0x10000 else bytes(t), extra)
    return pac.pack(items)


def sheet(out):
    from PIL import Image
    import font
    w = widths()
    page = font.pages_from(patch_font(font.FONT_PAC.read_bytes()))[3]
    img = np.zeros((14 * 6, 16 * 16), np.uint8)
    for i in range(LAST - FIRST + 1):
        cell = EN_BASE - 0x1200 + i
        y, x = i // 16 * 14, i % 16 * 16
        img[y:y + 12, x:x + 12] = page[cell // 21 * 12:cell // 21 * 12 + 12, cell % 21 * 12:cell % 21 * 12 + 12] * 255
        img[y + 12, x:x + w[i]] = 96
    Image.fromarray(img).resize((img.shape[1] * 3, img.shape[0] * 3), Image.NEAREST).save(out)


if __name__ == '__main__':
    if sys.argv[1:2] == ['sheet']:
        sheet(sys.argv[2])
