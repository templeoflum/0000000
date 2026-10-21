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
 def test_unprofiled_source_retains_existing_open(self):
  c=SimpleNamespace(name='Unprofiled',atom=None,role='field',slots=[])
  with patch.object(heart,'guard_context',return_value=None):
   self.assertTrue(heart.opening_settings(c,SimpleNamespace(name='New knob'),.5,(0.,1.))['drive'])
