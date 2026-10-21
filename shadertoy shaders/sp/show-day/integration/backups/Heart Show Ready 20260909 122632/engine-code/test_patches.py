import copy
import threading
import unittest
from pathlib import Path
from patches import open_verified, composition_signature, Cancelled


class OpenVerificationTests(unittest.TestCase):
    def setUp(self):
        self.comp = {'name': {'value': 'Start'}, 'video': {
            'width': {'value': 1920}, 'height': {'value': 1080}}, 'layers': []}
        self.path = Path('/tmp/Start.avc')
        self.signature = composition_signature(self.comp)

    def test_pending_http_can_complete_from_confirmed_readback(self):
        release = threading.Event()
        try:
            before=copy.deepcopy(self.comp);before['name']['value']='Previous'
            reads=iter([before])
            result = open_verified(lambda *args: release.wait(2), lambda: next(reads,self.comp),
                                   self.path, self.signature, lambda: None, timeout=1)
            self.assertEqual(result, self.comp)
        finally:
            release.set()

    def test_ack_does_not_accept_wrong_composition(self):
        wrong = copy.deepcopy(self.comp)
        wrong['name']['value'] = 'Other'
        with self.assertRaises(TimeoutError):
            open_verified(lambda *args: None, lambda: wrong, self.path,
                          self.signature, lambda: None, timeout=.2)

    def test_same_name_with_wrong_layout_is_rejected(self):
        wrong = copy.deepcopy(self.comp)
        wrong['video']['width']['value'] = 1280
        with self.assertRaises(TimeoutError):
            open_verified(lambda *args: None, lambda: wrong, self.path,
                          self.signature, lambda: None, timeout=.2)

    def test_cancellation_stops_readback(self):
        calls = []
        def cancelled():
            raise Cancelled()
        with self.assertRaises(Cancelled):
            open_verified(lambda *args: calls.append(args), lambda: self.comp, self.path,
                          self.signature, cancelled)
        self.assertEqual(calls, [])

class ProgressTests(unittest.TestCase):
    def test_cancelled_operation_cannot_overwrite_progress(self):
        from patches import Operations
        o=Operations();o.number=1
        try:
            o.progress(1,'Opening fixture')
            self.assertEqual(o.snapshot()['stage'],'Opening fixture')
            o.cancel()
            with self.assertRaises(Cancelled):o.progress(1,'Complete')
            self.assertNotEqual(o.snapshot()['stage'],'Complete')
        finally:o.pool.shutdown()

class RecallCompletionAuditTests(unittest.TestCase):
    """Offline completion regressions; no Arena or filesystem mutation."""
    def setUp(self):
        self.path = Path('/tmp/Start.avc')
        self.comp = {'name': {'id': 10, 'value': 'Start'}, 'video': {
            'width': {'id': 11, 'value': 1920},
            'height': {'id': 12, 'value': 1080}}, 'layers': []}
        self.signature = composition_signature(self.comp)

    def pending_post(self):
        release = threading.Event()
        self.addCleanup(release.set)
        return lambda *args: release.wait(3)

    def test_pending_open_cannot_accept_already_open_same_snapshot(self):
        with self.assertRaises(TimeoutError):
            open_verified(self.pending_post(), lambda: self.comp, self.path,
                          self.signature, lambda: None, timeout=.65)

    def test_pending_open_accepts_new_root_ids_for_same_snapshot(self):
        opened = copy.deepcopy(self.comp)
        opened['name']['id'] = 20
        reads = iter([self.comp])
        result = open_verified(self.pending_post(), lambda: next(reads, opened),
                               self.path, self.signature, lambda: None, timeout=1)
        self.assertEqual(result['name']['id'], 20)

    def test_pending_open_accepts_observed_snapshot_transition(self):
        before = copy.deepcopy(self.comp)
        before['name']['value'] = 'Other'
        reads = iter([before])
        result = open_verified(self.pending_post(), lambda: next(reads, self.comp),
                               self.path, self.signature, lambda: None, timeout=1)
        self.assertEqual(result, self.comp)

    def test_acknowledged_same_snapshot_needs_no_generation_change(self):
        result = open_verified(lambda *args: None, lambda: self.comp, self.path,
                               self.signature, lambda: None, timeout=.5)
        self.assertEqual(result, self.comp)

    def test_cancel_after_request_stops_polling_not_the_inflight_post(self):
        issued, release, completed = threading.Event(), threading.Event(), threading.Event()
        self.addCleanup(release.set)
        def post(*args):
            issued.set()
            release.wait(2)
            completed.set()
        def check():
            if issued.is_set():
                raise Cancelled()
        with self.assertRaises(Cancelled):
            open_verified(post, lambda: self.comp, self.path, self.signature, check)
        self.assertTrue(issued.is_set())
        self.assertFalse(completed.is_set())
        release.set()
        self.assertTrue(completed.wait(1))


