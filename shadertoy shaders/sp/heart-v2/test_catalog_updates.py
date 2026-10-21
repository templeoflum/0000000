import unittest
from catalog_updates import apply_patch, merge_patches


class CatalogBatchTests(unittest.TestCase):
    def test_multiple_clips_and_mode_updates_equal_ordered_application(self):
        catalog=dict(epoch='one',targets=[dict(id='oldA'),dict(id='oldB'),dict(id='untouched')],layers=[dict(id=1,active=1,clips=[]),dict(id=2,active=1,clips=[])])
        patches=[dict(epoch='one',remove=['oldA'],targets=[dict(id='newA',params=[])],layers=[dict(id=1,active=2)],stage_only=True),
                 dict(epoch='one',remove=['oldB'],targets=[dict(id='newB',params=[])],layers=[dict(id=2,active=2)],stage_only=True),
                 dict(epoch='one',targets=[dict(id='newA',params=[dict(id=7,native_phase=True)])],native_phase_mode=True,stage_only=False)]
        expected=catalog;combined=patches[0]
        for p in patches:expected=apply_patch(expected,p)
        for p in patches[1:]:combined=merge_patches(combined,p)
        self.assertEqual(apply_patch(catalog,combined),expected)
        self.assertFalse(combined['stage_only'])

    def test_latest_switch_drops_intermediate_clip_before_publication(self):
        first=dict(epoch='one',remove=['A'],targets=[dict(id='B')],layers=[dict(id=1,active=2)],stage_only=True)
        second=dict(epoch='one',remove=['B'],targets=[dict(id='C')],layers=[dict(id=1,active=3)],stage_only=True)
        merged=merge_patches(first,second)
        self.assertEqual(merged['targets'],[dict(id='C')]);self.assertEqual(set(merged['remove']),{'A','B'})
        self.assertEqual(merged['layers'],[dict(id=1,active=3)])

    def test_compositions_cannot_share_a_batch(self):
        with self.assertRaises(ValueError):merge_patches(dict(epoch='one'),dict(epoch='two'))


if __name__=='__main__':unittest.main()
