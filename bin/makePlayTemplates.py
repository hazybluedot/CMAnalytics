#!/usr/bin/env python
import sys
sys.path.append('../') 

import cv2
from CMAnalytics.video import Frame
from CMAnalytics.uievents import findPlayButton

if __name__ == '__main__':
    from sys import argv

    file_order = [ 'nohover', 'hover', 'play_hover', 'play_nohover']
    playButton = None
    for state, fname in zip(file_order, argv[1:]):
        frame = Frame(cv2.imread(fname))

        if state == 'nohover':
            playButton, contours = findPlayButton(frame)
            if playButton is None:
                raise Exception("Could not find play button in '{0}'".format(fname))

        frame.roi = playButton.boundingRect
        print('making template for {0}'.format(state))
        cv2.imwrite('template_{0}.png'.format(state), frame.img)
