import cv2
import numpy as np
from itertools import tee, cycle
from operator import attrgetter
from shapely.geometry import Polygon

def pts2Poly(pts):
    return Polygon([ pt[0] for pt in pts ])

class Rectangle:
    @staticmethod
    def _boundingRect2rectangle(rect):
        """converts points in boundingRect coordinates (pt1, delta) to
rectangle coordinates (pt1, pt2)"""
        return rect[0:2], (rect[0]+rect[2], rect[1]+rect[3])

    def __init__(self, shape):
        try:
            contour = shape.contour
        except AttributeError:
            contour = shape
        finally:
            try:
                #print('trying to get boundingRect of {0}'.format(contour))
                #print('getting bounding rectangle')
                rect = cv2.boundingRect(contour)
                #print('{1} methods: {0}'.format(dir(rect), type(rect)))
                rect =  self._boundingRect2rectangle(rect)
            except TypeError as e:
                self.pt1, self.pt2 = shape
            else:
                self.pt1, self.pt2 = rect

    @property
    def delta(self):
        return (self.pt2[0]-self.pt1[1], self.pt2[1]-self.pt1[1])

    def __iter__(self):
        yield self.pt1
        yield self.pt2

    def __getitem__(self, i):
        return [self.pt1, self.pt2][i]

    @property
    def contour(self):
        return np.array([
            [[self.pt1[0], self.pt1[1]]],
            [[self.pt1[0], self.pt2[1]]],
            [[self.pt2[0], self.pt2[1]]],
            [[self.pt2[0], self.pt1[1]]]
        ])

    def draw(self, img, *args, **kwargs):
        cv2.rectangle(img, self.pt1, self.pt2, *args, **kwargs)

def shapeFilter(attr, op, val):
    def _wrapper(shape):
        return op(getattr(shape, attr), val)
    return _wrapper

def empty():
    # an empty iterator
    # see http://stackoverflow.com/questions/13243766/python-empty-generator-function
    return
    yield

def findContours(frame, *args, **kwargs):
    """Find contours for frame image"""

    mode = kwargs.get('mode', cv2.RETR_TREE)
    threshold = kwargs.get('threshold', 127)
    
    def morphReducer(img, (op, kernel)):
        res = cv2.morphologyEx(img, op, kernel)
        return res

    #print('frame pre threshold: {0}'.format(frame))
    ret, thresh = cv2.threshold(frame.gray, threshold, 255, cv2.THRESH_BINARY)
    #print('frame post threshold: {0}'.format(frame))
    #print('frame.gray {0}'.format(frame.gray))
    #print('ret, thresh: {0}, {1}'.format(ret, thresh))
    #cv2.imshow('premorph thresh', thresh)
    #print('morphing with {0}'.format(kwargs.get('morph', [])))
    thresh = reduce(morphReducer, kwargs.get('morph', []), thresh)
    #cv2.imshow('postmorph thresh', thresh)
    #cv2.waitKey(0)

    im, contours, hierarchy = cv2.findContours(thresh, mode, cv2.CHAIN_APPROX_SIMPLE, None, None, frame.offset)

    return Contours(frame, im, contours, hierarchy)

