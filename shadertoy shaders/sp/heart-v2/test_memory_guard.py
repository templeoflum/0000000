"""Memory alarms use the OS counter, preserve deliberate pause, and fail visibly."""
import json,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import memory_guard as guard

class MemoryGuardTests(unittest.TestCase):
 def test_high_memory_pauses_heart_and_recovery_requires_deliberate_clear(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   with patch.object(guard,'ROOT',root),patch('sys.argv',['memory_guard.py','--once']),patch.object(guard.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'123\n','')),patch.object(guard,'notify') as notify:
    with patch.object(guard,'footprint',return_value=70*guard.GIB):guard.main()
    self.assertEqual(json.loads((root/'arena-memory.json').read_text())['status'],'pause')
    pause=(root/'api-paused.json').read_text();self.assertIn('70.0',pause);notify.assert_called_once()
    with patch.object(guard,'footprint',return_value=20*guard.GIB):guard.main()
    self.assertEqual((root/'api-paused.json').read_text(),pause)
    self.assertEqual(json.loads((root/'arena-memory.json').read_text())['status'],'normal')
 def test_warning_does_not_pause_and_failed_read_is_not_zero(self):
  with tempfile.TemporaryDirectory() as directory:
   root=Path(directory)
   with patch.object(guard,'ROOT',root),patch('sys.argv',['memory_guard.py','--once']),patch.object(guard.subprocess,'run',return_value=subprocess.CompletedProcess([],0,'123\n','')),patch.object(guard,'notify') as notify:
    with patch.object(guard,'footprint',return_value=45*guard.GIB):guard.main()
    self.assertFalse((root/'api-paused.json').exists());notify.assert_called_once()
    with patch.object(guard,'footprint',side_effect=OSError('permission denied')):guard.main()
    row=json.loads((root/'arena-memory.json').read_text());self.assertEqual(row['status'],'unavailable');self.assertNotIn('footprint_gib',row)
