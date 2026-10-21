import concurrent.futures
import json
from pathlib import Path
import tempfile
import unittest

from home_store import Catalog, HomeStore, Scope


class HomeStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.legacy = Path(self.temp.name) / 'home.json'
        self.scoped = Path(self.temp.name) / 'homes-scoped.json'
        self.store = HomeStore(self.legacy, self.scoped)
        self.scope = Scope('sculpt', 'level', 'SPStudyLevel')

    def legacy_record(self, value):
        self.legacy.write_text(json.dumps({'level': value}))
        return self.legacy.read_bytes()

    def test_unique_legacy_preserves_old_runtime_format(self):
        record = {'178881234567': 0.4, 'manual:Zoom': 0.6, 'sweet_home': True}
        original = self.legacy_record(record)
        result = self.store.lookup(self.scope, Catalog((self.scope,), complete=True))
        self.assertEqual((result.status, result.record), ('legacy_unique', record))
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertFalse(self.scoped.exists())

    def test_inactive_same_name_prevents_fallback(self):
        self.legacy_record({'sweet_home': True})
        other = Scope('feedback', 'level', 'SPChainLevel')
        catalog = Catalog((self.scope, other), complete=True)
        self.assertEqual(self.store.lookup(self.scope, catalog).status, 'legacy_ambiguous')
        self.assertIsNone(self.store.lookup(self.scope, catalog).record)

    def test_active_only_catalog_unverified(self):
        self.legacy_record({'sweet_home': True})
        self.assertEqual(self.store.lookup(self.scope, Catalog((self.scope,))).status, 'legacy_unverified')
        self.assertEqual(self.store.lookup(self.scope).status, 'legacy_unverified')

    def test_scope_must_be_in_catalog(self):
        self.legacy_record({})
        other = Scope('feedback', 'level', 'SPChainLevel')
        self.assertEqual(self.store.lookup(self.scope, Catalog((other,), True)).status, 'legacy_ambiguous')

    def test_new_layer_same_name_does_not_inherit_scoped_home(self):
        self.store.save(self.scope, {'sweet_home': True})
        other = Scope('feedback', 'level', 'SPChainLevel')
        self.assertEqual(self.store.lookup(other).status, 'missing')

    def test_slash_names_and_occurrences_are_unambiguous(self):
        scopes = [Scope('a/b', 'c', 'd'), Scope('a', 'b/c', 'd'),
                  Scope('a', 'b', 'c/d'), Scope('a/b', 'c', 'd', 2),
                  Scope('a/b', 'c', 'd', clip_occurrence=2)]
        self.assertEqual(len({s.key for s in scopes}), len(scopes))

    def test_concurrent_disjoint_writes_across_instances(self):
        def save(i):
            store = HomeStore(self.legacy, self.scoped)
            return store.save(Scope('figure', f'clip {i}', 'source'), {'value': i})
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
            self.assertTrue(all(r.status == 'saved' for r in pool.map(save, range(50))))
        self.assertEqual(len(json.loads(self.scoped.read_text())['entries']), 50)

    def test_seed_never_replaces_saved_home(self):
        self.store.save(self.scope, {'sweet_home': True, 'value': 1}, replace=True)
        result = self.store.seed(self.scope, {'sweet_home': False, 'value': 0})
        self.assertEqual(result.status, 'scoped')
        self.assertEqual(result.record['value'], 1)

    def test_seed_blocks_ambiguous_legacy_without_modifying_it(self):
        original = self.legacy_record({'sweet_home': True})
        catalog = Catalog((self.scope, Scope('feedback', 'level', 'SPChainLevel')), True)
        self.assertEqual(self.store.seed(self.scope, {'sweet_home': False}, catalog).status, 'legacy_ambiguous')
        self.assertEqual(self.legacy.read_bytes(), original)
        self.assertFalse(self.scoped.exists())

    def test_explicit_save_preserves_legacy_and_requires_replace(self):
        original = self.legacy_record({'old': True})
        self.store.save(self.scope, {'value': 1})
        self.assertEqual(self.store.save(self.scope, {'value': 2}).status, 'exists')
        self.assertEqual(self.store.lookup(self.scope).record, {'value': 1})
        self.store.save(self.scope, {'value': 2}, replace=True)
        self.assertEqual(self.store.lookup(self.scope).record, {'value': 2})
        self.assertEqual(self.legacy.read_bytes(), original)

    def test_corrupt_scoped_file_cannot_be_overwritten(self):
        self.scoped.write_text('{bad json')
        with self.assertRaises(ValueError):
            self.store.save(self.scope, {}, replace=True)
        self.assertEqual(self.scoped.read_text(), '{bad json')

    def test_future_format_preserved(self):
        self.scoped.write_text('{"version": 5, "entries": {}}')
        with self.assertRaises(ValueError):
            self.store.seed(self.scope, {})
        self.assertEqual(json.loads(self.scoped.read_text())['version'], 5)

    def test_legacy_and_scoped_paths_must_differ(self):
        with self.assertRaises(ValueError):
            HomeStore(self.legacy, self.legacy)


if __name__ == '__main__':
    unittest.main()
