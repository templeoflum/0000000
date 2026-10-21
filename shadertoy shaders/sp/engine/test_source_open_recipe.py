import unittest
from types import SimpleNamespace
from unittest.mock import patch
import heart
class SourceOpenRecipeTests(unittest.TestCase):
 def test_corpus_open_preserves_visual_comparison(self):
  for name,support,mult in [('Heart Barberpole Field','Contrast',16.),('Heart Stepping Feet Field','Stripes',1.)]:
   slots=[SimpleNamespace(name=n) for n in ['Phase',support]]
   c=SimpleNamespace(name=name,atom=None,role='field',slots=slots)
   phase=heart.opening_settings(c,slots[0],.5,(0.,1.));fixed=heart.opening_settings(c,slots[1],.2,(0.,1.))
   self.assertTrue(phase['drive']);self.assertEqual(phase['mult'],mult);self.assertEqual(phase['shape'],0)
   self.assertFalse(fixed['drive']);self.assertEqual(fixed['manual'],1.)
 def test_unprofiled_source_uses_schema_selection(self):
  c=SimpleNamespace(name='Unprofiled',atom=None,role='field',slots=[])
  with patch.object(heart,'guard_context',return_value=None):
   self.assertFalse(heart.opening_settings(c,SimpleNamespace(name='New knob'),.5,(0.,1.))['drive'])
 def test_authored_home_does_not_open_camera_or_ignore_bounds(self):
  slots=[SimpleNamespace(name=n,kind='ParamRange',pmin=0.,pmax=1.) for n in ['camX','spinRate','Warp','Hue']]
  c=SimpleNamespace(name='Example',atom=None,role='field',slots=slots)
  profile={'bindings':{'Warp':{'range':[.45,.52]}}}
  with patch.object(heart,'home_profile',return_value=profile):
   self.assertFalse(heart.opening_settings(c,slots[0],.5,(0.,1.))['drive'])
   self.assertFalse(heart.opening_settings(c,slots[1],.5,(0.,1.))['drive'])
   r=heart.opening_settings(c,slots[2],.5,(0.,1.));self.assertEqual((r['lo'],r['hi']),(.45,.52))
   self.assertFalse(heart.opening_settings(c,slots[2],.9,(0.,1.))['drive'])
