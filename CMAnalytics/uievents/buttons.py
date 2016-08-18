import cv2
import numpy as np

from CMAnalytics import findContours
from CMAnalytics.templates import playTemplates

# left for posterity, we are now using actual images from screen captures as templates. Use bin/makePlayTempltes.py to create templates from captured frames
def _generatePlayButtonTemplates(playButton, roi):
    def offset(points, offset):
        m = np.hstack((np.eye(2), np.array(offset).reshape(2,1)))
        return cv2.transform(points, m)

    play_template = roi.img.copy()
    nohover_template = roi.img.copy()

    yellow = (13,255,254) # taken with color picker
    green = (2,255,177)

    symbol_pts = offset(playButton.contour, roi.offset)
    
    cv2.fillConvexPoly(play_template, symbol_pts, yellow)
    cv2.fillConvexPoly(nohover_template, symbol_pts, green)

    hover_template = play_template.copy()

    sym = next(playButton.children)

    symbol_pts = offset(sym.contour, roi.offset)

    cv2.fillConvexPoly(hover_template, symbol_pts, (255,255,255))
    cv2.drawContours(hover_template, [symbol_pts], 0, (128,128,128), 2)

    cv2.fillConvexPoly(nohover_template, symbol_pts, (255,255,255))
    cv2.drawContours(nohover_template, [symbol_pts], 0, (128,128,128), 2)

    m1 = np.hstack((np.eye(2)*np.array((0.9,0.8)), np.array((1,8)).reshape(2,1)))
                   # m*np.array((1,1,0.99)) # np.hstack((np.eye(2), m[:,2].reshape(2,1)))

    play_symbol = cv2.transform(sym.boundingRect.contour, m*np.array([1, 1, 1]))
    play_symbol = cv2.transform(play_symbol, m1)
    
    cv2.fillConvexPoly(play_template, play_symbol, (255,255,255))
    cv2.drawContours(play_template, [play_symbol], 0, (128,128,128), 2)

    return dict(zip(('play', 'hover', 'nohover'), (play_template, hover_template, nohover_template)))

def isPlaying(frame, playButton, **kwargs):
    return playButtonState(frame, playButton, **kwargs) in [ 'play_hover', 'play_nohover' ]
def playButtonState(frame, playButton, **kwargs):
    """return play button state, one of 'play', 'hover', or 'nohover'"""
    
    # we do this by template matching: we generate three templates,
    # one for each button state, from contour information, then apply
    # the matchTemplate function to the region of interest for each
    # template. The template with the lowest match score corresponds
    # to the button state in the frame.
        
    roi = frame.subFrame(playButton.boundingRect)
    # TODO: should generate templates once at start
    #templates = kwargs.get('templates', _generatePlayButtonTemplates(playButton, roi))
    templates = playTemplates
    
    match = [ (label, cv2.matchTemplate(roi.img, template, cv2.TM_SQDIFF)[0][0]) for label, template in templates.items() ]
    
    return min(match, key=lambda x: x[1])[0]

def findPlayButton(frame):
    """Returns the bounding rectangle of the play button as well as the
bounding rectangle of the play symbol (triangle or square, depending
on state). Returns None if no play button is found on frame"""
    
    def playButtonFilter(shape):
        if shape.corners == 4 and shape.normalizedArea >= 0.01:
            first_child = next(shape.children, None)
            if first_child is not None:
                return first_child.corners == 3
        return False

    lHeight, lWidth = frame.img.shape[0:2]
    upper_right = frame.subFrame( [ (lWidth*3/4, 0), (lWidth, lHeight/4) ] )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    
    contours = findContours(upper_right,
                            threshold=129,
                            mode=cv2.RETR_CCOMP,
                            morph=[(cv2.MORPH_ERODE, kernel)])

    # idium for finding first item in iterable matching a predicate
    return next( (s for s in contours if playButtonFilter(s) ), None), contours
