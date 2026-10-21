import unittest
import clip_navigation as nav
class NavigationTests(unittest.TestCase):
 def test_identity_not_name_or_position(self):
  rows=nav.annotate([dict(col=81,name='renamed',source='Heart Torus'),dict(col=2,name='Heart Torus',source='other')])
  self.assertTrue(rows[0]['heart_copy']);self.assertFalse(rows[1]['heart_copy'])
 def test_bank_keeps_composition_order_and_all_retains_originals(self):
  rows=nav.annotate([dict(col=13,source='Heart HypnoWorm'),dict(col=28,source='HypnoWorm')]);l=dict(bank='heart',clips=rows,heart_copies=[rows[0]])
  self.assertEqual(nav.candidates(l),[rows[0]]);l['bank']='all';self.assertEqual(nav.candidates(l),rows);self.assertTrue(rows[1]['note'])
 def test_forms_and_empty_bank(self):
  self.assertEqual(nav.candidates(dict(bank='forms',forms=[1])),[1]);self.assertEqual(nav.candidates(dict(bank='heart')),[])
 def test_exploration_excludes_diagnostics_and_unreviewed_sources(self):
  rows=nav.annotate([dict(col=i,source=n) for i,n in enumerate(['SpaceSpore','SP State Test','Metaballs','unknown','Heart Capsule'])])
  picked=nav.exploration(rows,'figure');self.assertEqual([x['source'] for x in picked],['SpaceSpore','Heart Capsule'])
  self.assertEqual(nav.exploration(rows,'field'),[])
  self.assertEqual(nav.candidates(dict(bank='explore',explore=picked)),picked)