class QueuedOperationAuditTests(unittest.TestCase):
    def setUp(self):
        from patches import Operations
        self.ops = Operations()
        self.addCleanup(self.ops.pool.shutdown)

    def test_busy_covers_queued_request_before_worker_starts(self):
        occupied, release = threading.Event(), threading.Event()
        self.addCleanup(release.set)
        def blocker():
            occupied.set(); release.wait(2)
        self.ops.pool.submit(blocker)
        self.assertTrue(occupied.wait(1))
        writes = []
        future = self.ops.submit(lambda token: self.ops.write(token, writes.append, 'stale'))
        self.assertFalse(self.ops.active)
        self.assertTrue(self.ops.busy)
        self.assertTrue(self.ops.snapshot()['active'])
        self.ops.cancel()
        release.set(); future.result(2)
        self.assertEqual(writes, [])
        self.assertFalse(self.ops.busy)

    def test_old_failure_does_not_clear_new_pending_work(self):
        started, release, latest_started, latest_release = [threading.Event() for _ in range(4)]
        self.addCleanup(release.set); self.addCleanup(latest_release.set)
        def first(token):
            started.set(); release.wait(2); raise RuntimeError('old failure')
        old = self.ops.submit(first)
        self.assertTrue(started.wait(1))
        def second(token):
            latest_started.set(); latest_release.wait(2)
            self.ops.progress(token, 'Newest applied')
        new = self.ops.submit(second)
        release.set(); old.result(2)
        self.assertTrue(latest_started.wait(1))
        self.assertTrue(self.ops.busy)
        self.assertNotIn('old failure', self.ops.status)
        latest_release.set(); new.result(2)
        self.assertFalse(self.ops.busy)
        self.assertEqual(self.ops.status, 'Ready')

    def test_status_snapshot_does_not_wait_for_blocking_renderer_write(self):
        started, release, published = [threading.Event() for _ in range(3)]
        self.addCleanup(release.set)
        def write():
            started.set(); release.wait(2)
        future=self.ops.submit(lambda token:self.ops.write(token,write))
        self.assertTrue(started.wait(1))
        samples=[]
        reader=threading.Thread(target=lambda:(samples.append(self.ops.snapshot()),published.set()))
        reader.start()
        self.assertTrue(published.wait(.2), 'status polling blocked on a renderer request')
        self.assertTrue(samples[0]['active'])
        self.assertTrue(self.ops.busy)
        release.set();reader.join();future.result(2)

    def test_cancel_waits_for_inflight_write_lock(self):
        # Documents the remaining cancellation latency boundary: the current blocking
        # write must finish; cancellation only fences writes that have not begun.
        started, release, cancelled = [threading.Event() for _ in range(3)]
        self.addCleanup(release.set)
        def blocking_write():
            started.set(); release.wait(2)
        future = self.ops.submit(lambda token: self.ops.write(token, blocking_write))
        self.assertTrue(started.wait(1))
        cancel_thread = threading.Thread(target=lambda: (self.ops.cancel(), cancelled.set()))
        cancel_thread.start()
        self.assertFalse(cancelled.wait(.05))
        release.set(); self.assertTrue(cancelled.wait(1))
        cancel_thread.join(); future.result(2)

