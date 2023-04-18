from threading import Thread
import cv2 as cv
from urllib.request import urlopen
import ssl
import numpy as np

class Reader:
    '''
    obj = Reader(src).start()\n
    Reader(Source)\n
    Reader.start()\n
    Reader.get()\n
    Reader.stop()\n
    Reader.frame is the required output
    '''

    def __init__(self, src, gray=False, binary=False):
        self.stopped = False
        self.grayscale = gray
        self.binary_ = binary
        self.stream = cv.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        if self.binary_:
            self.binary()
        if self.grayscale:
            self.gray()

    def start(self):
        Thread(target=self.get, args=()).start()
        return self

    def get(self):
        while not self.stopped:
            if not self.grabbed or cv.waitKey(20) & 0xff == ord(" "):
                self.stream.release()
                print("Stream ended")
                self.stop()
            if self.grabbed:
                (self.grabbed, self.frame) = self.stream.read()
                if self.binary_:
                    self.binary()
                if self.grayscale:
                    self.gray()
            else:
                try:
                    self.arr = np.array(
                        bytearray(self.res.read()),
                        dtype=np.uint8
                    )
                    self.frame = cv.resize(cv.imdecode(
                        self.arr, -1), (640, 480))
                except:
                    pass

    def gray(self):
        cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)

    def binary(self, thr=70, max=255, sty=0):
        _, self.frame = cv.threshold(cv.cvtColor(
            self.frame, cv.COLOR_BGR2GRAY), thr, max, sty)

    def stop(self):
        self.stopped = True
        self.res = None
