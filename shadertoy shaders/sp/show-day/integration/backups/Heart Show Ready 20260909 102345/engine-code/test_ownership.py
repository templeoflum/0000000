"""Offline ownership audit: renderer reads/writes and persistence are mocked.

Guard tests cover current safety behavior. Characterization tests explicitly
record missing ongoing observation; they are not claims that the desired polling
protocol has been implemented.
"""
import copy
import io
import json
import unittest
from unittest.mock import patch

import heart


class OwnershipAuditTests(unittest.TestCase):
    def setUp(self):
        atom={'Gain':{'drive':True,'cyclic':False,'ratio':'1:4','mult':1,
                      'offset':0,'shape':1,'lo':.2,'hi':.8}}
        self.payload={'name':{'value':'ownership fixture'},
                      'video':{'description':'OwnershipFixture',
                               'sourceparams':{'Gain':{'id':42,'valuetype':'ParamRange',
                                                      'min':0.,'max':1.,'value':.25}}}}
        replacements={'ATOMS':{'OwnershipFixture':atom},'CONTROL_CONFIG':{},'MOTION':{},
                      'RESUME':{},'DRIVE_ALL':False,'SLOT_WRITERS':{}}
        for name,value in replacements.items():
            p=patch.object(heart,name,value);p.start();self.addCleanup(p.stop)
        for name in ('save_atoms','put_http','event'):
            p=patch.object(heart,name);setattr(self,name,p.start());self.addCleanup(p.stop)
        for name,value in [('load_armsets',{}),('load_homes',{'ownership fixture':{'version':2}})]:
            p=patch.object(heart,name,return_value=value);p.start();self.addCleanup(p.stop)
        self.phase='static'
        def response(*args,**kwargs):
            return io.BytesIO(json.dumps({'phase_source':self.phase}).encode())
        p=patch.object(heart.urllib.request,'urlopen',side_effect=response)
        self.http=p.start();self.addCleanup(p.stop)
        self.clip=heart.Clip(0,0,self.payload);self.clip.refresh(self.payload)
        self.slot=self.clip.slots[0]

    def test_initial_static_owner_is_heart(self):
        self.clip.takeover(None)
        self.assertEqual(self.slot.owner,'heart')
        self.assertTrue(self.slot.drive)
        self.assertEqual(self.http.call_count,1)

    def test_initial_external_owner_is_not_automatically_claimed(self):
        self.phase='timeline';self.slot.ids['Drive']=43
        self.clip.takeover(None)
        self.assertEqual(self.slot.owner,'resolume')
        self.assertFalse(self.slot.drive)
        self.put_http.assert_not_called()
        self.assertIsInstance(self.http.call_args.args[0],str)  # GET, no DELETE.

    def test_failed_initial_probe_disables_continuous_writes(self):
        self.http.side_effect=TimeoutError('offline fixture')
        self.clip.takeover(None)
        self.assertEqual(self.slot.owner,'unverified')
        self.assertFalse(self.slot.drive)
        self.put_http.assert_not_called()

    def test_explicit_claim_deletes_phase_source_before_enabling_heart_owner(self):
        self.phase='bpm_sync';self.clip.takeover(None)
        self.slot.ids['Drive']=43;self.http.reset_mock()
        heart.claim_slot(self.slot)
        request=self.http.call_args.args[0]
        self.assertEqual(request.get_method(),'DELETE')
        self.assertTrue(request.full_url.endswith('/42/phase-source'))
        self.put_http.assert_called_once_with(43,False)
        self.assertEqual(self.slot.owner,'heart')

    def test_failed_explicit_claim_does_not_assert_heart_ownership(self):
        self.phase='timeline';self.clip.takeover(None)
        self.http.side_effect=TimeoutError('offline fixture')
        with self.assertRaises(TimeoutError):heart.claim_slot(self.slot)
        self.assertEqual(self.slot.owner,'resolume')
        self.put_http.assert_not_called()

    def test_characterization_refresh_never_rechecks_changed_phase_source(self):
        self.clip.takeover(None)
        self.phase='timeline'
        for _ in range(8):self.clip.refresh(self.payload)
        self.assertEqual(self.http.call_count,1)
        self.assertEqual(self.slot.owner,'heart')
        self.assertTrue(self.slot.drive)
        self.assertEqual(heart.clip_schema(self.payload),self.clip.schema)

    def test_external_value_is_used_for_display_pose_without_mutating_home(self):
        self.phase='timeline';self.clip.takeover(None)
        updated=copy.deepcopy(self.payload)
        updated['video']['sourceparams']['Gain']['value']=.9
        self.clip.refresh(updated)
        self.assertEqual(self.slot.owner,'resolume')
        self.assertAlmostEqual(self.slot.cfg['manual'],.25)
        self.assertAlmostEqual(heart.slot_display_value(self.slot,self.slot.value(self.slot.eff_cfg(self.clip.g))),.9)

    def test_resume_does_not_rearm_drive_flag_under_external_owner(self):
        self.phase='timeline'
        heart.RESUME[(1,1)]={'slots':[{'name':'Gain','drive':True,'v':.4}]}
        self.clip.takeover(None)
        self.assertEqual(self.slot.owner,'resolume')
        self.assertFalse(self.slot.drive)

    def test_characterization_cached_heart_claim_makes_no_native_request(self):
        self.clip.takeover(None);self.http.reset_mock()
        self.phase='timeline'  # External change after the last ownership observation.
        heart.claim_slot(self.slot)
        self.http.assert_not_called()
        self.assertEqual(self.slot.owner,'heart')

    def test_forced_discrete_claim_reasserts_even_cached_heart_owner(self):
        self.clip.takeover(None);self.http.reset_mock();before=self.slot.claim_epoch
        self.phase='timeline';self.slot._lastout=.5;self.slot._lastv=.5
        heart.claim_slot(self.slot,force=True)
        self.assertEqual(self.http.call_args.args[0].get_method(),'DELETE')
        self.assertGreater(self.slot.claim_epoch,before)
        self.assertEqual(self.slot.owner,'heart')
        self.assertFalse(self.slot.claim_inflight)
        self.assertIsNone(self.slot._lastout)
        self.assertEqual(self.slot._lastv,9.)

    def test_choice_force_claim_never_deletes_native_phase_source(self):
        self.slot.choices=['a','b'];self.slot.owner='heart';before=self.slot.claim_epoch
        self.http.reset_mock();heart.claim_slot(self.slot,force=True)
        self.http.assert_not_called()
        self.assertGreater(self.slot.claim_epoch,before)


