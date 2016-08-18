#!/usr/bin/env python

import cv2

import sys
sys.path.append('../') 

from CMAnalytics import Frame
from CMAnalytics.uievents import puzzleStartDialog, puzzleStopDialog
                
if __name__ == '__main__':
    from sys import argv
    import cProfile, pstats, StringIO

    pr = cProfile.Profile()
    sortby = 'cumulative'

    for fname in argv[1:]:
        frame = Frame(cv2.imread(fname))

        canvas = cv2.cvtColor(frame.gray, cv2.COLOR_GRAY2BGR)

        pr.enable()
        ret = puzzleStopDialog(frame)
        pr.disable()

        if ret is not None:
            for c in ret:
                cv2.drawContours(canvas, [c.hull], 0, (0,0,255), 2)
            cv2.imshow('found stop dialog', canvas)
            cv2.waitKey(0)
            
        print('{0} has stop dialog: {1}'.format(fname, ret is not None))
        
        s = StringIO.StringIO()
        with open('{0}.stats'.format(fname), 'w') as s:
            ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
            ps.print_stats()

