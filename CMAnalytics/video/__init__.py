import cv2
from frame import Frame, isLight

def drawFrameContours(fname, img, cs):
    for j in range(len(cs)):
        cv2.drawContours(img, [ c.contour for c in cs ], j, (249,0,10), 2)
        cv2.drawContours(img, [ c.hull for c in cs ], j, (0,102,255), 2)
        cv2.imwrite(fname, img)

def open_video(fname):
    class VideoCapture():
        def __init__(self, fname):
            self.fname = fname
            self._cap = cv2.VideoCapture(self.fname)
            self._video = Video(self._cap)

        def __enter__(self):
            #self._cap = cv2.VideoCapture(self.fname)
            #return Video(self._cap)
            return self._video
            
        def __exit__(self,exc_type, exc_val, exc_tb):
            self._cap.release()

    return VideoCapture(fname)

class Video():
    def __init__(self, cap):
        self.cap = cap

    @property
    def fps(self):
        return self.cap.get(cv2.CAP_PROP_FPS)

    def __call__(self, yif):
        return self._frameIterator(self.cap, yif)

    #def __filtered_cap_iterator(self, pred=None):
    @staticmethod
    def _frameIterator(cap, pred=None):
        while(cap.isOpened()):
            retval = cap.grab()
            if not retval:
                cap.release()
            else:
                if pred is None or pred(cap):
                    yield Frame(None, cap)
                    #return _frameIterator(cap)
    
    def __iter__(self):
        return self._frameIterator(self.cap)