class ObserverProtocolTests(unittest.TestCase):
    def setUp(self):
        OwnershipAuditTests.setUp(self)
        from ownership import OwnershipObserver
        from delivery import LatestValues
        self.clip.takeover(None)
        self.now=[0.];self.generation=[1];self.available=[True];self.live=[self.clip]
        self.read=lambda pid:self.phase
        self.observer=OwnershipObserver(
            clips=lambda:self.live,available=lambda:self.available[0],
            generation=lambda:self.generation[0],
            current=lambda c,s:c in self.live and any(x is s for x in c.slots),
            read_phase=lambda pid:self.read(pid),release=heart.release_native_slot,
            clock=lambda:self.now[0])
        p=patch.object(heart,'OUT',LatestValues());p.start();self.addCleanup(p.stop)
        heart.SLOT_WRITERS[42]=self.slot

    def test_external_phase_demotes_and_discards_only_its_pending_value(self):
        heart.OUT.put((42,.5));heart.OUT.put((99,.7));self.phase='timeline'
        self.assertTrue(self.observer.step())
        self.assertEqual(self.slot.owner,'resolume');self.assertFalse(self.slot.drive)
        self.assertEqual(heart.OUT.take(),[(99,.7)])
        self.assertFalse(heart.ownership_allows_write(42))  # Already-dequeued value also blocked.
        self.assertTrue(heart.ownership_allows_write(99))
        self.put_http.assert_not_called()  # Observer does not take ownership or touch native Drive.

    def test_static_read_never_reclaims_released_slot(self):
        self.phase='timeline';self.observer.step()
        self.phase='static';self.now[0]=2.;self.observer.step()
        self.assertEqual(self.slot.owner,'resolume');self.assertFalse(self.slot.drive)

    def test_id_replacement_discards_old_response(self):
        def read(pid):self.slot.ids['']=99;return 'timeline'
        self.read=read;self.observer.step()
        self.assertEqual(self.slot.owner,'heart')

    def test_generation_change_discards_old_response(self):
        def read(pid):self.generation[0]+=1;return 'timeline'
        self.read=read;self.observer.step()
        self.assertEqual(self.slot.owner,'heart')

    def test_removed_clip_discards_old_response(self):
        def read(pid):self.live.clear();return 'timeline'
        self.read=read;self.observer.step()
        self.assertEqual(self.slot.owner,'heart')

    def test_explicit_claim_epoch_discards_old_response(self):
        def read(pid):heart.claim_slot(self.slot);return 'timeline'
        self.read=read;self.observer.step()
        self.assertEqual(self.slot.owner,'heart')

    def test_disconnect_and_busy_skip_queries(self):
        self.available[0]=False
        self.assertFalse(self.observer.step());self.assertEqual(self.observer.polls,0)

    def test_error_does_not_reclaim_or_mutate_owner(self):
        def read(pid):raise TimeoutError('fixture')
        self.read=read;self.observer.step()
        self.assertEqual(self.observer.errors,1);self.assertEqual(self.slot.owner,'heart')

    def test_read_rate_is_bounded_and_other_lane_is_fair(self):
        from types import SimpleNamespace
        slots=[]
        for i in range(50):
            sl=heart.Slot(str(i),False);sl.ids={'':100+i};sl.owner='heart';sl.drive=i<40
            slots.append(sl)
        self.live[:]=[SimpleNamespace(taken=True,slots=slots)]
        seen=[];self.read=lambda pid:(seen.append(pid) or 'static')
        for tick in range(1000):self.now[0]=tick/1000.;self.observer.step()
        self.assertLessEqual(len(seen),20)
        self.assertTrue(any(pid>=140 for pid in seen))
        self.assertEqual(len(seen),len(set(seen)))  # At least one second per target.

    def test_claim_inflight_slot_is_not_probed(self):
        self.slot.claim_inflight=True
        self.assertFalse(self.observer.step());self.assertEqual(self.observer.polls,0)


if __name__=='__main__':
    unittest.main()
