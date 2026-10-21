import asyncio
import copy
import threading
import time
import unittest
from discovery import Discovery
from scan import discover
from test_phase_detection import fixture


class DiscoveryWorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_simultaneous_layer_updates_publish_one_coherent_batch(self):
        messages=[];worker=Discovery(messages.append);worker.configure(dict(serial=1))
        for lid in range(4):
            worker.publish(time.perf_counter(),event='clip',layer_id=lid,patch=dict(epoch='one',remove=['old'+str(lid)],targets=[dict(id='new'+str(lid))],layers=[dict(id=lid,active=2)],stage_only=True))
        self.assertEqual(messages,[])
        await asyncio.sleep(.015)
        self.assertEqual(len(messages),1);self.assertEqual(messages[0]['clip_layers'],[0,1,2,3])
        self.assertEqual(len(messages[0]['patch']['targets']),4)

    async def test_queued_old_generation_is_cancelled(self):
        messages=[];worker=Discovery(messages.append);worker.configure(dict(serial=1))
        worker.publish(time.perf_counter(),event='clip',layer_id=1,patch=dict(epoch='one',targets=[]))
        worker.configure(dict(serial=2));await asyncio.sleep(.015)
        self.assertEqual(messages,[])

    async def test_clip_handoff_publishes_before_slow_mode_inspection_finishes(self):
        native=fixture();catalog=discover(native);clip=copy.deepcopy(native['layers'][0]['clips'][0]);clip['id']=999
        catalog['layers'][0]['clips'].append(dict(id=999,col=2,name='New',description=clip['video']['description']))
        started=threading.Event();release=threading.Event();messages=[]
        def inspect(result,previous,budget):started.set();release.wait(1);return result
        worker=Discovery(messages.append,active=lambda layer:(layer['id'],clip),inspect=inspect)
        worker.configure(dict(serial=1,catalog=catalog));task=asyncio.create_task(worker.modes())
        try:
            await asyncio.to_thread(started.wait,.5)
            await worker.poll_layer(catalog['layers'][0],1,worker.revision)
            await asyncio.sleep(.012)
            self.assertEqual(messages[0]['event'],'clip')
            self.assertEqual(messages[0]['patch']['layers'][0]['active'],2)
            self.assertFalse(any(t.get('clip_id')==40 for t in worker.catalog['targets']))
            release.set();await asyncio.sleep(.02)
            self.assertFalse(any(t.get('clip_id')==40 for t in worker.catalog['targets']),'Old mode result must not revive the outgoing clip')
        finally:worker.stopped=True;release.set();task.cancel();await asyncio.gather(task,return_exceptions=True)

    async def test_inflight_launch_generation_cannot_reintroduce_old_clip(self):
        catalog=discover(fixture());messages=[];started=threading.Event();release=threading.Event()
        def active(layer):started.set();release.wait(1);return layer['id'],None
        worker=Discovery(messages.append,active=active);worker.configure(dict(serial=1,catalog=catalog))
        task=asyncio.create_task(worker.poll_layer(catalog['layers'][0],1,worker.revision))
        await asyncio.to_thread(started.wait,.5);worker.configure(dict(serial=2,launches=[20]));release.set();await task
        self.assertEqual(messages,[]);self.assertEqual(worker.catalog['layers'][0]['active'],1);self.assertEqual(worker.due[20],0)


if __name__=='__main__':unittest.main()
