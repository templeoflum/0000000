import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import heart

class ManualAtomicTests(unittest.TestCase):
 def setUp(self):
  self.c=SimpleNamespace(layer=0,col=0,g={'pattern':0,'seed':0,'spread':1,'depth':1.,'fm':0.},morph=3.)
  self.sl=heart.Slot('value',False);s=self.sl;s.index=0;s.ids={'':42};s.cfg={'manual':.2,'ratio':'1:1','mult':1.,'offset':0.,'shape':1,'lo':0.,'hi':1.};s.drive=False;s.retarget(self.c.g,0);s._lastv=.2;s._lastout=.2
  self.c.slots=[s];p=patch.dict(heart.CLIPS,{(0,0):self.c},clear=True);p.start();self.addCleanup(p.stop)
 def test_scan_cannot_overwrite_an_explicit_edit(self):
  entered=threading.Event();release=threading.Event();started=threading.Event();done=threading.Event();c=self.c;s=self.sl
  def scan(_):
   snapshot=dict(s.cfg);entered.set();release.wait(2);s.cfg=snapshot
  c._refresh=scan
  a=threading.Thread(target=heart.Clip.refresh,args=(c,{}));a.start();self.assertTrue(entered.wait(1))
  def edit():
   started.set();heart.set_manual_value(c,s,.7);done.set()
  b=threading.Thread(target=edit);b.start();self.assertTrue(started.wait(1))
  try:self.assertFalse(done.wait(.05),'manual edit raced an unfinished scan')
  finally:release.set();a.join(2);b.join(2)
  self.assertTrue(done.is_set());self.assertEqual(s.cfg['manual'],.7);self.assertEqual(s.value(s.blend(100)),.7)
 def test_same_value_invalidates_delivery_cache(self):
  heart.set_manual_value(self.c,self.sl,.2)
  self.assertIsNone(self.sl._lastout);self.assertEqual(self.sl._lastv,9.)
 def test_manual_stops_drive_and_completes_transition(self):
  s=self.sl;s.drive=True;s.dur=3.;s.retarget(self.c.g,1)
  heart.set_manual_value(self.c,s,.8)
  self.assertFalse(s.drive);self.assertEqual(s.value(s.blend(1)),.8)
 def test_replaced_controller_rejects_edit(self):
  heart.CLIPS[(0,0)]=object()
  with self.assertRaisesRegex(ValueError,'target changed'):heart.set_manual_value(self.c,self.sl,.8)
  self.assertEqual(self.sl.cfg['manual'],.2)
