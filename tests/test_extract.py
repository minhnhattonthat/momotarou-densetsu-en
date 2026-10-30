"""Phase 4 extraction (tools/extract.py): script/ matches the disc, every table rebuilds byte-identical from its jp
text, every overlay string re-encodes to its bytes, and no text-like run on the disc is left out."""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import extract  # noqa: E402

needs_tree = pytest.mark.skipif(not (extract.TREE / "0/03FONT/FONT.PAC").is_file(),
                                reason="disc not unpacked (dumpsxiso, docs/re/archives.md)")

# Text-like runs (extract.text_runs) that are not strings, checked by eye: {location: [start offsets]}.
NOT_TEXT = {
    "SLPS_017.85": [0x6D982, 0x6DB56, 0xD39DA, 0xD4A80, 0xD579C],     # code/data words that happen to be glyph codes
    "0/06CITY/SMAP16.PAC:22": [0x150C, 0x40DA, 0x490A, 0x4CF0],      # map data (runs of one tile value)
    "0/07HMAP/HMAP20.PAC:15": [0x0],                                 # type 0x112 data
    "0/07HMAP/HMAP2606.PAC:65": [0x22F2, 0x237A],                    # card game's kana cell records
}


@pytest.fixture(scope="module")
def fresh():
    return extract.extract()


@needs_tree
def test_tables_and_overlay_strings_roundtrip(fresh):
    docs, located = fresh
    assert len(located) > 250
    for loc, (rel, b) in located.items():
        doc = docs[rel]
        if doc["kind"] == "table":
            assert extract.build_table(doc) == b, loc
            continue
        for s in doc["strings"]:
            enc = extract.TBL.encode(s["jp"] + "{end}")
            assert b[s["off"]:s["off"] + len(enc)] == enc, s["id"]
            assert len(enc) <= s["max"] and not any(b[s["off"] + len(enc):s["off"] + s["max"]]), s["id"]


@needs_tree
def test_script_matches_disc(fresh):
    docs, _ = fresh
    assert {p.relative_to(extract.SCRIPT).as_posix() for p in extract.SCRIPT.rglob("*.json")} == set(docs)

    def shape(d):
        return d["copies"], d.get("pad"), [(s["id"], s.get("jp"), s.get("same"), s.get("off")) for s in d["strings"]]
    for rel, doc in docs.items():
        assert shape(extract.load(extract.SCRIPT / rel)) == shape(doc), f"{rel} stale: rerun extract.py --force"


@needs_tree
def test_every_glyph_has_a_table_value(fresh):
    docs, _ = fresh
    for doc in docs.values():
        for s in doc["strings"]:
            assert not re.search(r"\[[0-9A-F]{2}\]", s.get("jp", "")), s["id"]


@needs_tree
def test_every_string_table_entry_is_extracted(fresh):
    _, located = fresh
    for loc, typ, b in extract.sources(want=lambda loc, typ: typ & 0xFFFF == 0x10D):
        assert loc in located or b == extract.EMPTY, loc


@needs_tree
def test_no_text_outside_script(fresh):
    """Coverage: every text-like run in every PAC entry, the EXE and the loose files is an extracted string or a
    listed non-text run."""
    docs, located = fresh
    tables, ends = set(), {}
    for loc, (rel, b) in located.items():
        if docs[rel]["kind"] == "table":
            tables.add(loc)
        else:   # a run covers a string when both end on the same terminator (runs can start before the string)
            ends[loc] = {s["off"] + len(extract.TBL.encode(s["jp"] + "{end}")) for s in docs[rel]["strings"]}
    blobs = ((loc, b) for loc, _, b in extract.sources(want=None))
    loose = [p for p in extract.TREE.rglob("*") if p.is_file() and p.suffix not in (".PAC", ".XA", ".DAT")]
    blobs = [*blobs, *((p.relative_to(extract.TREE).as_posix(), p.read_bytes()) for p in loose)]
    missed = []
    for loc, b in blobs:
        if loc in tables:
            continue
        for a, e in extract.text_runs(b[:len(b) & ~1]):
            if e not in ends.get(loc, ()) and a not in NOT_TEXT.get(loc, []):
                missed.append(f"{loc}@{a:#x}: {extract.TBL.decode(b, a, length=e - a)[0][:40]}")
    assert not missed, "\n".join(missed)
