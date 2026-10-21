import asyncio
import copy
import math
import unittest
from unittest.mock import patch
from motion_clock import integral
from motion_frames import LatestFrame
from server import Engine
from test_phase_detection import fixture
from scan import discover, native_phases, refresh_active


def engine():
    c=discover(fixture())
    for t in c['targets']:
        for p in t['params']:
            if p.get('phase_route'):p['native_phase']=p['phase_route']
    c['native_phase_mode']=True
    e=Engine()
    with patch('server.time.perf_counter',return_value=0):
        e.reconcile(c);e.armed=e.connected=True;e.start_prepared()
    return e


class SharedClockTests(unittest.TestCase):
    def test_hour_of_irregular_frames_and_stalls_keeps_beat_distance(self):
        e=engine();now=0
        for dt in [.008,.011,.1,2.3,.007,17.574]*180:
            now+=dt;e.tick(dt,now)
        self.assertAlmostEqual(e.clock.beat,now*2,places=7)
        self.assertAlmostEqual(e.slots[2].phi,now*2/32,places=7)

    def test_rate_ramps_integrate_same_distance_across_stall(self):
        def setup():
            e=engine()
            with patch('server.time.perf_counter',return_value=0):
                e.motion_multiplier(dict(epoch=e.catalog['epoch'],scope='global',value=4,seconds=2))
                e.parameter_motion(2,dict(mult=.025,seconds=1))
            return e
        fine,stalled=setup(),setup()
        for n in range(1,501):fine.tick(.01,n*.01)
        stalled.tick(5,5)
        self.assertAlmostEqual(fine.slots[2].phi,stalled.slots[2].phi,places=9)
        self.assertAlmostEqual(fine.clock.paths[('global','layer:20')],stalled.clock.paths[('global','layer:20')],places=8)

    def test_drive_off_and_late_clip_join_running_phase(self):
        e=engine()
        with patch('server.time.perf_counter',return_value=0):e.drive(2,False)
        e.tick(8,8);off=e.slots[2].phi
        self.assertAlmostEqual(off,.5)
        c=copy.deepcopy(e.catalog);t=copy.deepcopy(next(t for t in c['targets'] if any(p['id']==2 for p in t['params'])))
        t['id']='new-source';t['params']=[copy.deepcopy(next(p for p in t['params'] if p['id']==2))];t['params'][0]['id']=999;c['targets'].append(t)
        with patch('server.time.perf_counter',return_value=8):e.reconcile(c);e.start_prepared()
        self.assertAlmostEqual(e.slots[999].phi,off)
        self.assertFalse(e.slots[2].drive)

    def test_hold_freezes_motion_and_morph_but_transport_and_downbeat_work(self):
        e=engine();e.tick(1,1)
        with patch('server.time.perf_counter',return_value=1):e.parameter_motion(2,dict(amount=.2,seconds=2))
        before=e.slots[2].phi;e.set_hold(True);e.tick(3,4)
        self.assertEqual(e.slots[2].phi,before)
        self.assertEqual(e.slots[2].blend(4)['amount'],1)
        self.assertEqual(e.clock.beat,8)
        e.set_hold(False);e.tick(1,5);self.assertGreater(e.slots[2].phi,before)
        e.downbeat();self.assertEqual(e.clock.beat,0);self.assertTrue(all(sl.phi==0 for sl in e.slots.values()))

    def test_new_parameter_joins_source_speed_history_during_a_ramp(self):
        e=engine();e.tick(8,8);target=e.params[2][0]
        with patch('server.time.perf_counter',return_value=8):e.settings(target,dict(rate=4,seconds=2))
        e.tick(1,9)
        c=copy.deepcopy(e.catalog);t=next(t for t in c['targets'] if t['id']==target);p=copy.deepcopy(next(p for p in t['params'] if p['id']==2));p['id']=999;t['params'].append(p)
        with patch('server.time.perf_counter',return_value=9):e.reconcile(c);e.start_prepared()
        self.assertAlmostEqual(e.slots[999].phi,e.slots[2].phi)
        for i in range(1,101):e.tick(.02,9+i*.02)
        self.assertAlmostEqual(e.slots[999].phi,e.slots[2].phi)
        self.assertAlmostEqual(e.slots[2].phi,.5+2/16*2.5+1/16*4)

    def test_amount_position_phase_are_independent_and_never_change_native_range(self):
        e=engine();p=e.params[2][1];before=copy.deepcopy(e.catalog);sl=e.slots[2]
        for amount,position in [(1,0),(.25,.5),(.25,0),(.25,1),(0,.37)]:
            with patch('server.time.perf_counter',return_value=0):e.parameter_motion(2,dict(amount=amount,range_offset=position,seconds=0))
            config=sl.blend(10);config['drive']=1
            values=[]
            for i in range(1001):sl.phi=i/1000;values.append(sl.value(config))
            self.assertAlmostEqual(min(values),(1-amount)*position)
            self.assertAlmostEqual(max(values),(1-amount)*position+amount)
        self.assertEqual(e.catalog,before)
        with patch('server.time.perf_counter',return_value=0):e.parameter_motion(2,dict(mult=-.025,seconds=0))
        phi=sl.phi;e.tick(1,1);self.assertLess(sl.phi,phi)

    def test_native_range_tuning_does_not_retire_clip_contract(self):
        c=discover(fixture());clip=copy.deepcopy(fixture()['layers'][0]['clips'][0])
        for p in clip['video'].get('sourceparams',{}).values():p['in']=.23;p['out']=.27
        result=refresh_active(c,{20:clip})
        self.assertFalse(result['_changed'])


class FrameMailboxTests(unittest.IsolatedAsyncioTestCase):
    async def test_backpressure_replaces_whole_frame(self):
        box=LatestFrame()
        for n in range(1000):box.put(dict(frame=n,values=[(1,n),(2,-n)]))
        self.assertEqual(await box.get(),dict(frame=999,values=[(1,999),(2,-999)]))
        self.assertEqual(box.dropped,999)


if __name__=='__main__':unittest.main()
