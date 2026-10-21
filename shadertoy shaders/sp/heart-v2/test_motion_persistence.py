import asyncio
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from motion_memory import MotionMemory, key, contract, SLOT_DEFAULTS, GROUP_DEFAULTS
from motion_persistence import MotionWriter
from test_motion_memory import started


class MotionChangeTests(unittest.TestCase):
    def test_snapshot_is_constant_cost_and_old_records_stay_unchanged(self):
        e = started(); e.motion_memory.capture(e)
        revision, snapshot = e.motion_memory.snapshot(); original = copy.deepcopy(snapshot)
        self.assertIs(snapshot, e.motion_memory.data)
        e.parameter_motion(5, dict(ratio='1:4', mult=.025)); e.motion_memory.capture(e)
        e.params[5][1]['options'].append('native edit')
        self.assertEqual(snapshot, original)
        self.assertGreater(e.motion_memory.revision, revision)

    def test_small_edit_does_not_copy_or_send_saved_library(self):
        e = started(); e.motion_memory.capture(e); e.motion_memory.acknowledge(e.motion_memory.revision)
        rows = e.motion_memory.data['compositions']['10']['targets']
        original_count = len(rows)
        for n in range(20000): rows['historical-'+str(n)] = {'unchanged': 'x'*100}
        e.parameter_motion(5, dict(offset=.42)); e.motion_memory.capture(e)
        revision, changes = e.motion_memory.changes()
        self.assertEqual(len(changes['10']['targets']), 1)
        self.assertLess(len(json.dumps(changes)), 2500)
        self.assertEqual(len(e.motion_memory.data['compositions']['10']['targets']), 20000+original_count)

    def test_untouched_static_controls_do_not_create_history(self):
        e=started();e.motion_memory.capture(e)
        rows=e.motion_memory.data['compositions']['10']['targets'].values()
        self.assertEqual({int(pid) for row in rows for pid in row['params']},{2,5})

    def test_legacy_defaults_compact_without_losing_explicit_off_or_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            e=started();e.drive(5,False);e.parameter_motion(6,dict(mult=.025));e.motion_memory.capture(e)
            data=copy.deepcopy(e.motion_memory.data);target=next(t for t in e.catalog['targets'] if t['id']=='effect:31')
            from motion_memory import identity
            data['compositions']['10']['targets'][key(target)]=dict(identity=identity(target),group=GROUP_DEFAULTS,params={'1':dict(contract=contract(e.params[1][1]),cfg=SLOT_DEFAULTS)})
            path=Path(directory)/'settings.json';MotionMemory.write(path,data);memory=MotionMemory();memory.load(path)
            self.assertNotIn(key(target),memory.data['compositions']['10']['targets'])
            source=next(t for t in e.catalog['targets'] if t['id']=='source:40')
            self.assertFalse(memory.parameter('10',source,e.params[5][1])['drive'])
            self.assertEqual(memory.parameter('10',source,e.params[6][1])['cfg']['mult'],.025)

    def test_acknowledgement_keeps_edits_that_arrived_during_write(self):
        e = started(); e.motion_memory.capture(e); revision, first = e.motion_memory.changes()
        e.parameter_motion(5, dict(mult=.025)); e.motion_memory.capture(e)
        e.motion_memory.acknowledge(revision)
        second_revision, second = e.motion_memory.changes()
        self.assertGreater(second_revision, revision)
        self.assertEqual(len(second['10']['targets']), 1)
        row = next(iter(second['10']['targets'].values()))
        self.assertEqual(row['params']['5']['cfg']['mult'], .025)
        self.assertEqual(next(r for r in first['10']['targets'].values() if '5' in r['params'])['params']['5']['cfg']['mult'], 1)


