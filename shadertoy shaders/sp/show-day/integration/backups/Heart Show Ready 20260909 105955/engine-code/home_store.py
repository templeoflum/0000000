"""Offline-ready scoped Home storage; not integrated with the running engine.

Legacy file remains read-only. Caller must build Catalog from every populated clip
in a complete composition snapshot, including inactive and unsupported clips.
"""
from contextlib import contextmanager
from dataclasses import dataclass
import copy
import fcntl
import json
import os
from pathlib import Path
import tempfile
import threading


@dataclass(frozen=True)
class Scope:
    role: str
    name: str
    source: str
    layer_occurrence: int = 1
    clip_occurrence: int = 1

    def __post_init__(self):
        if not all(isinstance(v, str) and v for v in (self.role, self.name, self.source)):
            raise ValueError('Home identity requires role, name and source identity')
        if any(type(v) is not int or v < 1 for v in (self.layer_occurrence, self.clip_occurrence)):
            raise ValueError('Occurrences must be positive integers')

    @property
    def key(self):
        # JSON tuple framing prevents collisions from slash-containing names.
        return json.dumps([self.role, self.layer_occurrence, self.name, self.source,
                           self.clip_occurrence], ensure_ascii=False, separators=(',', ':'))


@dataclass(frozen=True)
class Catalog:
    scopes: tuple
    complete: bool = False

    def unique_legacy_name(self, scope):
        return (self.complete and sum(s == scope for s in self.scopes) == 1
                and sum(s.name == scope.name for s in self.scopes) == 1)


@dataclass(frozen=True)
class Result:
    status: str
    record: dict | None = None


_LOCKS = {}
_LOCKS_GUARD = threading.Lock()


class HomeStore:
    def __init__(self, legacy_path, scoped_path):
        self.legacy_path = Path(legacy_path).resolve()
        self.scoped_path = Path(scoped_path).resolve()
        if self.legacy_path == self.scoped_path:
            raise ValueError('Scoped Homes require a separate file; legacy is read-only')
        self.lock_path = self.scoped_path.with_name(self.scoped_path.name + '.lock')
        with _LOCKS_GUARD:
            self._lock = _LOCKS.setdefault(str(self.lock_path), threading.RLock())

    @contextmanager
    def _locked(self):
        with self._lock:
            with self.lock_path.open('a') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(lock, fcntl.LOCK_UN)

    @staticmethod
    def _read(path, default):
        try:
            with path.open() as stream:
                value = json.load(stream)
        except FileNotFoundError:
            return copy.deepcopy(default)
        if not isinstance(value, dict):
            raise ValueError(f'Invalid Home object: {path}')
        return value

    def _load(self):
        data = self._read(self.scoped_path, {'version': 1, 'entries': {}})
        if data.get('version') != 1 or not isinstance(data.get('entries'), dict):
            raise ValueError('Unsupported scoped Home format; refusing to overwrite')
        return data

    def _lookup(self, scope, catalog, data):
        if scope.key in data['entries']:
            record = data['entries'][scope.key]
            if not isinstance(record, dict):
                raise ValueError('Invalid scoped Home record')
            return Result('scoped', copy.deepcopy(record))
        legacy = self._read(self.legacy_path, {})
        if scope.name not in legacy:
            return Result('missing')
        # Ambiguous/unknown records remain in legacy storage, never silently bound.
        if not catalog or not catalog.complete:
            return Result('legacy_unverified')
        if not catalog.unique_legacy_name(scope):
            return Result('legacy_ambiguous')
        if not isinstance(legacy[scope.name], dict):
            return Result('legacy_invalid')
        return Result('legacy_unique', copy.deepcopy(legacy[scope.name]))

    def lookup(self, scope, catalog=None):
        with self._locked():
            return self._lookup(scope, catalog, self._load())

    def _write(self, data):
        serialized = json.dumps(data, ensure_ascii=False, indent=1, allow_nan=False) + '\n'
        fd, name = tempfile.mkstemp(prefix=self.scoped_path.name + '.', suffix='.tmp',
                                    dir=self.scoped_path.parent)
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(serialized)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.scoped_path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def save(self, scope, record, *, replace=False):
        """Explicit user save. Default is create-only; old legacy data is retained."""
        if not isinstance(record, dict):
            raise ValueError('Home must be an object')
        with self._locked():
            data = self._load()
            if scope.key in data['entries'] and not replace:
                return Result('exists', copy.deepcopy(data['entries'][scope.key]))
            data['entries'][scope.key] = copy.deepcopy(record)
            self._write(data)
            return Result('saved', copy.deepcopy(record))

    def seed(self, scope, record, catalog=None):
        """Auto-capture only if neither scoped nor any same-name legacy Home exists.

        Lookup and create share the lock, so a late discovery task cannot replace
        an explicit user save. Ambiguous legacy records block auto-capture too.
        """
        if not isinstance(record, dict):
            raise ValueError('Home must be an object')
        with self._locked():
            data = self._load()
            existing = self._lookup(scope, catalog, data)
            if existing.status != 'missing':
                return existing
            data['entries'][scope.key] = copy.deepcopy(record)
            self._write(data)
            return Result('seeded', copy.deepcopy(record))
