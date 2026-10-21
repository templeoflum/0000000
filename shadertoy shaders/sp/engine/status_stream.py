"""Compact surface updates; every new connection receives a complete keyframe."""
import json

class StatusStream:
    def __init__(self):
        self.previous = {}
        self.sequence = 0

    def encode(self, state):
        changed = {}
        rows = {}
        current = {}
        for key, value in state.items():
            if key in ('layers', 'fx', 'clips') and isinstance(value, list):
                encoded = tuple(json.dumps(row, separators=(',', ':')) for row in value)
                prior = self.previous.get(key)
                current[key] = encoded
                if not isinstance(prior, tuple) or len(prior) != len(encoded):
                    changed[key] = value
                else:
                    edits = {str(i): value[i] for i, row in enumerate(encoded) if row != prior[i]}
                    if edits: rows[key] = edits
            else:
                encoded = json.dumps(value, separators=(',', ':'))
                current[key] = encoded
                if self.previous.get(key) != encoded: changed[key] = value
        self.previous = current
        self.sequence += 1
        return json.dumps({'_delta': True, 'sequence': self.sequence, 'set': changed, 'rows': rows}, separators=(',', ':'))