class MotionWriterTests(unittest.IsolatedAsyncioTestCase):
    async def test_return_to_defaults_removes_previous_record_on_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'settings.json';e=started();target=next(t for t in e.catalog['targets'] if t['id']=='effect:31')
            e.settings(target['id'],dict(amount=.3));e.motion_memory.capture(e);writer=MotionWriter(e.motion_memory,path)
            try:
                await writer.save();self.assertIn(key(target),json.loads(path.read_text())['compositions']['10']['targets'])
                e.settings(target['id'],dict(amount=1));e.motion_memory.capture(e)
                self.assertIsNone(e.motion_memory.changes()[1]['10']['targets'][key(target)])
                await writer.save();self.assertNotIn(key(target),json.loads(path.read_text())['compositions']['10']['targets'])
            finally:await writer.close()

    async def test_real_process_saves_changes_and_preserves_inactive_history(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'motion-settings.json'; e = started(); e.motion_memory.capture(e)
            MotionMemory.write(path, e.motion_memory.data)
            e.motion_memory.acknowledge(e.motion_memory.revision)
            old = json.loads(path.read_text()); e.parameter_motion(5, dict(mult=.025)); e.motion_memory.capture(e)
            writer = MotionWriter(e.motion_memory, path)
            try:
                with patch.object(e.motion_memory, 'snapshot', side_effect=AssertionError('Never copy the library on the timing thread')):
                    await writer.save()
                self.assertNotEqual(writer.process.pid, os.getpid())
                saved = json.loads(path.read_text())
                target = next(t for t in e.catalog['targets'] if t['id']=='source:40')
                self.assertEqual(saved['compositions']['10']['targets'][key(target)]['params']['5']['cfg']['mult'], .025)
                effect = next(t for t in e.catalog['targets'] if t['id']=='effect:32')
                self.assertEqual(saved['compositions']['10']['targets'][key(effect)], old['compositions']['10']['targets'][key(effect)])
                self.assertEqual(e.motion_memory.saved_revision, e.motion_memory.revision)
            finally: await writer.close()

    async def test_failed_disk_write_is_retained_and_can_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'missing'/'motion-settings.json'; e = started(); e.motion_memory.capture(e); writer=MotionWriter(e.motion_memory,path)
            try:
                with self.assertRaises(OSError): await writer.save()
                self.assertNotEqual(e.motion_memory.saved_revision, e.motion_memory.revision)
                path.parent.mkdir(); await writer.save()
                self.assertEqual(json.loads(path.read_text()), e.motion_memory.data)
                self.assertEqual(e.motion_memory.pending, {})
            finally: await writer.close()

    async def test_slow_writer_and_cancellation_do_not_block_clock_or_lose_new_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); worker=root/'slow.py'
            worker.write_text("import sys,json,time\nfrom pathlib import Path\nfor line in sys.stdin:\n m=json.loads(line);Path('received').touch()\n while not Path('release').exists():time.sleep(.005)\n print(json.dumps({'saved':m['revision']}),flush=True)\n")
            e=started();e.motion_memory.capture(e);writer=MotionWriter(e.motion_memory,root/'settings.json')
            writer.process=await asyncio.create_subprocess_exec(sys.executable,str(worker),cwd=root,stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE)
            task=asyncio.create_task(writer.save());ticks=0
            try:
                async with asyncio.timeout(5):
                    while not (root/'received').exists():
                        e.tick(.008,asyncio.get_running_loop().time());ticks+=1;await asyncio.sleep(.008)
                self.assertGreater(ticks,0);self.assertFalse(task.done())
                e.parameter_motion(5,dict(mult=.025));e.motion_memory.capture(e)
                task.cancel();await asyncio.sleep(.01);self.assertFalse(task.done(),'Finish the acknowledged write before releasing the save lock')
                (root/'release').touch()
                with self.assertRaises(asyncio.CancelledError):await task
                self.assertNotEqual(e.motion_memory.saved_revision,e.motion_memory.revision)
                await writer.save();self.assertEqual(e.motion_memory.saved_revision,e.motion_memory.revision)
            finally:
                (root/'release').touch();await asyncio.gather(task,return_exceptions=True);await writer.close()


if __name__=='__main__':unittest.main()
