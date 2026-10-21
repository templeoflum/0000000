"""Provisional Open recipes, pending visual checks across input images.

These configure existing Smart Params only. They do not clamp output or restrict
manual controls, and do not alter timing, phase, or the native effect schema.
"""
from urllib.parse import unquote


def settings(effect_key, parameter, pose, limits=(0., 1.)):
    """Return only the configuration changes needed for an Open gesture."""
    native = unquote((effect_key or '').rsplit('/effect/', 1)[-1].rsplit('~', 1)[0])
    if native == 'Transform':
        # Native framing ranges can move the entire image far outside the canvas.
        # Keep the current pose until source-aware exploration bounds are verified.
        return {'drive': False, 'manual': pose}
    if native in ('LinearCloner', 'RadialCloner'):
        if parameter in ('Clones', 'Tails', 'Delay Amount'):
            return {'drive': False, 'manual': pose}
        if parameter in ('Start Scale', 'End Scale'):
            limits = (.2, 1.)
    elif native == 'Iterate':
        if parameter in ('StartOpacity', 'OpacityChange', 'DOpacityChange'):
            return {'drive': False, 'manual': 1.}
        if parameter in ('TransformStrength', 'Iterations'):
            limits = (.1, .35)
        elif parameter == 'GRotateZ':
            limits = (0., 1.)
        else:
            return {'drive': False, 'manual': pose}
    return {'drive': True, 'lo': limits[0], 'hi': limits[1], 'lock': False}