class Contours:
    def __init__(self, frame, im2, contours, hierarchy):
        self.frame = frame
        self.im2 = im2
        self.contours = contours
        self._hierarchy = hierarchy
            
    @property
    def hierarchy(self):
        return self._hierarchy[0]
    
    def __len__(self):
        return self.contours.__len__()
    
    def __repr__(self):
        return "<Contours frame='{0}' {1} contours>".format(self.frame, self.contours.__len__())
        
    class Shape():
        def __init__(self, parent, idx, **kwargs):
            self.parent = parent
            self.idx = idx
            self.frame = parent.frame
            self.epsilon = kwargs.get('epsilon', 0.05)

        def __repr__(self):
            return "<Contour idx='{0}' parent='{1}'>".format(self.idx, self.parent)

        @property
        def contour(self):
            return self.parent.contours[self.idx]
        
        @property
        def siblings(self, **kwargs):
            return self._sibling_iterator(**kwargs)

        @property
        def children(self, **kwargs):
            child_idx = self.parent.hierarchy[self.idx,2]
            if child_idx >=0:
                child = self.parent._shapeForIndex(child_idx)
                return child.siblings
            return empty()
                    
        def _sibling_iterator(self, **kwargs):
            return self.parent._sibling_iterator(self.idx, **kwargs)
                
        @property
        def arcLength(self):
            return cv2.arcLength(self.contour, True)

        @property
        def area(self):
            return int(cv2.contourArea(self.contour))

        @property
        def normalizedArea(self):
            return self.area/float(self.frame.area)
            #try:
            #    return float(self.area)/self.arcLength
            #except ZeroDivisionError:
            #    return 0
            
        @property    
        def approx(self):
            return cv2.approxPolyDP(self.contour, self.epsilon*self.arcLength, True)

        @property
        def corners(self):
            return len(self.approx)

        @property
        def hull(self):
            return cv2.convexHull(self.contour)

        @property
        def convexityDefects(self):
            return cv2.convexityDefects(self.contour, self.hull)
        
        @property
        def boundingRect(self):
            return Rectangle(self)
        
        @property
        def color(self):
            return self._color

        @property
        def aspect_ratio(self):
            """The ratio of width to height of bounding rect of the object."""
            x,y,w,h = cv2.boundingRect(self.contour)
            return float(w)/h

        @property
        def rect_area(self):
            x,y,w,h = cv2.boundingRect(self.contour)
            return w*h
            
        @property
        def extent(self):
            """Extent is the ratio of contour area to bounding rectangle area."""
            return float(self.area)/self.rect_area

        @property
        def equi_diameter(self):
            """Equivalent Diameter is the diameter of the circle whose area is same as the contour area."""
            return np.sqrt(4*self.area/np.pi)

        def poly(self, getter=attrgetter('contour')):
            return pts2Poly(self.contour)

        @color.setter
        def color(self, color):
            self._color = color

        def hls(self, frame):
            mask = np.zeros(frame.shape[0:2], np.uint8)
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HLS_FULL)
            cv2.drawContours(mask, [self.approx], 0, 255, -1)
            return cv2.mean(hsv, mask)

        def draw(self, img, color, *args, **kwargs):
            #cv2.drawContours(img, self.parent.contours, self.idx, color, *args, **kwargs)
            #print('drawing hierarchy starting from index {0}'.format(self.idx))
            self.parent._drawHierarchy(img, self.parent.hierarchy[self.idx,2], color, *args, **kwargs)

    def _shapeForIndex(self, idx, **kwargs):
        return self.Shape(self, idx, **kwargs)

    def __iter__(self):
        return self.iterate()

    def _level_iterator(self, idx, level):
        i = idx
        while i >= 0:
            #print('yielding shape {0} at level {1}'.format(i, level))
            yield (level, self._shapeForIndex(i))
            j = self.hierarchy[i,2]
            while j >= 0:
                for l, item in self._level_iterator(j, level+1):
                    yield (l, item)
                j = self.hierarchy[j,0]
            i = self.hierarchy[i,0]
            
    def level_iterator(self):
            return self._level_iterator(0,0)
                   
    def iterate(self, **kwargs):
        for i, c in enumerate(self.contours):
            yield self.Shape(self, i)
                
    def _sibling_iterator(self, idx, **kwargs):
        i = idx
        while i >= 0:
            yield self._shapeForIndex(i, **kwargs)
            i = self.hierarchy[i,0]
            
    def groups(self, **kwargs):
        """iterate over sibling iterators for each level of the hierarchy"""
        i = 0
        yield self._sibling_iterator(i, **kwargs)
        while i >=0:
            yield self._sibling_iterator(self.hierarchy[i,2], **kwargs)
            i = self.hierarchy[i,0]
            
    def top_level(self, **kwargs):
        return next(self.groups(**kwargs))
    
    def _drawHierarchy(self, img, idx, colors=cycle([(0,0,255),(0,255,255),(255,0,0)]), *args, **kwargs):
        _filter = kwargs.get('filter', None)
        i = idx
        try:
            level_color = colors.next()
        except AttributeError:
            level_color = colors
        external_color = kwargs.get('external_color', level_color)
        hole_color = kwargs.get('hole_color', level_color)
        shape_selector = kwargs.get('shape_selector', attrgetter('contour'))
        contours = [ shape_selector(shape) for shape in self ]
        while i >= 0:
            if _filter is None or _filter(self._shapeForIndex(i)):
                cv2.drawContours(img, contours, i, level_color, 2)
                
            j = self.hierarchy[i,2]
            while j >=0:
                if _filter is None or _filter(self._shapeForIndex(j)):
                    cv2.drawContours(img, contours, j, external_color, 1)
                self._drawHierarchy(img, self.hierarchy[j,2], colors, **kwargs)
                j = self.hierarchy[j,0]
            i = self.hierarchy[i,0]
            
    def drawHierarchy(self, img, colors=cycle([(0,0,255),(0,255,255),(255,0,0)]), *args, **kwargs):
        if kwargs.get('grayscale', False):
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        self._drawHierarchy(img, 0, colors, *args, **kwargs)
        #cv2.drawContours(img, self.contours, -1, (0,0,255), 2, cv2.LINE_8, self._hierarchy, 2)

colors = [ (0,0,255), (0,255,0), (0,255,255) ]

if __name__ == '__main__':
    import sys
    from itertools import cycle
    import timeit
    
    files = sys.argv[1:]
    kernel = np.ones((2,2),np.uint8)

    for i, f in enumerate(files):
        img = cv2.imread(f, cv2.IMREAD_COLOR)
        contours = Contours(img,
                            threshold=120,
                            dilation=kernel,
                            retrieval_mode=cv2.RETR_TREE)

        first = iter(contours).next()
        #output = img.copy()
        output = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        output = cv2.cvtColor(output, cv2.COLOR_GRAY2BGR)
        output = output * 0.25
        output1 = output.copy()
        cit0 = iter(cycle(colors))
        cit1 = iter(cycle(colors))

        cv2.imwrite('thresh0_{0}.png'.format(contours.threshold), contours.thresh)
        for iGroup,group in enumerate(contours.groups()):
            img2 = cv2.cvtColor(contours.thresh, cv2.COLOR_GRAY2BGR)
            cv2.drawContours(img2, [ g.contour for g  in group ], -1, (0,255,0),1)
            cv2.imwrite('contours_{0}_group_{1}.png'.format(i,iGroup), img2)
