"""Scan text reached by the final disc's pointers, including compressed PACs.

The shared jp_left.py scanner cannot follow this game's compressed containers or
its 0x8000-terminated u16 strings. Export the actual reachable bytes, then scan
that corpus with the runtime codec (including English digraphs), without --orig.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import engine
import extract
import insert
import pac
from skill import SKILL


class Disc:
    def __init__(self, path):
        self.path = Path(path)
        self.files = {}
        pvd = self.read(16, 2048)
        if pvd[1:6] != b'CD001':
            raise ValueError('expected raw Mode-2 ISO9660 disc')
        root = pvd[156:]
        self.walk('', struct.unpack_from('<I', root, 2)[0], struct.unpack_from('<I', root, 10)[0])

    def read(self, lba, size):
        out = bytearray()
        with self.path.open('rb') as f:
            for i in range((size + 2047) // 2048):
                f.seek((lba + i) * 2352 + 24)
                out.extend(f.read(2048))
        if len(out) < size:
            raise ValueError('truncated disc')
        return bytes(out[:size])

    def walk(self, prefix, lba, size):
        data = self.read(lba, size)
        at = 0
        while at < len(data):
            n = data[at]
            if not n:
                at = (at // 2048 + 1) * 2048
                continue
            record = data[at:at + n]
            at += n
            name = record[33:33 + record[32]]
            if name in (b'\0', b'\1'):
                continue
            name = name.decode('ascii').split(';')[0]
            start, length = struct.unpack_from('<I', record, 2)[0], struct.unpack_from('<I', record, 10)[0]
            path = prefix + name
            if record[25] & 2:
                self.walk(path + '/', start, length)
            else:
                self.files[path] = (start, length)

    def file(self, path):
        return self.read(*self.files[path])


def u32(b, off):
    return struct.unpack_from('<I', b, off)[0]


def pointer_target(b, pointer, base):
    kind, offset = pointer.split('@')
    at = int(offset, 16)
    if kind == 'word':
        address = u32(b, at)
    elif kind == 'lui':
        hi, lo = u32(b, at), u32(b, at + 4)
        if hi >> 26 != 15 or lo >> 26 not in (9, 13):
            raise ValueError(f'unexpected MIPS pointer at {at:x}')
        low = lo & 0xFFFF
        if lo >> 26 == 9 and low & 0x8000:
            low -= 0x10000
        address = ((hi & 0xFFFF) << 16) + low
    else:
        raise ValueError(kind)
    target = address - base
    if not 0 <= target < len(b):
        raise ValueError(f'pointer outside container: {pointer} -> {target:x}')
    return target


def string_at(b, off):
    if off & 1 or not 0 <= off < len(b):
        raise ValueError(f'bad string offset {off:x}')
    end = off
    while end + 2 <= len(b):
        word = struct.unpack_from('<H', b, end)[0]
        end += 2
        if word == 0x8000:
            return b[off:end]
    raise ValueError(f'unterminated text at {off:x}')


def scan(image, out):
    disc = Disc(image)
    out.mkdir(parents=True, exist_ok=True)
    corpus, locations, cache = bytearray(), [], {}
    intentional = []
    copies = strings = 0
    for _, authored in insert.docs():
        doc = insert.laid_out(authored)
        for loc in doc['copies']:
            path, _, entry = loc.partition(':')
            if path not in cache:
                cache[path] = disc.file(path)
            data = cache[path]
            if entry:
                data = extract.blob(data, *pac.entries(data)[int(entry)])
            copies += 1
            for index, s in enumerate(doc['strings']):
                if 'same' in s:
                    s = doc['strings'][s['same']]
                if doc['kind'] == 'table':
                    off = u32(data, 4 * index)
                    if off < 4 * len(doc['strings']):
                        raise ValueError(f'{loc}: string points into pointer table')
                else:
                    targets = {pointer_target(data, p, int(doc['base'], 16)) for p in s['ptrs']}
                    if len(targets) != 1:
                        raise ValueError(f'{s["id"]}: pointers disagree')
                    off = targets.pop()
                actual = string_at(data, off)
                if 'data' in s:
                    if actual != extract.TBL.encode(s['jp'] + '{end}'):
                        raise ValueError('non-display tongue-twister board data changed')
                    intentional.append({'location': loc, 'offset': off, 'reason': s['data']})
                    continue
                codec = insert.EN1 if s['id'] in insert.SINGLE or doc['id'] == insert.WORD_MAZE else insert.EN
                expected = codec.encode(s['en'] + '{end}') if s.get('en') else extract.TBL.encode(s['jp'] + '{end}')
                if actual != expected:
                    raise ValueError(f'{loc} {s["id"]}: final disc differs from current release text')
                locations.append(f'{len(corpus):08x}\t{loc}@{off:x}\t{s["id"]}')
                corpus.extend(actual)
                strings += 1
    # Check the real EXE against the production transformation of the clean EXE.
    # The debug warp is a PCSX Lua hook; it is never linked into this executable.
    exe_doc = next(d for _, d in insert.docs() if d['id'] == 'SLPS_017')
    original_exe = (extract.TREE / insert.EXE).read_bytes()
    expected_exe = engine.patch_exe(insert.repacked(insert.laid_out(exe_doc), original_exe))
    actual_exe = disc.file(insert.EXE)
    if actual_exe != expected_exe:
        raise ValueError('release EXE contains unexpected/debug changes')
    intentional.append({'location': insert.EXE, 'reason': 'Optional Hiragana/Katakana player-name grids; Latin is the default. Production EXE verified byte-for-byte.'})
    # jp_left expects numeric table keys with --le16, whereas tbl.py uses byte strings.
    table = out / 'runtime.tbl'
    lines = [f'{int.from_bytes(k, "little"):04X}={v}' for k, v in insert.EN.dec.items()]
    table.write_text('\n'.join(lines) + '\n', encoding='utf-8', newline='\n')
    payload = out / 'reachable-text.bin'
    payload.write_bytes(corpus)
    (out / 'locations.tsv').write_text('\n'.join(locations) + '\n', encoding='utf-8', newline='\n')
    cmd = [sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts/jp_left.py'), str(payload),
           '--tbl', str(table), '--le16', '--min', '1', '--kanji-runs']
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
    (out / 'jp_left.txt').write_text(result.stdout + result.stderr, encoding='utf-8')
    print(result.stdout, end='')
    if result.returncode:
        raise ValueError('unintended Japanese in reachable release text; see jp_left.txt')
    report = {'image': str(image), 'sha1': hashlib.sha1(Path(image).read_bytes()).hexdigest(),
              'containers': copies, 'strings_including_copies': strings, 'bytes_scanned': len(corpus),
              'unintended_japanese': 0, 'debug_in_release': False, 'intentional_data': intentional,
              'scope': 'Every extracted text pointer in every copy, read from final ISO; graphic lettering is covered by visual QA gates.'}
    (out / 'scan.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(f'{copies} containers, {strings} reachable strings: clean; production EXE verified')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('image', type=Path)
    ap.add_argument('--out', type=Path, default=ROOT / 'work/qa/release/scan')
    args = ap.parse_args()
    scan(args.image, args.out)
