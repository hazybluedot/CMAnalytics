#!/usr/bin/env python

import sys

sys.path.append('../') 
import cv2
from operator import attrgetter
import numpy as np

from CMAnalytics import Frame
from CMAnalytics.uievents import findHelpDialog
from CMAnalytics.puzzleName import extractText

def helpDialogFilter(shape):
    return shape.corners <= 8 and shape.area >= 1000

def colorForCorners(p):
    if p.corners >= 15:
        return (255,255,0)
    if p.corners == 14:
        return (10,250,250)
    if p.corners == 4:
        return (250,10,250)
    return (0,0,128)

def colorForArea(p):
    if p.normalizedArea >= 100:
        return (10,250,250)
    if p.normalizedArea >= 50:
        return (250,10,250)
    if p.normalizedArea >= 25:
        return (255,255,0)
    return (0,0,128)

if __name__ == '__main__':
    from sys import argv
    import cProfile, pstats, StringIO

    pr = cProfile.Profile()
    sortby = 'cumulative'
    
    for fname in argv[1:]:
        frame = Frame(cv2.imread(fname))

        canvas = cv2.cvtColor(frame.gray, cv2.COLOR_GRAY2BGR)

        pr.enable()
        dialogContour, text = findHelpDialog(frame, filter=helpDialogFilter)
        pr.disable()

        s = StringIO.StringIO()
        with open('{0}.stats'.format(fname), 'w') as s:
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()

        print('{0} help dialog: {1}'.format(fname, text))
        #cv2.imshow(fname, canvas)
        #cv2.waitKey(0)
        #pr.dump_stats('{0}.profile'.format(fname))
        #sortby = 'cumulative'
        #ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