class RecallRecoveryAuditTests(unittest.TestCase):
    """Exercise the real recall coordinator with isolated files and a fake renderer."""
    def setUp(self):
        import json
        import tempfile
        import heart
        from types import SimpleNamespace
        from unittest.mock import patch
        from patches import Operations
        self.heart=heart
        directory=tempfile.TemporaryDirectory();self.addCleanup(directory.cleanup)
        self.root=Path(directory.name)
        self.comp={'name':{'value':'Before'},'video':{
            'width':{'id':1,'value':1920},'height':{'id':2,'value':1080}},'layers':[]}
        self.data={'version':1,'signature':composition_signature(self.comp),'layers':{},
                   'instruments':{'feedback/map':{'marker':'after'}},'bars':4,'hold':False}
        (self.root/'Fixture.avc').write_text('<Composition currentDeckIndex="0"/>')
        (self.root/'Fixture.json').write_text(json.dumps(self.data))
        self.ops=Operations();self.ops.number=1;self.addCleanup(self.ops.pool.shutdown)
        self.state={'bars':8,'hold':True,'arena_connected':True,'events':[]}
        values={
            'PATCH_ROOT':str(self.root),'PATCH_OPS':self.ops,'STATE':self.state,
            'CLIPS':{(0,0):SimpleNamespace(layer=0,name='map',taken=True)},
            'LAYERS':[{'i':1,'name':'feedback'}],
        }
        for name,value in values.items():
            p=patch.object(heart,name,value);p.start();self.addCleanup(p.stop)
        for name in ('arena_post','put_http','clear_layer','connect_clip','event','capture_native_snapshot','require_dependencies'):
            p=patch.object(heart,name);mock=p.start();setattr(self,name,mock);self.addCleanup(p.stop)
        p=patch.object(heart,'dependency_inventory',return_value=({},{}));p.start();self.addCleanup(p.stop)
        p=patch.object(heart.dependencies,'build_contract',return_value={'version':1});p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'patch_states',return_value={'feedback/map':{'marker':'before'}});p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'get_comp',return_value=self.comp);p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'open_verified',return_value=self.comp);self.opened=p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'request_reconnect',side_effect=lambda:self.state.update(arena_connected=True));p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'apply_state');self.apply=p.start();self.addCleanup(p.stop)

    def test_missing_critical_layer_aborts_before_recovery_save_or_open(self):
        import json
        self.data['layers']={'missing':{'clip':None}}
        (self.root/'Fixture.json').write_text(json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,'Missing or ambiguous layer'):
            self.heart.patch_recall('Fixture',1)
        self.arena_post.assert_not_called();self.opened.assert_not_called()

    def test_apply_failure_attempts_recovery_and_reports_restored_state(self):
        self.apply.side_effect=[RuntimeError('apply failed'),None]
        with self.assertRaisesRegex(RuntimeError,'previous controllable state restored'):
            self.heart.patch_recall('Fixture',1)
        self.assertEqual(self.opened.call_count,2)
        self.assertEqual(self.apply.call_args_list[-1].args[1],{'marker':'before'})
        self.assertEqual((self.state['bars'],self.state['hold']),(8,True))

    def test_missing_plugin_aborts_before_save_or_open(self):
        self.require_dependencies.side_effect=ValueError('Missing effect plugin')
        with self.assertRaisesRegex(ValueError,'Missing effect plugin'):
            self.heart.patch_recall('Fixture',1)
        self.arena_post.assert_not_called();self.opened.assert_not_called();self.apply.assert_not_called()

    def test_bad_native_route_recovers_before_requested_motion_is_applied(self):
        self.require_dependencies.side_effect=[None,ValueError('router mismatch'),None]
        with self.assertRaisesRegex(RuntimeError,'previous controllable state restored'):
            self.heart.patch_recall('Fixture',1)
        self.apply.assert_called_once()
        self.assertEqual(self.apply.call_args.args[1],{'marker':'before'})
        self.assertEqual(self.capture_native_snapshot.call_count,2)

    def test_recovery_failure_reports_partial_state(self):
        self.apply.side_effect=[RuntimeError('apply failed'),RuntimeError('renderer disconnected')]
        with self.assertRaisesRegex(RuntimeError,'recovery incomplete: renderer disconnected'):
            self.heart.patch_recall('Fixture',1)
        self.assertEqual(self.opened.call_count,2)

    def test_manual_cancellation_at_end_of_recovery_preserves_new_settings(self):
        attempts=[]
        def apply(*args):
            attempts.append(args)
            if len(attempts)==1:raise RuntimeError('apply failed')
            self.ops.cancel()
            self.state.update(bars=99,hold=False)
        self.apply.side_effect=apply
        with self.assertRaises(Cancelled):
            self.heart.patch_recall('Fixture',1)
        self.assertEqual((self.state['bars'],self.state['hold']),(99,False))
