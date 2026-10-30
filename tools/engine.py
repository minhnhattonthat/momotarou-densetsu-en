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
from write_audit import Buffer

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
FREE1_END = 0x8003E308
# Digraphs: code 0x8000 | c1 << 7 | c2 (two printable ASCII chars, 0x9000-0xBF7E) is one u16 in the control range
# draw_string skipped as a no-op. The hook draws it as the two glyphs by calling draw_string on a 3-word string on
# the stack, as the {str} handler does, so English text costs one byte per letter. It lives in the sheet 1 block of
# glyph_prim (0x8003F644), freed the same way (that function's sheet 1 path now runs its sheet 0 path).
DIGRAPH = 0x8003F704
FREE2_END = 0x8003F790
NEXT = 0x8003E660                # draw_string: s2 += 2, next code
DRAW_STRING = 0x8003E128
REGS = {'$v0': 2, '$t1': 9}
PATCH = [                        # (address, original, replacement)
    (0x8003E1BC, 'sltiu $v0, $a2, 0x200', 'sltiu $v0, $a2, 0x400'),
    (0x8003E1C0, 'beqz $v0, 0x8003e260', 'beqz $v0, 0x8003e308'),
    (0x8003E1C8, 'andi $a0, $v1, 0xffff', 'andi $a0, $a2, 0x1ff'),
    (0x8003E1DC, 'nop', 'srl $t5, $a2, 9'),
    (0x8003E258, 'j 0x8003e3fc', f'j {HOOK:#x}'),
    (0x8003E25C, 'addiu $a0, $a0, 0xd', 'addu $v0, $v0, $t5'),
    (0x8003E430, 'beqz $v0, 0x8003e660', f'beqz $v0, {DIGRAPH:#x}'),   # control code past the jump table
    # glyph_prim(code a0, dest a1): same merge as above; a1 (a copy of code & 0xFFF) is freed for the sheet bit
    (0x8003F674, 'andi $a1, $a0, 0xffff', 'srl $t4, $a0, 9'),
    (0x8003F678, 'sltiu $v0, $a1, 0x200', 'sltiu $v0, $a0, 0x400'),
    (0x8003F67C, 'beqz $v0, 0x8003f704', 'beqz $v0, 0x8003f790'),
    (0x8003F684, 'andi $a0, $v1, 0xffff', 'andi $a0, $v1, 0x1ff'),
    (0x8003F700, 'addiu $v0, $zero, 0x1d', 'addiu $v0, $t4, 0x1d'),
    (0x8003F808, 'sltiu $v0, $a1, 0x800', 'sltiu $v0, $a0, 0x800'),
    # number printer 0x8003E8B8 ({num}/{gold} only): 8 px digit cells advanced 12 px ("took 3 4 da"); 8 = 1 px gap
    (0x8003EACC, 'addiu $v0, $v0, 0xc', 'addiu $v0, $v0, 8'),
    # field HUD 0x800D87A4: level label (段 -> tiny Lv) moves from after the number to the HP/SP label column,
    # the level number right-aligns to the HP/SP numbers' edge: "Lv 1 / HP 25 / SP 0"
    (0x800D87B0, 'addiu $a2, $zero, 0x20', 'addiu $a2, $zero, 8'),
    (0x800D8808, 'addiu $a1, $zero, 0x20', 'addiu $a1, $zero, 0x30'),
    # Status summary: the full "cards" suffix needs 24 px, but the original field has only 18.
    # Move the right-aligned count and suffix together, preserving their separation.
    (0x800DBF30, 'addiu $a1, $zero, 0xd4', 'addiu $a1, $zero, 0xc4'),
    (0x800DBF54, 'addiu $a2, $zero, 0xd8', 'addiu $a2, $zero, 0xc8'),
] + [
    # money boxes: the number (right-aligned to x) and the 両 label (FONT_6:556, x) move 8 px left for "ryo"
    (addr, f'addiu ${reg}, $zero, {x:#x}', f'addiu ${reg}, $zero, {x - 8:#x}')
    for addr, reg, x in [(0x80021884, 'a1', 0xA8), (0x800218A4, 'a2', 0xA8), (0x800368F0, 'a1', 0x48),
                         (0x80036914, 'a2', 0x48), (0x800D8BF0, 'a1', 0x48), (0x800D8C14, 'a2', 0x48),
                         (0x800D9810, 'a1', 0xA8), (0x800D9830, 'a2', 0xA8), (0x800DAD6C, 'a1', 0xA8),
                         (0x800DAD8C, 'a2', 0xA8), (0x800DB6A0, 'a1', 0x48), (0x800DB6E4, 'a2', 0x48)]
] + [
    # name entry 0x800DC3D0: cursor starts at column 0 (top-left 'A' of the English page), not 14 (あ, top-right)
    (0x800DC5FC, 'addiu $a0, $zero, 0xe', 'addiu $a0, $zero, 0'),
]
# Map-overlay layout patches (decompressed PAC entry, offset, original, replacement). Window descriptors start with
# u16 width, height in 8 px tiles (docs/re/windows.md §Window descriptors).
OVERLAY_PATCH = [
    # elevator floor list (maps 309-314, FONT_6:799-803): 6 tiles = 26 px cut "Floor 5" to "Floor"; 7 tiles = 34 px
    (f'0/07HMAP/{pac}:65', off, b'\x06\x00\x0c\x00', b'\x07\x00\x0c\x00')
    for pac, off in [('HMAP26.PAC', 0x31DC), ('HMAP2606.PAC', 0x1608), ('HMAP2607.PAC', 0xBB4)]
]
# Name-entry grids (docs/re/text.md): 15 x 5 cells, row-major left to right, each {glyph}{end}. The first page shown
# (hiragana at EXE 0xD4158) becomes English; hiragana moves to the 英数字 page (0xD43B8); katakana stays.
GRID_FIRST, GRID_ALNUM, GRID_CELLS = 0xD4158, 0xD43B8, 75
NAME_GRID = "ABCDEFGHIJKLMNOPQRSTUVWXYZ.,'-abcdefghijklmnopqrstuvwxyz!?& 0123456789+/():"
# 8x8 HUD label glyphs (codes 08xx, sheet 1 plane 0, cells at x = 8 * (code & 0xFF), y = 240; docs/re/text.md):
# 12 px letters don't fit their 8 px row pitch, so the kanji cells are redrawn as 3x7 letter pairs.
SMALL_Y, SMALL_PLANE = 240, 0
SMALL = {
    0x0A: ['#.#.##.', '#.#.#.#', '#.#.#.#', '###.##.', '#.#.#..', '#.#.#..', '#.#.#..'],   # 体 -> HP
    0x0C: ['.##.##.', '#...#.#', '#...#.#', '.#..##.', '..#.#..', '..#.#..', '##..#..'],   # 技 -> SP
    0x0D: ['#......', '#......', '#...#.#', '#...#.#', '#...#.#', '#...#.#', '###..#.'],   # 段 -> Lv
}


