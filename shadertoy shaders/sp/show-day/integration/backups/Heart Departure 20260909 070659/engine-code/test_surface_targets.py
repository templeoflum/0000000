"""No live server: stale surface gestures and ordinary effect takeover."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock
import heart


class SurfaceTargetTests(unittest.TestCase):
    def test_replacement_source_at_same_column_is_rejected(self):
        d={'cmd':'manual','layer':5,'col':3,'instance':'first'}
        with patch.object(heart,'CLIPS',{(4,2):SimpleNamespace(instance='first')}):
            heart.validate_surface_target(d)
            heart.CLIPS[(4,2)]=SimpleNamespace(instance='replacement')
            with self.assertRaisesRegex(ValueError,'target changed'):heart.validate_surface_target(d)

    def test_same_named_effects_are_scoped_and_missing_stays_missing(self):
        fx={'layer/A/effect/Cloner~1':SimpleNamespace(instance='a'),
            'layer/A/effect/Cloner~2':SimpleNamespace(instance='b')}
        with patch.object(heart,'FX',fx):
            d={'cmd':'fx_param','key':'layer/A/effect/Cloner~2','instance':'b'}
            heart.validate_surface_target(d)
            del fx[d['key']]
            with self.assertRaises(ValueError):heart.validate_surface_target(d)

    def test_stale_release_is_left_to_existing_owner_tracking(self):
        with patch.object(heart,'FX',{}):
            heart.validate_surface_target({'cmd':'fx_release','key':'gone','instance':'old'})

    def test_manual_effect_edit_claims_native_automation_once_per_binding(self):
        p={'id':123,'valuetype':'ParamRange','min':-180,'max':180,'value':0}
        with patch.object(heart,'CLIPS',{}),patch.object(heart,'put') as put,patch.object(heart.urllib.request,'urlopen',return_value=MagicMock()) as request:
            heart.manual_parameter(p,12.5);heart.manual_parameter(p,13)
            self.assertEqual(request.call_count,1)
            req=request.call_args.args[0]
            self.assertEqual(req.method,'DELETE');self.assertTrue(req.full_url.endswith('/123/phase-source'))
            self.assertEqual(put.call_args.args,(123,13))

    def test_failed_takeover_does_not_write_value(self):
        p={'id':123,'valuetype':'ParamRange','value':0}
        with patch.object(heart,'CLIPS',{}),patch.object(heart,'put') as put,patch.object(heart.urllib.request,'urlopen',side_effect=OSError('offline')):
            with self.assertRaises(OSError):heart.manual_parameter(p,1)
            put.assert_not_called();self.assertNotIn('_heart_manual',p)


if __name__=='__main__':unittest.main()
