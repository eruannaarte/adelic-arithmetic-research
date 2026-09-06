"""Exact consequences of the proved directional support/dual-norm theorem."""
from fractions import Fraction as F


def strict_radius_squared(separation,negative_support,positive_support,gain_squared):
    d,hm,hp,g2=map(F,(separation,negative_support,positive_support,gain_squared))
    if d<=0 or min(hm,hp)<0 or g2<=0:raise ValueError('invalid directional contract')
    gap=d-hm-hp
    if gap<=0:raise ValueError('no strict support gap')
    return gap*gap/(4*g2)


def slab_contains(residual,negative_support,positive_support,gain_squared,noise_radius):
    value,hm,hp,g2,eta=map(F,(residual,negative_support,positive_support,gain_squared,noise_radius))
    if min(hm,hp,g2,eta)<0:raise ValueError('invalid slab contract')
    excess=value-hp if value>=0 else -value-hm
    return excess<=0 or excess*excess<=eta*eta*g2
