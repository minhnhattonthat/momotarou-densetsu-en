"""RAM regions that stay zero in every given scene state (candidates for relocated text; docs/re/engine.md).

    python -X utf8 tools/debug/ramfree.py [--min 0x2000] SCENE..   # loads work/states/<scene>.sstate on the JP disc,
                                                                    # runs 60 frames, dumps RAM, intersects zero runs
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

ROM = ROOT / 'rom/Momotarou Densetsu (Japan).cue'


def dump(scene):
    out = ROOT / 'work/qa/ramfree' / scene
    subprocess.run([sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts/emu.py'), str(ROM), '--out', str(out),
                    '--state-in', str(ROOT / f'work/states/{scene}.sstate'), '--script',
                    str(ROOT / 'tools/debug/hits.lua'), '--var', 'HITS={}', '--var', 'DUMP_AT=60', '--frames', '70'],
                   capture_output=True, check=True)
    return (out / 'ram.bin').read_bytes()


def main(argv):
    lo = 0x2000
    if '--min' in argv:
        i = argv.index('--min'); lo = int(argv[i + 1], 0); del argv[i:i + 2]
    with ThreadPoolExecutor(4) as ex:
        dumps = list(ex.map(dump, argv))
    runs, start = [], None
    for o in range(0x10000, 0x200000 + 256, 256):
        zero = o < 0x200000 and not any(any(d[o:o + 256]) for d in dumps)
        if zero and start is None:
            start = o
        elif not zero and start is not None:
            if o - start >= lo:
                runs.append((0x80000000 + start, o - start))
            start = None
    for a, n in runs:
        print(f'{a:#010x} {n:#07x} ({n // 1024} KB)')


if __name__ == '__main__':
    main(sys.argv[1:])
