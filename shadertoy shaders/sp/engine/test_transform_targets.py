"""Offline native Transform discovery and absence of envelope writes."""
import copy
import unittest
from unittest.mock import patch
import heart

class TransformTests(unittest.TestCase):
    def test_existing_clip_and_layer_transforms_are_distinct_and_have_motion(self):
        def transform(identity,pid):
            return {'name':'Transform','id':identity,'params':{'Position X':{'id':pid,'valuetype':'ParamRange','min':-1920,'max':1920,'value':0}}}
        comp={'name':{'id':'composition'},'layers':[{'name':{'value':'Figure'},'video':{'effects':[transform('layer-transform',101)]},'clips':[{'name':{'value':'Shape'},'connected':{'value':'Connected'},'video':{'effects':[transform('clip-transform',102)]}}]}]}
        original=copy.deepcopy(comp)
        with patch.object(heart,'FX',{}),patch.object(heart,'CLIPS',{}),patch.object(heart,'FX_RELEASES',{}),patch.object(heart,'EFFECT_RESUME',{}),patch.object(heart,'load_fx',return_value={}),patch.object(heart,'load_homes',return_value={}),patch.object(heart,'is_sp',return_value=False),patch.object(heart,'index_slot_owners'),patch.object(heart,'put') as put:
            heart.discover_fx(comp)
            self.assertEqual(len(heart.FX),2)
            self.assertEqual({fx.scope for fx in heart.FX.values()},{'L','K'})
            for fx in heart.FX.values():
                self.assertEqual(fx.target_kind,'transform')
                self.assertIsNone(fx.id_opacity);self.assertIsNone(fx.id_bypass)
                self.assertEqual([sl.name for sl in fx.motion.slots],['Position X'])
                self.assertFalse(fx.motion.slots[0].drive)
                fx.last_written=None;fx.step(.1,0)
            put.assert_not_called()
            self.assertEqual(comp,original)
            added=transform('added-transform',103)
            added['params']['Opacity']={'id':104,'valuetype':'ParamRange','min':0,'max':1,'value':1}
            added['bypassed']={'id':105,'value':False}
            comp['layers'][0]['video']['effects'].insert(0,added)
            heart.discover_fx(comp)
            fx=heart.FX['layer/Figure~1/effect/Transform~1']
            self.assertEqual(fx.native_identity,'added-transform')
            self.assertEqual(fx.target_kind,'effect')
            self.assertEqual((fx.id_opacity,fx.id_bypass),(104,105))
            self.assertEqual(heart.FX['layer/Figure~1/effect/Transform~2'].target_kind,'transform')

if __name__=='__main__':unittest.main()
