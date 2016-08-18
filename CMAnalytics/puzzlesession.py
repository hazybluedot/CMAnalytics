class PuzzleSession(object):
    def __init__(self):
        self.name = None
        self.start_frame = None
        self.first_active_frame = None
        self.stop_frame = None
        self.run_clicks = [] # array of Frames
        self.help_clicks = []
        self.playButton = None
        
    # @property
    # def start_frame(self):
    #     return self._start_frame
    
    # @property
    # def stop_frame(self):
    #     return self._stop_frame

    @property
    def duration(self):
        return self.stop_frame.time - self.first_active_frame.time

    @property
    def inPuzzle(self):
        return self.start_frame is not None and self.stop_frame is None

    @property
    def hasStarted(self):
        return self.start_frame is not None

    @property
    def hasEnded(self):
        return self.stop_frame is not None

    @property
    def isActive(self):
        """Puzzle is considered active when it has started and the start
window has been dismissed. Graphically, the window returns to regular
brightness. Logically isActive is determined by inPuzzle being true
AND a puzzle name is set."""
        return self.inPuzzle and self.name is not None
    
    @property
    def runClicks(self):
        return self.run_clicks

    @runClicks.setter
    def runClicks(self, frame):
        print('setting run clicks')
        pass
    
    def recordRunClick(self, frame):
        self.run_clicks.append(frame)

    def recordHelpDialog(self, frame, text):
        self.help_clicks.append((frame, text))
    
    def __str__(self):
        help_list = '\n'.join([ '\t{1}\t{0}'.format(name, frame.time) for frame, name in self.help_clicks ])
        return "Puzzle '{0}', start at {1}, finish at {2} with {3} run clicks and {4} help clicks:\n{5}".format(self.name, self.first_active_frame.time, self.stop_frame.time, len(self.run_clicks), len(self.help_clicks), help_list)

