import cv2 as cv
# from Counter import Counter
from .Reader import Reader
from .Viewer import Viewer
from threading import Thread


class Camera:
    '''
    Implements a seperate thread for running both video and image threads\n
    Camera(source -> int, name -> str)\n
    Camera(source -> str, name -> str)\n
    Camera().start() --> starts webcam\n
    obj = Camera(src = 0,name = "Webcam").start()\n
    '''

    def __init__(self, source, gray=False, binary=False):
        print("Camera started")
        self.vid = Reader(source, gray, binary).start()
        self.img = Viewer(self.vid.frame,gray=False, bin=False)
        self.stopped = False
        self.frame = None

    def start(self):
        Thread(target=self.run, args=()).start()
        return self

    def run(self):
        def putIterationsPerSec(frame, iterations_per_sec):
            cv.putText(frame, "{:.0f} it/s".format(iterations_per_sec),
                       (10, 450), cv.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
            return frame

        if not self.stopped:
            self.img.start()
            # cps = Counter().start()
            while True:
                if self.vid.stopped or self.img.stopped:
                    self.img.stop()
                    self.vid.stop()
                    break

                frame = self.vid.frame
                self.frame = self.vid.frame
                # frame = putIterationsPerSec(frame, cps.countsPerSec())
                self.img.frame = frame
                # cps.increment()

    def stop(self):
        self.stopped = True
