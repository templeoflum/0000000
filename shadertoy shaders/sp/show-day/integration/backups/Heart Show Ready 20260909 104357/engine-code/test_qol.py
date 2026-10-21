import unittest
from unittest.mock import patch
import heart

class PerformanceQoL(unittest.TestCase):
    def test_effect_presses_ignore_old_quantize_settings(self):
        with patch.object(heart,'load_fx',return_value={}):fx=heart.Effect('q','L',1,1,'test',1,2,1)
        for mode in ['latch','momentary','oneshot']:
            fx.manual(0);fx.cfg.update(mode=mode,quant=8);fx.press(.13)
            self.assertEqual(fx.target,1);self.assertIsNone(fx.pending)

    def test_label_survives_incomplete_and_single_empty_poll(self):
        row={'clip':'Shell','ccol':2,'clips':[{'col':2,'name':'Shell'},{'col':3,'name':'Seed'}]}
        heart.update_connected_label(row,[(2,None)])
        self.assertEqual(row['clip'],'Shell')
        heart.update_connected_label(row,[(2,'Disconnected')]);self.assertEqual(row['clip'],'Shell')
        heart.update_connected_label(row,[(2,'Connected'),(3,'Previewing')]);self.assertEqual(row['clip'],'Seed')
        for _ in range(2):heart.update_connected_label(row,[(2,'Disconnected'),(3,'Disconnected')])
        self.assertEqual(row['clip'],'');self.assertEqual(row['ccol'],0)

    def test_rebuilt_rows_are_complete_and_keep_fader_hold(self):
        comp={'layers':[{'name':{'value':'figure'},'video':{'opacity':{'id':10,'value':.3}},'bypassed':{'id':11,'value':False},'clips':[{'name':{'value':'Shell'},'video':{'description':'x'},'connected':{'id':12,'value':'Connected'}}]}]}
        with patch.object(heart.time,'time',return_value=5):
            rows=heart.layer_rows(comp,[{'id_opacity':10,'opacity':.7,'_hold':4.8}])
        self.assertEqual(rows[0]['clip'],'Shell');self.assertEqual(rows[0]['ccol'],1)
        self.assertEqual(rows[0]['opacity'],.7);self.assertEqual(rows[0]['clips'][0]['name'],'Shell')
