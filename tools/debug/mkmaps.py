"""Write tools/debug/maps.txt from a RAM dump (any field-mode ram_*.bin): one line per map id.

    python tools/debug/mkmaps.py work/qa/.../ram_004200.bin
Columns: id, disc file, room (sub-map in the PAC), parent map (towns/dungeons that own an interior), raw bytes.
Map table 0x800729FC (36-byte entries, first u16 = file index, last u16 = room); second table 0x80077FE4
(16 bytes: overlay init, EXE init, goto_map callback, parent s16). docs/re/debug.md.
"""
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
r = open(sys.argv[1], 'rb').read()
files = dict(l.split(' ', 1) for l in (ROOT / 'tools/debug/files.txt').read_text().splitlines())
out = ['# id file room parent | map-table bytes 2..35']
i = 0
while True:
    e = r[0x729FC + 36 * i:0x729FC + 36 * i + 36]
    f = struct.unpack_from('<h', e)[0]
    if not 0 < f < 600:
        break
    parent = struct.unpack_from('<h', r, 0x77FE4 + 16 * i + 12)[0]
    room = struct.unpack_from('<H', e, 34)[0]
    out.append(f"{i} {files[str(f)].split(chr(92))[-1]} {room} {parent} | {e[2:].hex(' ')}")
    i += 1
(ROOT / 'tools/debug/maps.txt').write_text('\n'.join(out) + '\n')
print(i, 'maps')
