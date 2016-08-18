#!/usr/bin/env python
import sys
sys.path.append('../') 
import cv2
from operator import attrgetter
import numpy as np

from CMAnalytics import open_video
from CMAnalytics.uievents import findPlayButton, playButtonState

def colorByCorners(s):
    if s.corners == 4:
        return (0,0,255)
    if s.corners == 3:
        return (0,255,255)
    return (255,255,0)

if __name__ == '__main__':
    from sys import argv

    playButton = None
    this_state = None
    with open_video(argv[1]) as cap:
        print('FPS: {}'.format(cap.fps))

        for frame in cap:
            gray = cv2.cvtColor(frame.gray, cv2.COLOR_GRAY2BGR)

            #cv2.imshow('frame',gray)

            if playButton is None:
                playButton, contours = findPlayButton(frame)
                for c in contours:
                    cv2.drawContours(gray, [c.approx], 0, colorByCorners(c), 2)
                    #contours.drawHierarchy(gray, (255,255,0), 2)
            else:
                prev_state, this_state = this_state, playButtonState(frame, playButton)
                if this_state != prev_state:
                    print('play state transition to {0} at {1}'.format(this_state, frame.time))

                colorByState = { 'play_hover': (0,255,0), 'play_nohover': (0,220,50), 'hover': (0,255,255), 'nohover': (0,0,255) }
                rect = playButton.boundingRect
                rect.draw(gray, colorByState[this_state], 2)

            cv2.imshow('frame', gray)
            cv2.waitKey(10)
