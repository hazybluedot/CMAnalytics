#!/usr/bin/env python

import cv2
import pytesseract as ocr
from tempfile import NamedTemporaryFile
from os import unlink
from itertools import tee, izip

def counted(f):
    def wrapped(*args, **kwargs):
        wrapped.called += 1
        return f(*args, **kwargs)
    wrapped.called = 0
    return wrapped

## iterator utilities

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


## Text extraction, may eventually move to own file if we have more util related stuff

try:
    import Image
except ImportError:
    from PIL import Image

TEMP_OCR_FILE = 'ocr.bmp'

def isolateText(frame):
    """return list of contours likely containing text"""
    # see http://stackoverflow.com/questions/23506105/extracting-text-opencv#23565051

    gray = frame.gray
    morphKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
    grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, morphKernel)
    tresh = cv2.treshold(grad, 0.0, 255.0, cv2.THRESH_BINARY)

    # connect horizontally oriented regions
    morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,1))
    connected = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, morphKernel)

    # find contours
    mask = np.zeros(thresh.shape, np.uint8)
    im, contours, hierarchy = cv2.findContours(connected, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE, (0,))

def extractText(frameORimg, **kwargs):
    try:
        img = frameORimg.gray
    except AttributeError:
        img = frameORimg

    if img.mean() <= 200:
        img = (255-img)
    temp_file = NamedTemporaryFile(suffix='.bmp' , delete=False)
    temp_file.close()
    cv2.imwrite(temp_file.name, img) # because NamedTemporaryFile returns an open file, this will probably only work on a Unix-based system where a file can be opened multiple times.
    #print('img mean: {0}'.format(img.mean()))
    name = ocr.image_to_string(Image.open(temp_file.name))
    if kwargs.get('debug', False):
        print('extracted text: {0}'.format(name))
        cv2.imshow('ocr this!', img)
        cv2.waitKey(0)
    unlink(temp_file.name)
    return name

def extractPuzzleName(frame):
    try:
        img = frame.img
    except AttributeError:
        img = frame

    roi = frame.subFrame( [(115,18), (750,90)] )    
    return extractText(roi)

if __name__ == '__main__':
    import sys

    frame = cv2.imread(sys.argv[1])

    print(puzzleName(frame))
