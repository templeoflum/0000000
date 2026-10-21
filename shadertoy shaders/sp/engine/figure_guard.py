"""Frame-relative operating bounds for the Figure's native controls.

Pure projection of existing Smart Param output, not a new motion generator.
Caller must own all coupled numeric controls. The cloner branch covers a static,
forward, unwarped first copy; upstream expansion is explicitly reported separately.
"""
import math
import figure_geometry as geometry

TRANSFORM='layer/figure~1/effect/Transform~1'
CLONER='layer/figure~1/effect/LinearCloner~1'
KEYS=(TRANSFORM,CLONER)


def transform_radius(values,radius):
    return radius*values.get('Scale',100)*max(values.get('Scale W',100),values.get('Scale H',100))/10000


def project(key,values,w,h,source_radius,transform=None,driven=()):
    if key==TRANSFORM:
        out=geometry.constrain_transform(values,w,h,source_radius)
        radius=transform_radius(out,source_radius);margin=.02*min(w,h)
        for name,dimension in [('Position X',w),('Position Y',h)]:
            if name in driven:out[name]=max(-1.,min(1.,values.get(name,0)/(dimension*.45)))*max(0,dimension/2-margin-radius)
        return out
    if key!=CLONER:return dict(values)
    t=transform or {};out=dict(values);short=min(w,h)
    # Include source displacement in a circular bound, independent of whether
    # native Master Rotation rotates that displacement or only the clone axis.
    envelope=max(source_radius,transform_radius(t,source_radius)+math.hypot(t.get('Position X',0),t.get('Position Y',0)))
    cap=.48*short
    max_start=min(100.,100*cap/max(envelope,1e-9))
    min_start=min(max_start,100*.04*short/max(transform_radius(t,source_radius),1e-9))
    out['Start Scale']=max(min_start,min(max_start,values.get('Start Scale',100)))
    anchor=envelope*out['Start Scale']/100
    interval=geometry.safe_center(0,w,h,anchor,angle_degrees=out.get('Master Rotation',0))
    if interval and (values.get('Tails',1)>1 or abs(values.get('Tail Rotation',0))>1e-9):
        radial=geometry.safe_center(0,w,h,anchor,angle_degrees=90 if w>=h else 0)
        interval=(max(interval[0],radial[0]),min(interval[1],radial[1])) if radial else None
    out['Center']=(max(-1.,min(1.,out.get('Center',0)))*interval[1] if 'Center' in driven else max(interval[0],min(interval[1],out.get('Center',0)))) if interval else 0.
    # These modes can move/hide the initial copy and are outside this first guard.
    out['Distortion']=0.;out['Delay Amount']=0.
    return out


def drive_ranges(key,w,h,source_radius,transform=None):
    if key==TRANSFORM:
        cap=100*.46*min(w,h)/source_radius
        return {'Position X':(-w*.45,w*.45),'Position Y':(-h*.45,h*.45),
                'Scale':(cap*.25,cap*.8),'Rotation Z':(-180.,180.)}
    if key==CLONER:
        t=transform or {};env=transform_radius(t,source_radius)+math.hypot(t.get('Position X',0),t.get('Position Y',0))
        cap=min(100.,100*.46*min(w,h)/max(env,1e-9))
        return {'Center':(-1.,1.),'Start Scale':(cap*.35,cap),'Tail Length':(-1.,1.),'Master Rotation':(-180.,180.)}
    return {}
