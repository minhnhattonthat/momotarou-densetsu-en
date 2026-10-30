"""One-off: write the first draft of tbl/jp.tbl (kana/punctuation read by eye from `font.py sheet`, kanji from the
font_ocr.py guesses in work/font/ocr.tsv). tbl/jp.tbl is the source of truth after that; this refuses to overwrite it.

Keys are the u16 codes as little-endian bytes (`2B00=あ`), so tools/tbl.py decodes the game's u16 strings directly.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tbl/jp.tbl'
# codes 0x00-0xE6; '_' = blank cell (not emitted). 0x23 is the full-width space.
LOW = ("ABCDEFGHIJKLMNOPQRSTUVWXYZ&☆○◎□△()♥ ____■✕ぁあぃいぅう"
       "ぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづて"
       "でとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆ"
       "ょよらりるれろゎわをんァアィイゥウェエォオカガキギクグケゲコゴサ"
       "ザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフ"
       "ブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヲンヴヵヶ_"
       "__、。，・：；？！ー―～…「」『』＋－×÷＝")
CTRL = {0x8000: 'end', 0x8001: 'n', 0x8002: 'sp8', 0x8003: 'sp13', 0x8004: 'wait', 0x8005: 'num', 0x8006: 'c06',
        0x8007: 'str', 0x8008: 'c08', 0x8009: 'c09', 0x800A: 'c0a', 0x800B: 'col0', 0x800C: 'col2',
        0x800D: 'col4', 0x800E: 'col6', 0x800F: 'col8', 0x8010: 'col10', 0x8018: 'gold', 0x8019: 'c19',
        0x801A: 'c1a', 0x8027: 'name', 0x8028: 'c28', 0x802C: 'c2c'}
for c in range(0x8011, 0x802F):
    CTRL.setdefault(c, 'c%02x' % (c & 0xFF))


def key(code):
    return code.to_bytes(2, 'little').hex().upper()


def main():
    if OUT.exists():
        sys.exit(f'{OUT} exists; edit it by hand')
    assert len(LOW) == 0xE7, len(LOW)
    lines = ['# Momotarou Densetsu (PS1) text table: u16 little-endian codes (docs/re/text.md).',
             '# 0000-00E6 read by eye (verified on in-game text); 00E7+ and 1xxx kanji are OCR guesses until reviewed.',
             '# 07xx = 8x12 half-width glyphs (digits), 08xx = 8x8 glyphs: listed as [xx] escapes until mapped.']
    seen = set()
    for c, ch in enumerate(LOW):
        if ch == '_':
            continue
        if c == 0x23:
            ch = r'\s'
        lines.append(f'{key(c)}={ch}')
        seen.add(ch)
    for line in (ROOT / 'work/font/ocr.tsv').read_text(encoding='utf-8').splitlines():
        code, ch, *_ = line.split('\t')
        code = int(code, 16)
        if code < 0xE7:
            continue
        lines.append(f'{key(code)}={ch}')
    for c, name in sorted(CTRL.items()):
        lines.append(f'{key(c)}={{{name}}}')
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()
