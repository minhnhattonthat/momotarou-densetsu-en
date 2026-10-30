"""Write provenance in immutable logical file / decompressed PAC-entry coordinates.

Repacking a table is one atomic replacement; overlays and executable patches record
individual spans. Container offsets are validated separately after compression.
"""
import json
from pathlib import Path


class Buffer:
    def __init__(self, original, location):
        self.original = bytes(original)
        self.data = bytearray(original)
        self.location = location
        self.writes = []

    def put(self, offset, data, owner, expected=None, *, replace=False, append=False):
        data = bytes(data)
        assert owner and offset >= 0, (self.location, owner, offset)
        assert not (replace and append), (self.location, owner, 'conflicting write modes')
        end = offset if append else len(self.original) if replace else offset + len(data)
        assert (append and offset == len(self.data) and offset >= len(self.original)) or \
            (replace and offset == 0) or (not append and end <= len(self.original)), \
            (self.location, owner, 'out of bounds')
        old = self.original[offset:end]
        assert expected is None or bytes(expected) == old, (self.location, owner, 'wrong expected original')
        stop = offset + len(data) if append else max(end, len(data)) if replace else end
        for w in self.writes:
            assert not (offset < w['stop'] and w['offset'] < stop), (
                self.location, owner, 'overlap', w['owner'])
        self.writes.append(dict(offset=offset, stop=stop, old=old.hex(), new=data.hex(), owner=owner,
                                replace=replace))
        self.data[offset:end] = data

    def verify(self, final):
        expected = bytearray(self.original)
        for w in self.writes:
            off = w['offset']
            old, new = bytes.fromhex(w['old']), bytes.fromhex(w['new'])
            assert self.original[off:off + len(old)] == old, (self.location, w['owner'], 'wrong original')
            expected[off:off + len(old)] = new
            assert final[off:off + len(new)] == new, (self.location, w['owner'], 'overwritten write')
        assert bytes(expected) == bytes(final), (self.location, 'unlogged mutation')


class Audit:
    def __init__(self):
        self.buffers = {}

    def buffer(self, location, original):
        if location not in self.buffers:
            self.buffers[location] = Buffer(original, location)
        assert self.buffers[location].original == bytes(original), (location, 'original changed')
        return self.buffers[location]

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8', newline='\n') as f:
            for loc, buf in self.buffers.items():
                for w in buf.writes:
                    f.write(json.dumps(dict(location=loc, **w)) + '\n')
