"""Warp to scenes from a cold boot (tools/debug/warp.lua + scenes.lua) and keep their savestates.

    python -X utf8 tools/debug/warp.py village ev_card     # -> work/qa/warp/<scene>/scene.png, work/states/<scene>.sstate
    python -X utf8 tools/debug/warp.py --all [--jobs 3]    # regenerate every state (after code/font/graphics edits)
    python -X utf8 tools/debug/warp.py --list
    python -X utf8 tools/debug/warp.py map:292:18:13       # any map id (tools/debug/maps.txt) at tile x,y
    python -X utf8 tools/debug/warp.py ROM.cue village     # another build (default: build/momotarou_en.cue, else rom/)
Extra emu.py args after "--", e.g. -- --var GOD=1 --shot-every 60. Exit 1 if any scene was not reached.
"""
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL  # noqa: E402

SCENES = ROOT / 'tools/debug/scenes.lua'


def scene_names():
    return re.findall(r'^\s+(\w+)\s*=\s*\{', SCENES.read_text(encoding='utf-8'), re.M)


def run(rom, scene, extra):
    safe = scene.replace(':', '_')
    out = ROOT / 'work/qa/warp' / safe
    state = ROOT / 'work/states' / f'{safe}.sstate'
    state.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, '-X', 'utf8', str(Path(SKILL) / 'scripts/emu.py'), str(rom), '--out', str(out),
           '--script', str(ROOT / 'tools/debug/warp.lua'), '--var', f"SCENE='{scene}'",
           '--var', f"SCENES=[[{SCENES.as_posix()}]]", '--var', f"STATE_SAVE=[[{state.as_posix()}]]",
           '--frames', '30000', '--timeout', '900', *extra]  # runs stop on arrival; 30000 = the epilogue's need
    r = subprocess.run(cmd, capture_output=True, text=True)
    ok = r.returncode == 0 and (out / 'scene.png').exists()
    msg = (out / 'lua_error.txt').read_text(errors='replace').strip() if (out / 'lua_error.txt').exists() else ''
    print(f"{'ok  ' if ok else 'FAIL'} {scene:16} {out / 'scene.png' if ok else msg or r.stdout[-300:]}", flush=True)
    return ok


def main(argv):
    extra = argv[argv.index('--') + 1:] if '--' in argv else []
    argv = argv[:argv.index('--')] if '--' in argv else argv
    jobs = 1
    if '--jobs' in argv:
        i = argv.index('--jobs'); jobs = int(argv[i + 1]); del argv[i:i + 2]
    if '--list' in argv:
        print('\n'.join(scene_names())); return 0
    rom = next((a for a in argv if a.endswith('.cue')), None)
    if rom is None:
        built = ROOT / 'build/momotarou_en.cue'
        rom = built if built.exists() else ROOT / 'rom/Momotarou Densetsu (Japan).cue'
    names = scene_names() if '--all' in argv else [a for a in argv if not a.endswith('.cue')]
    unknown = {n for n in names if not n.startswith('map:')} - set(scene_names())
    if unknown or not names:
        print(__doc__, 'unknown scenes:', sorted(unknown)); return 2
    with ThreadPoolExecutor(jobs) as ex:
        results = list(ex.map(lambda s: run(rom, s, extra), names))
    return 0 if all(results) else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
