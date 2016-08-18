import cv2
import numpy as np
from operator import mul

def isLight(frame):
    return frame.gray.mean() >= 120
            
class Frame(object):
    def __init__(self, img, cap=None, **kwargs):
        self.cap = cap
        self.parent = kwargs.get('parent', None)
        self.roi = kwargs.get('roi', None)
        
        self._img = img
        if cap is not None:
            self._ret = None
            self._time = cap.get(cv2.CAP_PROP_POS_MSEC)/1000.0
            self.number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        else:
            self._ret = 'still'
        self._gray = None

    def _retreive(self):
        self._ret, self._img = self.cap.retrieve()
        if self.roi is None:
            yRange, xRange = self._img.shape[:2]
            self.roi = ( (0,0), (xRange,yRange) )

    def _retreiveIfNecessary(self):
        if not self.retreived:
            self._retreive()
        
    @property
    def roi(self):
        return self._roi

    @roi.setter
    def roi(self, roi):
        if roi is None:
            self._roi = None
        else:    
            try:
                pt1, pt2 = roi
            except TypeError as e:
                raise TypeError('{0} not valid ROI. Must be unpackable into two points, e.g.  `pt1, pt2 = roi`'.format(roi))
            else:
                self._roi = roi
            
    @property
    def img(self):
        self._retreiveIfNecessary()
        if self.roi is None:
            return self._img
        else:
            pt1, pt2 = self.roi
            return self._img[pt1[1]:pt2[1], pt1[0]:pt2[0]]

    @property
    def gray(self):
        self._retreiveIfNecessary()
        if self._gray is None:
            self._gray = cv2.cvtColor(self._img, cv2.COLOR_BGR2GRAY)

        if self.roi is None:
            return self._gray
        else:
            pt1, pt2 = self.roi
            return self._gray[pt1[1]:pt2[1], pt1[0]:pt2[0]]

    @property
    def offset(self):
        if self.roi is None:
            return (0,0)
        else:
            pt1, pt2 = self.roi
            return (pt1[0], pt1[1])
    
    @property
    def time(self):
        return self._time
    
    @property
    def retreived(self):
        return self._ret is not None
    
    @property
    def mask(self):
        return np.zeros(self.gray.shape, np.uint8)

    def subFrame(self, roi):
        return Frame(self._img, self.cap, roi=roi)

    @property
    def area(self):
        return mul(*self.img.shape[:2])
        
    def __repr__(self):

        retreive_stat = 'still'
        if self._ret == 'still':
            retreive_state = 'still'
        elif self.retreived:
            retreive_state = 'retreived'
        else:
            retreive_state = 'not retreived'
            
        if self.cap is not None:
            cap_stat = 'number={0}, time={1}'.format(self.number, self.time)
        else:
            cap_stat = ''
            
        # shape statistics
        if self._ret == 'still' or self.retreived:
            shape = 'shape={0}'.format(self._img.shape)
        else:
            shape = ''

        if self.roi is not None:
            roi_stat = 'roi={0}'.format(self.roi)
        else:
            roi_stat = ''
            
        return '<Frame {shape} {roi} {cap_state} ({retreived})>'.format(shape=shape,
                                                                       roi=roi_stat,
                                                                       cap_state=cap_stat,
                                                                       retreived=retreive_state)
