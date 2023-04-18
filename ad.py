import cv2 as cv
from motion import *
tracker = Tracker(50, 5, 500, (255, 255, 99), (0, 52, 0), 64)
vid = cv.VideoCapture(1)
ref = None
while True:
    _, frm = vid.read()
    frm = cv.flip(frm, 1)
    cv.imshow('',tracker.direction(frm))
    
    if cv.waitKey(10) & 0xff == ord(' '):
        break
