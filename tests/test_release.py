"""Release safeguards: real patch roundtrip, gate failures, and pointer semantics."""
import json
import re
import shutil
import struct
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import release
import release_scan


def test_scan_follows_relocated_pointers_and_u16_terminator():
    data = bytearray(64)
    struct.pack_into('<I', data, 0, 0x80168020)
    # LUI t0,0x8017; ADDIU t0,t0,-0x7fe0 -> 0x80168020.
    struct.pack_into('<II', data, 8, 0x3C088017, 0x25088020)
    data[32:38] = b'\x2a\x00\x2b\x00\x00\x80'
    assert release_scan.pointer_target(data, 'word@0', 0x80168000) == 32
    assert release_scan.pointer_target(data, 'lui@8', 0x80168000) == 32
    assert release_scan.string_at(data, 32) == data[32:38]
    struct.pack_into('<I', data, 0, 0x80169000)
    with pytest.raises(ValueError, match='outside'):
        release_scan.pointer_target(data, 'word@0', 0x80168000)


def test_polish_requires_resolutions(tmp_path):
    p = tmp_path / 'polish.md'
    p.write_text('# Nothing reviewed\n', encoding='utf-8')
    with pytest.raises(ValueError):
        release.polish_check(p)
    p.write_text('- [x] fixed\n- [ ] pending\n', encoding='utf-8')
    with pytest.raises(ValueError):
        release.polish_check(p)
    p.write_text('- [x] waived: concrete reason\n', encoding='utf-8')
    release.polish_check(p)


def test_tour_rejects_other_image_and_changed_shot(tmp_path, monkeypatch):
    monkeypatch.setattr(release, 'ROOT', tmp_path)
    shot = tmp_path / 'work/qa/warp_release/title/scene.png'
    shot.parent.mkdir(parents=True)
    shot.write_bytes(b'reviewed image')
    receipt = tmp_path / 'tour.json'
    receipt.write_text(json.dumps({'sha1': 'image-one', 'shots': {'title': release.digest(shot)}}))
    release.tour_check(receipt, 'image-one')
    with pytest.raises(ValueError, match='different image'):
        release.tour_check(receipt, 'image-two')
    shot.write_bytes(b'changed image')
    with pytest.raises(ValueError, match='changed or missing'):
        release.tour_check(receipt, 'image-one')


def test_real_xdelta_roundtrip_patch_only_zip_and_overwrite_guard(tmp_path, monkeypatch):
    xdelta = shutil.which('xdelta3') or shutil.which('xdelta3.exe')
    if not xdelta:
        pytest.skip('xdelta3 unavailable')
    original, built = tmp_path / 'original.bin', tmp_path / 'build/patched.bin'
    built.parent.mkdir()
    original.write_bytes(bytes(range(256)) * 256)
    built.write_bytes(b'English patch!' + original.read_bytes()[14:] + b'new pool')
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'docs/release-readme.txt').write_text('Version @VERSION@\nSHA-1 @PATCHED_SHA1@\n')
    monkeypatch.setattr(release, 'ROOT', tmp_path)
    monkeypatch.setattr(release, 'ORIGINAL', original)
    monkeypatch.setattr(release, 'IMAGE', built)
    archive = release.package('0.0', xdelta, False)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == {'Momotarou_Densetsu_EN_v0.0.xdelta', 'README.txt'}
        assert all(i.compress_type == zipfile.ZIP_STORED for i in z.infolist())
    assert (tmp_path / 'build/momotarou_reapplied.bin').read_bytes() == built.read_bytes()
    before = archive.read_bytes()
    with pytest.raises(ValueError, match='already exists'):
        release.package('0.0', xdelta, False)
    assert archive.read_bytes() == before


def test_word_maze_reveals_match_the_letters_players_enter():
    answers = json.loads((ROOT / 'script/07HMAP/HMAP2606_65.json').read_text(encoding='utf-8'))['strings']
    dialogue = json.loads((ROOT / 'script/07HMAP/HMAP2606_66.json').read_text(encoding='utf-8'))['strings']
    letters = lambda text: re.sub('[^A-Za-z]', '', text).upper()
    assert len(answers) == 41
    for i, answer in enumerate(answers):
        reveal = dialogue[45 + i]
        assert letters(answer['en']) == letters(reveal['en']), (answer['id'], reveal['id'])
        assert 1 <= len(letters(answer['en'])) <= 18, answer['id']


def test_museum_scrolls_recall_the_village_proverbs_verbatim():
    import insert
    rows = {s['id']: s for _, d in insert.docs() for s in d['strings'] if 'jp' in s}
    normalized = lambda text: re.sub(r'\{[^}]+\}|[\s「」！!？?…ー、。]', '', text)
    checked = 0
    for index in range(165, 215):
        scroll = rows[f'HMAP26_66:{index:03d}']
        matches = [s for key, s in rows.items() if not key.startswith('HMAP26_66:')
                   and normalized(s['jp']) == normalized(scroll['jp'])]
        if not matches:
            assert index == 209, 'new unmapped museum proverb'
            # This village message embeds the proverb between narration pages.
            source = rows['OMAP00_43:056']
            assert normalized(scroll['jp']) in normalized(source['jp'])
            assert scroll['en'] == source['en'].split('{wait}')[1] + '{wait}'
            checked += 1
        for source in matches:
            assert source['en'] == scroll['en'], (source['id'], scroll['id'])
            checked += 1
    assert checked >= 50