def digraph_asm():
    return [
        'lhu $t0, 0($s2)',                       # the code
        'ori $t3, $zero, 0x8000',                # load delay slot; {end}
        'srl $t1, $t0, 12',
        'addiu $t1, $t1, -9',
        'sltiu $t1, $t1, 3',
        f'beqz $t1, {NEXT:#x}',                  # not 0x9000-0xBFFF: skip it, as the game did
        'srl $t1, $t0, 7',
        'andi $t1, $t1, 0x7f',
        'andi $t0, $t0, 0x7f',
        f'addiu $t1, $t1, {EN_BASE - FIRST}',
        f'addiu $t0, $t0, {EN_BASE - FIRST}',
        'addiu $sp, $sp, -8',
        'sh $t1, 0($sp)',
        'sh $t0, 2($sp)',
        'sh $t3, 4($sp)',
        'move $a0, $s0',
        'move $a1, $s1',
        f'jal {DRAW_STRING:#x}',
        'move $a2, $sp',
        f'j {NEXT:#x}',
        'addiu $sp, $sp, 8',
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


def table(jp=ROOT / 'tbl/jp.tbl', pairs=True):
    """English codec: digraphs (encode pairs greedily, left to right), then ASCII at EN_BASE (both listed before the
    Japanese table, so they win over its full-width A-Z), then the Japanese table for its control codes.
    pairs=False: single glyphs only, for text not drawn by draw_string."""
    key = lambda code: struct.pack('<H', code).hex().upper()
    lines = [f'{key(code)}={s}' for s, code in digraphs().items()] if pairs else []
    lines += [f'{key(EN_BASE + c - FIRST)}={chr(c) if c != 0x20 else chr(92) + "s"}' for c in range(FIRST, LAST + 1)]
    return Table(lines + jp.read_text(encoding='utf-8-sig').splitlines())


def asm(lines, addr):
    from keystone import KS_ARCH_MIPS, KS_MODE_LITTLE_ENDIAN, KS_MODE_MIPS32, Ks
    ks = Ks(KS_ARCH_MIPS, KS_MODE_MIPS32 | KS_MODE_LITTLE_ENDIAN)
    out = bytearray()
    for i, line in enumerate(lines):
        pc = addr + 4 * i
        op, _, args = line.partition(' ')
        if op in ('j', 'jal', 'beqz'):           # keystone pads j with a nop and rejects absolute branch targets
            target = int(args.split()[-1], 16)
            word = ((2 if op == 'j' else 3) << 26 | target >> 2 & 0x3FFFFFF if op != 'beqz' else
                    4 << 26 | REGS[args.split(',')[0]] << 21 | (target - pc - 4) >> 2 & 0xFFFF)
            out += struct.pack('<I', word)
            continue
        enc, _ = ks.asm(line, pc)
        assert len(enc) == 4, (line, enc)        # one word each: keystone must not add delay-slot nops
        out += bytes(enc)
    return bytes(out)


def patch_exe(exe, audit=None):
    from capstone import CS_ARCH_MIPS, CS_MODE_LITTLE_ENDIAN, CS_MODE_MIPS32, Cs
    cs = Cs(CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)
    audit = audit if audit is not None else Buffer(exe, 'SLPS_017.85')
    b = audit.data
    for addr, old, new in PATCH:
        o = addr - EXE_BASE
        ins = next(cs.disasm(bytes(b[o:o + 4]), addr))
        assert f'{ins.mnemonic} {ins.op_str}'.replace(' ', '') == old.replace(' ', ''), (hex(addr), ins.op_str)
        audit.put(o, asm([new], addr), f'engine:{addr:08x}', expected=exe[o:o + 4])
    code = asm(hook_asm(), HOOK)
    w = bytes(widths())
    assert len(code) == TABLE - HOOK and TABLE + len(w) <= FREE1_END
    o = HOOK - EXE_BASE
    audit.put(o, code + w, 'engine:vwf-hook-widths')
    code = asm(digraph_asm(), DIGRAPH)
    assert DIGRAPH + len(code) <= FREE2_END
    o = DIGRAPH - EXE_BASE
    audit.put(o, code, 'engine:digraph-hook')
    assert len(NAME_GRID) == GRID_CELLS and exe[GRID_ALNUM:GRID_ALNUM + 4] == b'\x00\x00\x00\x80'   # 'Ａ'{end}
    audit.put(GRID_ALNUM, exe[GRID_FIRST:GRID_FIRST + 4 * GRID_CELLS], 'engine:kana-grid')
    for i, c in enumerate(NAME_GRID):
        audit.put(GRID_FIRST + 4 * i, struct.pack('<HH', EN_BASE + ord(c) - FIRST, 0x8000), f'engine:latin-grid:{i}')
    audit.verify(b)
    return bytes(b)


def digraphs():
    """{'ab': code} for every printable pair, except a second char of { or [ (that would eat the start of a
    {control} or [XX] token when encoding) and the pair \\s (a table line can't hold it)."""
    return {chr(a) + chr(c): 0x8000 | a << 7 | c for a in range(FIRST, LAST + 1) for c in range(FIRST, LAST + 1)
            if chr(c) not in '{[' and chr(a) + chr(c) != '\\s'}


def patch_font(font_pac, audit=None):
    """FONT.PAC with the English glyphs drawn into sheet 1 plane 1 cells 0xA0.. (other planes untouched)."""
    items = pac.unpack(font_pac)
    typ, blob, extra = items[FONT_ENTRY]
    t = bytearray(lzss.decompress(blob)[0])
    audit = audit if audit is not None else Buffer(t, f'0/03FONT/FONT.PAC:{FONT_ENTRY}')
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
            start = 20 + (cy + y) * stride + cx // 2
            audit.put(start, t[start:start + 6], f'font:{c:02x}:row{y}')
    for idx, rows in SMALL.items():
        for y in range(8):                  # row 0 blank, letters on rows 1-7 like the small digits
            for x in range(8):
                ink = 1 <= y and x < len(rows[y - 1]) and rows[y - 1][x] == '#'
                o = 20 + (SMALL_Y + y) * stride + (idx * 8 + x) // 2
                bit = 1 << (SMALL_PLANE + 4 * ((idx * 8 + x) & 1))
                t[o] = t[o] | bit if ink else t[o] & ~bit
            start = 20 + (SMALL_Y + y) * stride + idx * 4
            audit.put(start, t[start:start + 4], f'font:small{idx}:row{y}')
    audit.verify(t)
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
