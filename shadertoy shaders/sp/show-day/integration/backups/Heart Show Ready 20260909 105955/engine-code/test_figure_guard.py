import copy,json,math,random,unittest
from pathlib import Path
from unittest.mock import patch
import heart,figure_guard as guard
import test_performance_motion
REAL_PUT_HTTP=heart.put_http

class GuardTests(unittest.TestCase):
 def test_transform_and_anchor_across_aspects(self):
  rng=random.Random(13)
  for w,h in [(1920,1080),(1080,1920),(1024,1024),(3840,1080)]:
   r=.46*min(w,h)
   for _ in range(100):
    t=guard.project(guard.TRANSFORM,{'Scale':rng.uniform(0,1000),'Scale W':rng.uniform(0,1000),'Scale H':rng.uniform(0,1000),'Position X':rng.uniform(-16384,16384),'Position Y':rng.uniform(-16384,16384),'Rotation Z':rng.uniform(-180,180)},w,h,r)
    tr=guard.transform_radius(t,r);m=.02*min(w,h)
    self.assertLessEqual(abs(t['Position X'])+tr,w/2-m+1e-7);self.assertLessEqual(abs(t['Position Y'])+tr,h/2-m+1e-7)
    v=guard.project(guard.CLONER,{'Start Scale':rng.uniform(0,100),'Center':rng.uniform(-1,1),'Master Rotation':rng.uniform(-180,180),'Tail Length':1},w,h,r,t)
    env=max(r,tr+math.hypot(t['Position X'],t['Position Y']))*v['Start Scale']/100;angle=math.radians(v['Master Rotation']);dist=v['Center']*w/2
    self.assertLessEqual(abs(dist*math.cos(angle))+env,w/2-m+1e-7);self.assertLessEqual(abs(dist*math.sin(angle))+env,h/2-m+1e-7);self.assertEqual(v['Tail Length'],1)
 def test_driven_center_uses_full_available_interval_without_saturation(self):
  vals=[guard.project(guard.CLONER,{'Start Scale':50,'Center':c,'Master Rotation':90},1920,1080,496.8,driven={'Center'})['Center'] for c in [-1,-.5,0,.5,1]]
  self.assertAlmostEqual(vals[3]*2,vals[4]);self.assertGreater(vals[4],vals[3])
 def test_manual_write_waits_for_coupled_projection_and_publishes_applied_values(self):
  f=test_performance_motion.EffectMotionTests();f.setUp();self.addCleanup(f.doCleanups)
  params=json.loads((Path(__file__).parent.parent/'audit/figure-transform-pilot/after-added-transform.json').read_text())['layers'][4]['video']['effects'][0]['params']
  fx=f.fx;heart.FX.clear();fx.key=guard.TRANSFORM;fx.params=copy.deepcopy(params);heart.FX[fx.key]=fx;c=fx.motion=heart.EffectMotion(fx);c.refresh(fx)
  for sl in c.slots:sl.owner='heart'
  with patch.dict(heart.FIGURE_FRAME,size=(1920,1080),radius=496.8,transform={}),patch.dict(heart.STATE,arena_connected=True):
   heart.put.reset_mock();
   with patch.object(heart.urllib.request,'urlopen') as native:
    REAL_PUT_HTTP(fx.params['Position X']['id'],16384);native.assert_not_called()
   heart.put.assert_not_called()
   rows=heart.step_motion(c,0,100,True);x=next(s for s in rows if s['name']=='Position X');actual=-16384+x['v']*32768
   self.assertLess(actual,450);self.assertGreaterEqual(actual,0);self.assertTrue(heart.put.called)
if __name__=='__main__':unittest.main()
