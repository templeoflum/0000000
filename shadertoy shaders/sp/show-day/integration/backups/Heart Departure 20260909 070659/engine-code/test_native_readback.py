import unittest
from pathlib import Path
from unittest.mock import patch
import heart
class NativeReadbackTests(unittest.TestCase):
 def test_readback_restores_name_without_reopening(self):
  with patch.object(heart,'get_comp',side_effect=[{'name':{'id':1,'value':'Live'}},{'name':{'id':1,'value':'_verify'}}]),patch.object(heart,'arena_post') as post,patch.object(heart,'put_http') as put:
   heart.capture_native_snapshot(Path('/tmp/_verify.avc'))
   post.assert_called_once_with('/composition/save','file:///tmp/_verify.avc');put.assert_called_once_with(1,'Live')
 def test_save_failure_still_restores_name(self):
  with patch.object(heart,'get_comp',return_value={'name':{'id':1,'value':'Live'}}),patch.object(heart,'arena_post',side_effect=OSError('save failed')),patch.object(heart,'put_http') as put:
   with self.assertRaises(OSError):heart.capture_native_snapshot(Path('/tmp/_verify.avc'))
   put.assert_called_once_with(1,'Live')
 def test_generation_change_does_not_rename_other_composition(self):
  with patch.object(heart,'get_comp',side_effect=[{'name':{'id':1,'value':'Live'}},{'name':{'id':2,'value':'Other'}}]),patch.object(heart,'arena_post'),patch.object(heart,'put_http') as put:
   with self.assertRaisesRegex(RuntimeError,'Composition changed'):heart.capture_native_snapshot(Path('/tmp/_verify.avc'))
   put.assert_not_called()
