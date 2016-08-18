import cv2
import numpy as np
from operator import attrgetter
from itertools import combinations, product, ifilter

from CMAnalytics.util import pairwise, extractText
from CMAnalytics.contours import findContours, intersect

def isWhite(hls):
    return hls[1] > 220 and hls[2] < 50

def isGreen(hls):
    return hls[0] > 40 and hls[0] < 55 and hls[2] > 127

def findStartDialog(frame, **kwargs):
    def startFilter(shape):
        return shape.corners == 4 and shape.normalizedArea >= 0.005
    gray = frame.gray # kwargs.get('gray', cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    mask = frame.mask # kwargs.get('mask', np.zeros(gray.shape, np.uint8))
    
    contours = findContours(frame, threshold=127, mode=cv2.RETR_CCOMP)
    #contours = Contours(frame, threshold=127, retrieval_mode=cv2.RETR_CCOMP)

    top = contours.top_level(epsilon=0.02)

    canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) 
    #cv2.drawContours(canvas, [ c.hull for c in filter(startFilter, top) ], -1, (0,0,255), 2)
    #cv2.imshow('start contours', canvas)
    #cv2.waitKey(0)
    
    for pair in (pair for pair in combinations(ifilter(startFilter, top), 2)
                 if intersect(pair, ('hull', 'intersects')) ):
        
        smaller, bigger = sorted(pair, key=lambda shape: shape.area)
        ratio = bigger.area/smaller.area

        if ratio > 10 and ratio < 15:
            for shape in [bigger,smaller]:
                mask[...]=0
                cv2.drawContours(mask,[shape.approx], 0, 255, -1)
                shape.color = cv2.mean(frame.img, mask)

            if isWhite(bigger.hls(frame.img)) and isGreen(smaller.hls(frame.img)):
                return pair
            
    return None

def findStopDialog(frame,  **kwargs):
    def stopFilter(shape):
        return shape.corners == 4 and shape.normalizedArea >= 0.01 and shape.normalizedArea < 0.2
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    
    contours = findContours(frame, threshold=122,
                            mode=cv2.RETR_TREE,
                            morph=[(cv2.MORPH_DILATE, kernel)],
                            **kwargs)

    level_group = filter(stopFilter, contours.top_level())

    for triple in (triple for triple in combinations(level_group, 3)
                   if intersect(triple, ('hull', 'intersects'))):        
        triple = sorted(triple, key=lambda shape: shape.area)

        ## Possible to look for 'official solution' text, but OCR is
        ## relatively expensive, an order of magnitude slower than the
        ## arrangement check
        
        #frame.roi = triple[0].boundingRect
        #text = extractText(frame)
        #print('got text: {0}'.format(text))
        #if text.lower() == 'official solution':
        #    return triple

        corners = [ pt1 for pt1, pt2 in map(attrgetter('boundingRect'), triple) ]

        # stop screen boxes are aranged top down from biggest to smallest
        if corners != sorted(corners, key=lambda x: -x[1]):
            return None

        ratio1, ratio2 = [ c1.area / float(c2.area) for c1, c2 in pairwise(triple) ]
        ## Magic numbers are bad practice, maybe these belong in a config file. They
        ## were determined by printing the ratio out and running the
        ## algorithm on a image containing the stop dialog
        #print('ratios: {0}'.format((ratio1,ratio2)))
        if 0.74 <= ratio1 <= 0.76 and 0.20 <= ratio2 <= 0.21:
            return triple

def findHelpDialog(frame, **kwargs):
    def gotItFilter(s):
        return s.normalizedArea > 0.005 and s.normalizedArea < 0.1 and s.corners == 4
    def dialogFilter(s):
        return s.normalizedArea > 0.1 and s.normalizedArea < 0.2 and s.corners >= 8

    kernel = [cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))]
    method = [cv2.MORPH_OPEN]

    contours = findContours(frame, threshold=180, mode=cv2.RETR_TREE, morph=zip(method, kernel))
    
    #canvas = cv2.cvtColor(frame.gray, cv2.COLOR_GRAY2BGR)
    #contours.drawHierarchy(canvas)
    
    #                                            lambda s: s.corners==8
    poly8 = filter(dialogFilter, contours.top_level(epsilon=0.01))
    poly4 = filter(gotItFilter, contours.top_level(epsilon=0.05))

    #print('cartesian product of {0} item and {1} item'.format(len(poly8), len(poly4)))
    for p1,p2 in [ (p1,p2) for p1,p2 in product(poly8, poly4) ]: #if intersect((p1,p2)) ]
        # if p1, the larger of the two, has a
        children = filter(lambda x: x.area/float(p1.area) > 0.02, p1.children)
        if len(children) == 2:
            smaller = min(children, key=lambda c: c.area)
            roi = frame.subFrame(smaller.boundingRect)
            newroi = (tuple(np.array(roi.roi[0])+np.array((2,2))), np.array(roi.roi[1])-np.array((2,4)))
            roi.roi = newroi
            #ret, broi = cv2.threshold(roi.gray, 164, 255, cv2.THRESH_BINARY)

            morph=[
                (cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2))),
                #(cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2)))
            ]
            contours = findContours(roi, threshold=164, mode=cv2.RETR_TREE, morph=morph)
            #broi = cv2.morphologyEx(broi, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2,2)))
            #im2, contours, h = cv2.findContours(broi.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            
            textcanvas = np.zeros(roi.gray.shape, np.uint8)
            textcanvas = roi.gray
            text = extractText(textcanvas, **kwargs)
            return p1, text

            # # so as it turns out, I have gotten better results by
            # # simply giving the grayscale image to tesseract. I will
            # # leave this convoluted re-drawing of letters routine for
            # # prosperity, since I dumped a whole afternoon into it.

            # offset = tuple(-1*np.array(roi.offset))

            # # to get better OCR results we find the outer contour of each letter, fill it with white,
            # # then fill each of the holes (children of letter contours) with white
            # letters = filter(lambda (l,c): l==2, contours.level_iterator())
            # for l,c in letters:
            #     cv2.drawContours(textcanvas, [c.contour], 0, 255, -1, cv2.LINE_8, None, -1, offset)
            #     for child in c.children:
            #         cv2.drawContours(textcanvas, [child.contour], 0, 0, -1, cv2.LINE_8, None, -1, offset)
            # text = extractText(textcanvas, **kwargs)
            # return p1, text

    return None, None

def hasStartDialog(frame, **kwargs):
    return findStartDialog(frame, **kwargs) is not None

def hasStopDialog(frame, **kwargs):
    return findStopDialog(frame, **kwargs) is not None
