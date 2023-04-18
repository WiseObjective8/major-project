import cv2 as cv
import yolov5 as y5  # needs revisiting
import sys
from collections import deque
import imutils
import numpy as np
# from alerts.sms import SMS
import cvzone


class Test_detect:
    def __init__(self, labels, weights):
        self.labels = labels
        self.weights = weights
        self.model = cv.dnn_DetectionModel(self.weights, self.labels)
        self.model.setInputSize(320, 320)
        self.model.setInputScale(1.0/127.5)
        self.model.setInputMean((127.5, 127.5, 127.5))
        self.model.setInputSwapRB(True)
        self.thresh = 0.55
        self.nms_thres = 0.2
        # self.alert = SMS()

    def detect(self, frame):
        if frame is not None:
            self.id, self.conf, self.bbox = self.model.detect(
                frame, confThreshold=self.thresh, nmsThreshold=self.nms_thres)
            try:
                for id, conf, bbox in zip(self.id.flatten(), self.conf.flatten(), self.bbox):
                    self.alert.start()
                    cvzone.cornerRect(frame, bbox)
                    return frame

            except Exception as e:
                print(f'{e}: Test_detect class')
                pass


class Tracking():
    def __init__(self, frame, lower=(0, 0, 0), upper=(180, 255, 30)):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.stopped = False
        self.pts = deque(maxlen=64)
        self.frame = frame

    def run(self):
        try:
            self.frame = imutils.resize(self.frame, width=600)
            self.blur = cv.GaussianBlur(self.frame, (11, 11), 0)
            self.hsv = cv.cvtColor(self.blur, cv.COLOR_BGR2HSV)
            self.mask = cv.dilate(
                cv.erode(
                    cv.inRange(
                        self.hsv,
                        self.lower,
                        self.upper),
                    None,
                    iterations=2),
                None,
                iterations=2)
            self.conts = imutils.grab_contours(
                cv.findContours(
                    self.mask.copy(),
                    cv.RETR_EXTERNAL,
                    cv.CHAIN_APPROX_SIMPLE))
            self.cen = None
            if len(self.conts) > 0:
                for conts in self.conts:
                    (x, y, w, h) = cv.boundingRect(conts)
                    ((_, __), self.rad) = cv.minEnclosingCircle(conts)
                    self.M = cv.moments(conts)
                    self.X = int(self.M['m10']/self.M['m00'])
                    self.Y = int(self.M['m01']/self.M['m00'])
                    cv.drawContours(self.frame, [conts], -1, (0, 255, 0), 2)
                    if self.rad > 10:
                        cv.circle(self.frame, (self.X, self.Y),
                                  7, (255, 255, 255), -1)
                        cv.rectangle(self.frame, (x, y),
                                     (x + w, y + h), (0, 255, 255), 2)
                        cv.putText(self.frame, "Status: {}".format('Movement'), (10, 20), cv.FONT_HERSHEY_SIMPLEX,
                                   1, (255, 0, 0), 3)
                #         self.pts.appendleft((self.X, self.Y))
                #     # loop over the set of tracked points
                #         for i in range(1, len(self.pts)):
                #             # if either of the tracked points are None, ignore
                #             # them
                #             if self.pts[i - 1] is None or self.pts[i] is None:
                #                 continue
                # # otherwise, compute the thickness of the line and
                # # draw the connecting lines
                #             thickness = int(
                #                 np.sqrt(int(64) / float(i + 1)) * 2.5)
                #             cv.line(
                #                 self.frame, self.pts[i - 1], self.pts[i], (0, 0, 255), thickness//4)
        except Exception as e:
            print("{} : Tracking Class".format(e))
            pass
        finally:
            return self.frame
