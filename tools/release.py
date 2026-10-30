"""Build and verify a local patch-only release; never publish it.

First run --prepare to generate final-build tour evidence, have read-only
reviewers supply verdicts, then run --skip-tour to package that identical build.
No QA gate is bypassed by --skip-tour: its receipt must match the image hash.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from skill import SKILL
import release_scan
import story

PYTHON = [sys.executable, '-X', 'utf8']
QA = ROOT / 'work/qa/release'
IMAGE = ROOT / 'build/momotarou_en.bin'
CUE = IMAGE.with_suffix('.cue')
ORIGINAL = ROOT / 'rom/Momotarou Densetsu (Japan).bin'


def run(*args):
    subprocess.run([str(a) for a in args], cwd=ROOT, check=True)


def py(script, *args):
    run(*PYTHON, script, *args)


def digest(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha1').hexdigest()


def hashes(path):
    data = Path(path).read_bytes()
    return {'size': len(data), 'crc32': f'{zlib.crc32(data):08X}',
            'md5': hashlib.md5(data).hexdigest(), 'sha1': hashlib.sha1(data).hexdigest()}


def polish_check(path):
    text = Path(path).read_text(encoding='utf-8')
    if re.search(r'^\s*[-*]\s+\[\s\]', text, re.M) or not re.search(r'^\s*- \[x\]', text, re.M):
        raise ValueError('docs/polish.md is empty or has unresolved checklist entries')


def tour_check(receipt, sha1):
    if not receipt.is_file():
        raise ValueError('no final-build tour receipt; run --prepare')
    data = json.loads(receipt.read_text(encoding='utf-8'))
    if data['sha1'] != sha1:
        raise ValueError('tour belongs to a different image; run --prepare again')
    for scene, expected in data['shots'].items():
        shot = ROOT / 'work/qa/warp_release' / scene / 'scene.png'
        if not shot.is_file() or digest(shot) != expected:
            raise ValueError(f'tour shot changed or missing: {scene}')


def capture_tour(sha1, jobs):
    py(ROOT / 'tools/debug/warp.py', CUE, '--all', '--tag', 'release', '--jobs', jobs)
    sys.path.insert(0, str(ROOT / 'tools/debug'))
    import warp
    sheets = QA / 'sheets'
    sheets.mkdir(parents=True, exist_ok=True)
    shots = {}
    for scene in warp.scene_names():
        shot = ROOT / 'work/qa/warp_release' / scene / 'scene.png'
        shots[scene] = digest(shot)
        args = [shot, '--zoom', '2', '--out', sheets / f'{scene}_sheet.png']
        py(Path(SKILL) / 'scripts/sheet.py', *args)
    if digest(IMAGE) != sha1:
        raise ValueError('image changed during tour')
    (QA / 'tour.json').write_text(json.dumps({'sha1': sha1, 'shots': shots}, indent=2) + '\n', encoding='utf-8')
    py(Path(SKILL) / 'scripts/qa_gate.py', 'init', QA / 'manifest.tsv', sheets)


def gates():
    config = json.loads((ROOT / 'docs/release-gates.json').read_text(encoding='utf-8'))
    for manifest, verdicts in [*config['visual'], config['story']]:
        py(Path(SKILL) / 'scripts/qa_gate.py', 'check', ROOT / manifest, ROOT / verdicts)
    polish_check(ROOT / 'docs/polish.md')


def package(version, xdelta, force):
    folder = ROOT / 'release' / f'v{version}'
    stem = f'Momotarou_Densetsu_EN_v{version}'
    targets = [folder / f'{stem}.xdelta', folder / 'README.txt', folder / f'{stem}.zip', folder / 'verification.json']
    if not force and any(p.exists() for p in targets):
        raise ValueError(f'{folder}: version already exists; use --force to replace it')
    folder.mkdir(parents=True, exist_ok=True)
    patch, readme, archive, proof = targets
    # Remove a previous success record before replacing any component.
    proof.unlink(missing_ok=True)
    run(xdelta, '-f', '-e', '-s', ORIGINAL, IMAGE, patch)
    verified = ROOT / 'build/momotarou_reapplied.bin'
    run(xdelta, '-f', '-d', '-s', ORIGINAL, patch, verified)
    wanted, got = hashes(IMAGE), hashes(verified)
    if got != wanted:
        raise ValueError('re-applied patch differs from the built image')
    base = hashes(ORIGINAL)
    template = (ROOT / 'docs/release-readme.txt').read_text(encoding='utf-8')
    values = {'VERSION': version, 'PATCH': patch.name, **{f'BASE_{k.upper()}': str(v) for k, v in base.items()},
              **{f'PATCHED_{k.upper()}': str(v) for k, v in wanted.items()}}
    for key, value in values.items():
        template = template.replace('@' + key + '@', value)
    if re.search(r'@[A-Z_]+@', template):
        raise ValueError('unresolved README placeholder')
    readme.write_text(template, encoding='utf-8', newline='\n')
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_STORED) as z:
        z.write(patch, patch.name)
        z.write(readme, readme.name)
    with zipfile.ZipFile(archive) as z:
        if set(z.namelist()) != {patch.name, readme.name} or z.testzip() is not None:
            raise ValueError('invalid patch-only ZIP')
    result = {'version': version, 'base': base, 'patched': wanted, 'patch_sha1': digest(patch),
              'zip_sha1': digest(archive), 'reapplied_identical': True, 'zip_members': [patch.name, readme.name],
              'published': False}
    proof.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(f'Verified local release: {archive}\nPatched SHA-1: {wanted["sha1"]}')
    return archive


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--version', default='1.0')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--prepare', action='store_true', help='build QA evidence for review, do not package')
    ap.add_argument('--skip-tour', action='store_true', help='reuse verified tour for the identical image')
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--xdelta', default=shutil.which('xdelta3') or shutil.which('xdelta3.exe'))
    args = ap.parse_args(argv)
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', args.version):
        ap.error('version must be numeric X.Y or X.Y.Z')
    if not args.prepare and not args.xdelta:
        ap.error('xdelta3 not on PATH; pass --xdelta path/to/xdelta3')
    folder = ROOT / 'release' / f'v{args.version}'
    if not args.prepare and folder.exists() and any(folder.iterdir()) and not args.force:
        ap.error('version directory already contains files; use --force')
    QA.mkdir(parents=True, exist_ok=True)
    py(ROOT / 'tools/build.py')
    py(ROOT / 'tools/check.py')
    py(Path(SKILL) / 'scripts/emu.py', CUE, '--out', QA / 'smoke', '--route', ROOT / 'tools/routes/boot.txt', '--smoke')
    release_scan.scan(IMAGE, QA / 'scan')
    sha1 = digest(IMAGE)
    story.generate(ROOT / 'work/qa/story/chapters')
    py(Path(SKILL) / 'scripts/qa_gate.py', 'init', ROOT / 'work/qa/story/manifest.tsv',
       ROOT / 'work/qa/story/chapters', '--glob', '*.txt')
    if args.skip_tour:
        tour_check(QA / 'tour.json', sha1)
    else:
        capture_tour(sha1, args.jobs)
    if args.prepare:
        print('Evidence ready for read-only review. No release packaged.')
        return
    gates()
    if digest(IMAGE) != sha1:
        raise ValueError('image changed during release checks')
    package(args.version, args.xdelta, args.force)


if __name__ == '__main__':
    main()
