from threading import Thread
import cv2 as cv


class Viewer:
    '''
    obj = Viewer(Read_obj.frm).start()\n
    Viewer(frame)\n
    Viewer.start()\n
    Viewer.show()\n
    Viewer.stop()\n
    Viewer.frame is the required input
    '''

    def __init__(self, frame,gray = False, bin = False, flip = True):
        self.frame = frame
        self.stopped = False
        self.gray_ = gray
        self.bin = bin
        self.flip = True
        if self.gray_:
            self.gray()
        if self.bin:
            self.binary()
    def start(self):
        Thread(target=self.show, args=()).start()
        return self

    def show(self):
        while not self.stopped:
            if self.flip:
                cv.flip(self.frame,1)
            cv.imshow("Video", cv.resize(self.frame,(640,480)))
            if cv.waitKey(1) == ord(" "):
                self.stopped = True
            if self.gray_:
                self.gray()
            if self.bin:
                self.binary()
    def gray(self):
        cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)

    def binary(self, thr=70, max=255, sty=0):
        _, self.frame = cv.threshold(cv.cvtColor(
            self.frame, cv.COLOR_BGR2GRAY), thr, max, sty)
    def stop(self):
        self.stopped = True
        cv.destroyAllWindows()
