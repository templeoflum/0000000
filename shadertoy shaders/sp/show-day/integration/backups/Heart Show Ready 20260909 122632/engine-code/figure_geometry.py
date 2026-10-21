"""Conservative 2D containment for a known circular source bound in pixels.

Native percentage scale multiplies as Scale*ScaleW/H/10000. We reserve a 2%
short-side margin and seek a visible radius >=4% of the short side, reducing that
floor if the frame cannot fit it. This is a pixel-based floor, not a fixed 5%
native scale: the latter does not account for source radius or frame resolution.
X/Y perspective rotation and anchors stay zero until their projection is verified.
These helpers do not apply to unknown source bounds or unbounded effect stacks.
"""
import math


def _finite(value, name):
    value=float(value)
    if not math.isfinite(value):raise ValueError(name+' must be finite')
    return value


def _frame(w, h):
    w=_finite(w,'width');h=_finite(h,'height')
    if w<=0 or h<=0:raise ValueError('Frame dimensions must be positive')
    short=min(w,h);margin=.02*short
    return w/2-margin,h/2-margin,short


def constrain_transform(values, w, h, source_radius):
    """Fit scale first, then position; preserve unrestricted 2D Rotation Z.

    Nonuniform scales use their largest radius as a circular envelope, so every Z
    rotation remains contained. Requested aspect ratios are retained except where
    a near-zero axis would violate the minimum-visible-radius floor.
    """
    halfw,halfh,short=_frame(w,h)
    radius=_finite(source_radius,'source radius')
    if radius<=0:raise ValueError('Source radius must be positive')
    out=dict(values)
    scale=max(0.,_finite(values.get('Scale',100.),'Scale'))
    sw=max(0.,_finite(values.get('Scale W',100.),'Scale W'))
    sh=max(0.,_finite(values.get('Scale H',100.),'Scale H'))
    cap=min(halfw,halfh);floor=min(.04*short,cap)
    rx=radius*scale*sw/10000.;ry=radius*scale*sh/10000.
    if not math.isfinite(rx+ry):raise ValueError('Scale product must be finite')
    largest=max(rx,ry)
    if largest>cap:
        factor=cap/largest;rx*=factor;ry*=factor;scale*=factor
    rx=max(floor,rx);ry=max(floor,ry)
    # Factor the constrained physical scales into valid 0..1000 native controls.
    # Existing master scale is retained whenever it can represent both axes.
    required=max(rx,ry)/radius*10.
    if required>1000.:raise ValueError('Source radius too small for native scale range')
    master=min(1000.,max(scale,required,1e-12))
    out.update({'Scale':master,'Scale W':rx/radius*10000./master,
                'Scale H':ry/radius*10000./master})
    envelope=max(rx,ry)
    for name,limit in [('Position X',halfw-envelope),('Position Y',halfh-envelope)]:
        position=_finite(values.get(name,0.),name)
        out[name]=max(-limit,min(limit,position))
    out['Rotation Z']=_finite(values.get('Rotation Z',0.),'Rotation Z')
    for name in ('Rotation X','Rotation Y','Anchor X','Anchor Y','Anchor Z'):out[name]=0.
    return out


def safe_center(center, w, h, anchor_radius, offset=(0.,0.), angle_degrees=0.):
    """Return the safe native Linear Cloner Center interval, or None if no fit.

    Center moves by center*width/2 along Master Rotation, independently of Tail
    Length. Offset orientation is deliberately not assumed: its norm enlarges
    the circular anchor bound, covering either rotated or unrotated offset.
    This protects only the bounded anchor instance, not the other tail clones.
    The center argument is validated but does not change the permissible interval.
    """
    _finite(center,'center');halfw,halfh,_=_frame(w,h)
    radius=_finite(anchor_radius,'anchor radius')
    if radius<0:raise ValueError('Anchor radius cannot be negative')
    ox=_finite(offset[0],'offset x');oy=_finite(offset[1],'offset y')
    envelope=radius+math.hypot(ox,oy)
    available=(halfw-envelope,halfh-envelope)
    if min(available)<0:return None
    angle=math.radians(_finite(angle_degrees,'angle'))
    direction=(math.cos(angle)*float(w)/2,math.sin(angle)*float(w)/2)
    limit=1.
    for extent,component in zip(available,direction):
        if abs(component)>1e-12:limit=min(limit,extent/abs(component))
    return (-limit,limit)


def clamp_center(center, w, h, anchor_radius, offset=(0.,0.), angle_degrees=0.):
    """Clamp to safe_center's interval; return None when the anchor cannot fit."""
    interval=safe_center(center,w,h,anchor_radius,offset,angle_degrees)
    return None if interval is None else max(interval[0],min(interval[1],float(center)))
