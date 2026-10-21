"""Native bypass only; all network operations isolated."""
import copy
import unittest
from unittest.mock import patch
import heart

class BlackoutTests(unittest.TestCase):
    def setUp(self):
        self.state={'arena_connected':True,'hold':True,'play_action':{'busy':True}}
        p=patch.object(heart,'STATE',self.state);p.start();self.addCleanup(p.stop)
        self.comp={'bypassed':{'id':42,'valuetype':'ParamBoolean','value':False},'layers':[{'level':.7}]}
        p=patch.object(heart,'get_comp',return_value=self.comp);self.get=p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'put_http');self.put=p.start();self.addCleanup(p.stop)
        p=patch.object(heart,'cur_val',return_value=True);self.read=p.start();self.addCleanup(p.stop)
    def test_busy_cut_uses_fresh_id_and_native_readback_without_motion_or_layer_edits(self):
        before=copy.deepcopy(self.comp)
        result=heart.set_blackout(True,42)
        self.put.assert_called_once_with(42,True);self.read.assert_called_once_with(42)
        self.assertTrue(result['on']);self.assertTrue(self.state['hold']);self.assertEqual(self.comp,before)
        self.assertTrue(self.state['play_action']['busy'])
    def test_restore_is_explicit_false(self):
        self.comp['bypassed']['value']=True;self.read.return_value=False
        self.assertFalse(heart.set_blackout(False,42)['on']);self.put.assert_called_once_with(42,False)
    def test_unconfirmed_write_never_reports_requested_state(self):
        self.read.return_value=False
        with self.assertRaisesRegex(ValueError,'not confirmed'):heart.set_blackout(True,42)
        self.assertFalse(self.state['blackout']['on']);self.assertTrue(self.state['blackout']['error'])
    def test_stale_identity_disconnected_and_invalid_schema_do_not_write(self):
        with self.assertRaises(ValueError):heart.set_blackout(True,99)
        self.comp['bypassed']['valuetype']='ParamRange'
        with self.assertRaises(ValueError):heart.set_blackout(True,42)
        self.state['arena_connected']=False
        with self.assertRaises(ValueError):heart.set_blackout(True,42)
        self.put.assert_not_called()
    def test_external_subscription_follows_native_boolean_and_ignores_stale_id(self):
        heart.observe_blackout(self.comp)
        heart.effect_feedback({'type':'parameter_update','id':42,'value':True},{42:(None,'blackout')})
        self.assertTrue(self.state['blackout']['on'])
        self.comp['bypassed']['id']=43;heart.observe_blackout(self.comp)
        heart.effect_feedback({'type':'parameter_update','id':42,'value':True},{42:(None,'blackout')})
        self.assertFalse(self.state['blackout']['on'])
    def test_network_failure_is_not_success(self):
        self.put.side_effect=OSError('offline')
        with self.assertRaises(OSError):heart.set_blackout(True,42)
        self.assertFalse(self.state['blackout']['on']);self.assertIn('offline',self.state['blackout']['error'])
if __name__=='__main__':unittest.main()
