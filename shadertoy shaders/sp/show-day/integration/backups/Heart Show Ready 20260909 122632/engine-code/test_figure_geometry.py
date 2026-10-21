import math
import unittest
from figure_geometry import constrain_transform, safe_center, clamp_center


class GeometryTests(unittest.TestCase):
    def test_scale_then_position_contains_all_z_rotations(self):
        for w,h in [(1920,1080),(1080,1920),(1024,1024)]:
            for angle in [0,30,90,179,270,725]:
                v={'Scale':900,'Scale W':700,'Scale H':100,'Position X':90000,
                   'Position Y':-90000,'Rotation Z':angle,'Rotation X':45,'Anchor X':88}
                out=constrain_transform(v,w,h,180)
                rx=180*out['Scale']*out['Scale W']/10000
                ry=180*out['Scale']*out['Scale H']/10000
                radius=max(rx,ry);margin=.02*min(w,h)
                self.assertLessEqual(abs(out['Position X'])+radius,w/2-margin+1e-8)
                self.assertLessEqual(abs(out['Position Y'])+radius,h/2-margin+1e-8)
                self.assertEqual(out['Rotation Z'],angle)
                for name in ['Rotation X','Rotation Y','Anchor X','Anchor Y','Anchor Z']:self.assertEqual(out[name],0)
                for name in ['Scale','Scale W','Scale H']:self.assertTrue(0<out[name]<=1000+1e-8)
                self.assertEqual(v['Scale'],900)

    def test_collapsed_scale_gets_resolution_relative_visible_floor(self):
        for w,h in [(1920,1080),(1080,1920),(500,500)]:
            out=constrain_transform({'Scale':0,'Scale W':0,'Scale H':0},w,h,100)
            for axis in ('Scale W','Scale H'):
                self.assertAlmostEqual(100*out['Scale']*out[axis]/10000,.04*min(w,h))

    def test_valid_pose_preserved_and_idempotent(self):
        v={'Scale':100,'Scale W':50,'Scale H':70,'Position X':20,'Position Y':-30,'Rotation Z':43}
        out=constrain_transform(v,1920,1080,100)
        for key,value in v.items():self.assertAlmostEqual(out[key],value)
        again=constrain_transform(out,1920,1080,100)
        for key in out:self.assertAlmostEqual(again[key],out[key])

    def test_center_ray_bounds_landscape_portrait_square(self):
        for w,h in [(1920,1080),(1080,1920),(1024,1024)]:
            for angle in [0,45,90,135,180,270]:
                radius=80;offset=(30,40);bound=radius+50
                lo,hi=safe_center(.8,w,h,radius,offset,angle)
                self.assertTrue(-1<=lo<=hi<=1)
                for center in (lo,hi):
                    x=center*w/2*math.cos(math.radians(angle))
                    y=center*w/2*math.sin(math.radians(angle))
                    self.assertLessEqual(abs(x)+bound,w/2-.02*min(w,h)+1e-8)
                    self.assertLessEqual(abs(y)+bound,h/2-.02*min(w,h)+1e-8)
                self.assertEqual(clamp_center(2,w,h,radius,offset,angle),hi)

    def test_center_nofit_and_invalid_inputs(self):
        self.assertIsNone(safe_center(0,100,100,49))
        self.assertIsNone(clamp_center(0,100,100,49))
        for dimensions in [(0,100),(-100,100),(float('nan'),100)]:
            with self.assertRaises(ValueError):constrain_transform({},*dimensions,10)
        with self.assertRaises(ValueError):constrain_transform({},100,100,0)
        with self.assertRaises(ValueError):safe_center(float('inf'),100,100,10)


if __name__=='__main__':unittest.main()
