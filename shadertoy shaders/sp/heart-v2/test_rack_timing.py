"""Independent accent timing and continuous soft-toggle ownership."""
import copy
import json
import unittest
from test_session_controls import engine


class RackTimingTests(unittest.TestCase):
    def setup(self):
        e=engine();row=e.rack_config['rows'][0]
        hit=copy.deepcopy(next(p for p in row['pads'] if p['id']=='twitch'))
        row['pads'].append(dict(hit,id='zoom'))
        row['pads'].append(dict(hit,id='mirror',mode='fade'))
        return e

    def set_length(self,e,pad,length):
        e.session.configure_timing(dict(epoch=e.catalog['epoch'],row='stage',pad=pad,length=length))

    def test_each_hit_and_fade_remembers_its_own_length(self):
        e=self.setup();self.set_length(e,'twitch',.125);self.set_length(e,'zoom',4);self.set_length(e,'mirror',2)
        e.session.configure(dict(epoch=e.catalog['epoch'],row='stage',kick='twitch',snare='zoom',pattern='alternate',running=True))
        prefs=json.loads(json.dumps(e.session.preferences));e.session.loops.clear();e.session.preferences=prefs
        self.assertFalse(e.session.loop('stage')['running'])
        self.assertEqual(e.session.state()['loops']['stage']['timings'],dict(twitch=.125,zoom=4,mirror=2))
        e.session.configure(dict(epoch=e.catalog['epoch'],row='stage',running=True))
        self.assertEqual(e.session.due(.5)[0]['pad'],'zoom')
        self.assertEqual(e.session.due(.5)[0]['pad'],'twitch')

    def test_toggles_and_native_events_do_not_gain_fake_decay_settings(self):
        e=self.setup()
        for pad in ['melt','pixel']:
            with self.assertRaises(ValueError):self.set_length(e,pad,1)
        for length in [False,float('nan'),float('inf'),0,9,'1']:
            with self.assertRaises(ValueError):self.set_length(e,'zoom',length)
        with self.assertRaises(ValueError):e.session.configure_timing(dict(epoch='old',row='stage',pad='zoom',length=1))
        with self.assertRaises(ValueError):e.session.configure(dict(epoch=e.catalog['epoch'],row='stage',kick='mirror',running=True))

    def test_beat_release_tracks_tempo_hold_and_downbeat(self):
        e=self.setup();e.hold=True;e.effect_pulse(10,.8,1,beats=2)
        e.tick(.5,.5);self.assertAlmostEqual(e.current_value(10),.4)
        e.bpm=60;e.tick(.5,1);self.assertAlmostEqual(e.current_value(10),.125)
        e.downbeat();e.tick(.5,1.5);self.assertEqual(e.current_value(10),0)
        self.assertEqual(e.envelopes[10]['progress'],1)

    def fade(self,e,on):
        rows=e.rack_fade(dict(epoch=e.catalog['epoch'],row='stage',pad='mirror',action='enable',on=on))
        for b,start,level,record in rows:
            e.manual(b['bypass'],False,owner=record['owner']);e.confirm_switch(b['bypass'],e.switches[b['bypass']]['serial'],False)
            e.effect_pulse(b['opacity'],start,.5,owner=record['owner'],end=level if on else 0.,beats=1)
        return rows[0]

    def test_fade_reversal_uses_current_amount_and_keeps_original_strength(self):
        e=self.setup();e.params[10][1]['value']=.7;e.params[11][1]['value']=True
        b,start,level,first=self.fade(e,True);self.assertEqual(start,0);self.assertEqual(level,.7)
        self.assertTrue(e.rack_state()['stage']['enabled']['mirror'])
        e.tick(.25,.25);self.assertAlmostEqual(e.current_value(10),.35)
        b,start,level,second=self.fade(e,False);self.assertAlmostEqual(start,.35);self.assertEqual(level,.7);self.assertNotEqual(first['owner'],second['owner'])
        self.assertFalse(e.rack_state()['stage']['enabled']['mirror']);self.assertFalse(e.current_value(11),'Keep processing during fade-out')
        e.tick(.25,.5);self.assertAlmostEqual(e.current_value(10),.175)
        e.tick(.25,.75);self.assertEqual(e.current_value(10),0);self.assertTrue(second['bypass']);self.assertEqual(second['value'],.7)
        e.manual(10,.42,duration=0);self.assertNotIn(10,e.rack_returns)

    def test_disarm_and_replacement_cancel_a_fade(self):
        for change in ['disarm','replace']:
            e=self.setup();self.fade(e,True)
            if change=='disarm':e.disarm()
            else:
                c=copy.deepcopy(e.catalog);c['targets'][0]['effect_name']='Replacement';e.reconcile(c)
            self.assertNotIn(10,e.rack_returns)


if __name__=='__main__':unittest.main()
