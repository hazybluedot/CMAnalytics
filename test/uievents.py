#!/usr/bin/env python

import cv2
from itertools import ifilter, cycle

from CMAnalytics import open_video
from CMAnalytics.uievents import *
from CMAnalytics.util import extractPuzzleName

if __name__ == '__main__':
    from sys import argv
    import cProfile
    
    colors = [ (0,255,0), (0,0,255), (0,255,255) ]

    playButton = None
    start_frame = None
    stop_frame = None
    this_state = None
    help_popup = None
    with open_video(argv[1]) as cap:
        print('FPS: {}'.format(cap.fps))
        
        for frame in ifilter(lambda frame: 0 == frame.number % 15, cap):
            canvas = cv2.cvtColor(frame.gray, cv2.COLOR_GRAY2BGR)
            waitTime = 1
            if start_frame is None:
                start_frame = findStartDialog(frame)
                if start_frame is not None:
                    print('start frame: {0}'.format(start_frame[0].parent))
                    #cv2.imwrite('start_frame.png', frame.img)
                    #waitTime = 1000

            if start_frame is not None and playButton is None:
                for contour in start_frame:
                    cv2.drawContours(canvas, [contour.contour], 0, (0,255,255), 2)
                    
            if start_frame is not None and playButton is None:
                #print('searching for play button')
                playButton, playButtonContours = findPlayButton(frame)
                name = extractPuzzleName(frame)
                if name is not None:
                    print('puzzle name: {0}'.format(name))
                    
            if playButton is not None:    
                prev_state, this_state = this_state, playButtonState(frame, playButton)
                if this_state != prev_state:
                    print('play state transition to {0} at {1}'.format(this_state, frame.time))

                colorByState = { 'play_hover': (0,255,0),
                                 'play_nohover': (0,250,50),
                                 'hover': (0,255,255),
                                 'nohover': (0,0,255) }
                
                rect = playButton.boundingRect
                rect.draw(canvas, colorByState[this_state], 2)

                help_popup, text = findHelpDialog(frame)
                if help_popup is not None:
                    print("help dialog for '{0}' at {1}".format(text, frame.time))
            if start_frame is not None and stop_frame is None:
                stop_contours = findStopDialog(frame)
                if stop_contours is not None:
                    stop_frame = frame
                    print('stop frame: {0}'.format(frame))

            #cv2.imshow('live preview', canvas)
            #cv2.waitKey(waitTime)
