#!/usr/bin/env python
from itertools import ifilter

from CMAnalytics import PuzzleSession
from CMAnalytics.uievents import hasStartDialog, hasStopDialog, findHelpDialog, findPlayButton, isPlaying
from CMAnalytics.util import extractPuzzleName
from CMAnalytics.video import isLight
from CMAnalytics import open_video

def everyN(n):
    return lambda frame: 0 == frame.number % n

class TransitionEvent(object):
    def __init__(self, fn):
        self.last_state, self.current_state = None, None
        self.fn = fn
        
    def __call__(self, *args, **kwargs):
        self.last_state, self.current_state = self.current_state, self.fn(*args, **kwargs)
        return self.last_state != self.current_state, self.current_state
    
def puzzleSession(cap):
    puzzle = PuzzleSession()
    
if __name__ == '__main__':
    from sys import argv, exit

    playChange = TransitionEvent(isPlaying)
    helpChange = TransitionEvent(lambda f: findHelpDialog(f)[1])
    
    with open_video(argv[1]) as cap:
        puzzle = PuzzleSession()

        # or
        puzzle.start_frame = next(
            ( frame for frame in ifilter(everyN(10), cap) if hasStartDialog(frame) )
        )

        if not puzzle.hasStarted:
            print('finished video with no start dialog')
            exit(0)

        first_active_frame = next (
            ( frame for frame in ifilter(everyN(10), cap) if isLight(frame) )
        )
        puzzle.first_active_frame = first_active_frame
        puzzle.name = extractPuzzleName(first_active_frame)
        puzzle.playButton, contours = findPlayButton(first_active_frame)
        
        while(puzzle.isActive):
            frame = next(ifilter(everyN(10), cap))

            play_transitioned, is_playing = playChange(frame, puzzle.playButton)

            # TODO: don't check for help immediately after a help dialog was found
            # to help prevent jittering due to OCR errors on subsequent frames
            
            if len(puzzle.help_clicks)==0 or frame.time - puzzle.help_clicks[-1][0].time > 3:
                try:
                    pass
                    #print('time since last help click: {0}'.format(frame.time - puzzle.help_clicks[-1][0].time))
                except IndexError:
                    pass
                
                change, text = helpChange(frame)
                if change and text is not None:
                    puzzle.recordHelpDialog(frame, text)
                
            if play_transitioned and is_playing:
                puzzle.recordRunClick(frame)
                #puzzle.runClicks += frame
                
            if hasStopDialog(frame):
                puzzle.stop_frame = frame

        print(puzzle)
        
