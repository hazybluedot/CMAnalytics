#!/usr/bin/env python
import cv2

import sys
sys.path.append('../') 

from CMAnalytics import Frame
from CMAnalytics.video import open_video

def everyTen(cap):
    print('checking if frame number is modulo 10')
    return 0 == int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 10

if __name__ == '__main__':
    from sys import argv

    with open_video(argv[1]) as cap:
        print('FPS: {}'.format(cap.fps))

        for frame in cap(everyTen):
            print(frame)
