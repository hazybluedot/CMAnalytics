from operator import attrgetter
from shapely.geometry import Polygon

from CMAnalytics.util import pairwise

def pts2Poly(pts):
    return Polygon([ pt[0] for pt in pts ])

def intersect(contours, *args, **kwargs):
    """p1 intersections with p2 AND p2 intersects with p3 AND p3 ... """

    try:
        shape_attr, poly_attr = args[0]
    except IndexError:
        polyattr = kwargs.get('polyattr', attrgetter('intersects'))
        getter = kwargs.get('getter', attrgetter('hull'))
    else:
        polyattr = attrgetter(poly_attr)
        getter = attrgetter(shape_attr)

    polygons = [ pts2Poly(getter(contour)) for contour in contours ]
    chain = [ polyattr(p1)(p2) for p1, p2 in pairwise(polygons) ]
    return all(chain)
