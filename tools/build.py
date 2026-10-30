"""Build the disc: unpacked tree + replaced files -> build/momotarou_en.bin/.cue (docs/re/archives.md).

    python -X utf8 tools/build.py [--marker]    # -> build/momotarou_en.bin (en, else Japanese) or momotarou_marker.bin
    python -X utf8 tools/build.py --marker --qa "SHOP:347=text"..   # stress/torture lines (also -> momotarou_marker)

The game reads files by MMPS_CD.SFS (800 x {u32 LBA, u32 size}), not ISO9660, so every build regenerates it from
mkpsxiso's LBA log: lay out once with -noisogen (the SFS keeps its 6400 bytes, so LBAs don't depend on it), write
the new table, then build the image. With no replaced files the output is byte-identical to the dump (tests).
"""
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import check_rom  # noqa: E402

CUE = ROOT / 'rom/Momotarou Densetsu (Japan).cue'
DISC = ROOT / 'work/disc'                      # tree/ + layout.xml from dumpsxiso (never edited)
OUT = ROOT / 'build'
MKPSXISO = ROOT / 'tools/mkpsxiso/mkpsxiso.exe'
DUMPSXISO = ROOT / 'tools/mkpsxiso/dumpsxiso.exe'
SFS = 'MMPS_CD.SFS'


def unpack():
    if not (DISC / 'layout.xml').is_file():
        subprocess.run([DUMPSXISO, '-x', DISC / 'tree', '-s', DISC / 'layout.xml', CUE], check=True)


def lba_log(layout, work):
    """{disc path 'A/B.PAC': (lba, bytes)} as mkpsxiso would lay out `layout` (no image written)."""
    log = work / 'lba.txt'
    subprocess.run([MKPSXISO, '-q', '-noisogen', '-lba', log, layout], check=True, cwd=layout.parent,
                   stdout=subprocess.DEVNULL)
    out, dirs = {}, []
    for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
        f = [x.strip() for x in line.split('|')]
        if len(f) < 7:
            continue
        if f[0] == 'Dir':
            dirs.append(f[1])
        elif f[0] == 'End':
            dirs.pop()
        elif f[0] in ('File', 'XA', 'STR', 'DA'):
            out['/'.join(dirs + [f[1]])] = (int(f[3]), int(f[5]))
    return out


def rebuild_sfs(sfs, old, new):
    """Point each SFS entry at its file's new LBA/size. Entries are matched to files by their original LBA; the
    size keeps its original offset from the file length (MECD.PAC's entry is 9 bytes short of the file)."""
    by_lba = {lba: path for path, (lba, _) in old.items()}
    out = bytearray(sfs)
    for i in range(len(sfs) // 8):
        lba, size = struct.unpack_from('<II', sfs, i * 8)
        if lba == size == 0:
            continue
        path = by_lba[lba]
        nlba, nlen = new[path]
        struct.pack_into('<II', out, i * 8, nlba, size + nlen - old[path][1])
    return bytes(out)


def write_layout(dst, files):
    """Copy of the dumped layout with absolute sources; files {disc path: local file} replace the tree's copy."""
    tree = ET.parse(DISC / 'layout.xml')
    root = tree.getroot()
    lic = root.find('.//license')
    lic.set('file', str((DISC / lic.get('file')).resolve()))
    dt = root.find('.//directory_tree')
    dt.set('source', str((DISC / dt.get('source')).resolve()))

    seen = set()

    def walk(el, prefix):
        for c in el:
            path = prefix + (c.get('name') or '')
            if c.tag == 'dir':
                walk(c, path + '/')
            elif c.tag == 'file' and path in files:
                c.set('source', str(Path(files[path]).resolve()))
                seen.add(path)
    walk(dt, '')
    if set(files) - seen:
        sys.exit(f'build: no such disc file {sorted(set(files) - seen)}')
    tree.write(dst, encoding='utf-8', xml_declaration=True)


def build(replaced, out_bin):
    """replaced: {disc path: bytes}. Writes out_bin and its .cue."""
    work = out_bin.parent / 'files'
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    files = {}
    for path, data in replaced.items():
        files[path] = work / path
        files[path].parent.mkdir(parents=True, exist_ok=True)
        files[path].write_bytes(data)
    layout = out_bin.parent / 'layout.xml'
    files[SFS] = work / SFS
    files[SFS].write_bytes((DISC / 'tree' / SFS).read_bytes())
    write_layout(layout, files)
    new = lba_log(layout, work)
    old = lba_log(DISC / 'layout.xml', work)
    files[SFS].write_bytes(rebuild_sfs((DISC / 'tree' / SFS).read_bytes(), old, new))
    subprocess.run([MKPSXISO, '-y', '-q', '-o', out_bin, '-c', out_bin.with_suffix('.cue'), layout], check=True,
                   cwd=layout.parent, stdout=subprocess.DEVNULL)


def main(argv):
    check_rom.check()
    unpack()
    import insert
    marker = '--marker' in argv
    qa = dict(argv[i + 1].split('=', 1) for i, a in enumerate(argv) if a == '--qa')
    OUT.mkdir(exist_ok=True)
    out_bin = OUT / ('momotarou_marker.bin' if marker or qa else 'momotarou_en.bin')
    build(insert.files(marker, qa), out_bin)
    print(f'built {out_bin} ({out_bin.stat().st_size} bytes)')


if __name__ == '__main__':
    main(sys.argv[1:])
