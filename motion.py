import cv2 as cv
import numpy as np
import imutils
from collections import deque


class Tracker:
    def __init__(self, thresh: int, ksize: int, cnt_area: int, upper: tuple, lower: tuple, buffer_len: int):
        self.thresh = thresh
        self.kernel = (ksize, ksize)
        self.sensitivity = cnt_area
        self.ref = None
        self.upper = upper
        self.lower = lower
        self.buffer = buffer_len
        self.points = deque(maxlen=self.buffer)

    def non_max_suppression(self, contours, overlap_thresh):
        boxes = []
        cv.drawContours(self.img,contours,-1,(255,0,0),cv.FILLED)
        for contour in contours:
            x, y, w, h = cv.boundingRect(contour)
            if w*h > self.sensitivity:
                boxes.append((x, y, w, h))
        boxes = np.array(boxes)
        boxes = np.reshape(boxes,(-1,4))
        pick = []
        print(len(boxes),'before')
        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = x1 + boxes[:, 2]
        y2 = y1 + boxes[:, 3]
        area = boxes[:, 2] * boxes[:, 3]
        idxs = np.argsort(y2)
        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)
            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])
            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)
            overlap = (w * h) / area[idxs[:last]]
            idxs = np.delete(idxs, np.concatenate(
                ([last], np.where(overlap > overlap_thresh)[0])))
            # print(idxs,'idx')
        print(len(pick),'pick')
        xxxx = [boxes[i] for i in pick]
        print(len(xxxx),'xxxx')
        return xxxx

    def non_max_suppression1(self, contours, overlapThresh):
        if len(contours) == 0:
            return []

        # if the contours are not in a numpy array, convert them to one
        if type(contours) is not np.ndarray:
            contours = np.array(contours)
        print(contours)
        # initialize the list of picked indexes
        pick = []

        # grab the coordinates of the bounding boxes
        _x, _y, _w, _h = cv.boundingRect(contours)
        rects = np.array([[_x, _y, _x+_w, _y+_h]])
        x, y, w, h = [], [], [], []
        x.append(_x)
        y.append(_y)
        w.append(_w)
        h.append(_h)
        # compute the area of the bounding boxes and sort the bounding
        # boxes by their bottom-right y-coordinate
        area = float(_w * _h)
        idxs = np.argsort(_y + _h)

        # keep looping while some indexes still remain in the indexes
        # list
        while len(idxs) > 0:
            # grab the last index in the indexes list and add the
            # index value to the list of picked indexes
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            # find the largest (x, y) coordinates for the start of
            # the bounding box and the smallest (x, y) coordinates
            # for the end of the bounding box
            xx1 = np.maximum(x[i], x[idxs[:last]])
            yy1 = np.maximum(y[i], y[idxs[:last]])
            xx2 = np.minimum(x[i] + w[i], x[idxs[:last]] + w[idxs[:last]])
            yy2 = np.minimum(y[i] + h[i], y[idxs[:last]] + h[idxs[:last]])

            # compute the width and height of the bounding box
            w1 = np.maximum(0, xx2 - xx1 + 1)
            h1 = np.maximum(0, yy2 - yy1 + 1)

            # compute the ratio of overlap
            overlap = (w1 * h1) / area[idxs[:last]]

            # delete all indexes from the index list that have
            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))

        # return only the bounding boxes that were picked
        return rects[pick]

    def direction(self, frm: cv.Mat):
        self.img = frm
        self.blur_dir = cv.GaussianBlur(self.img, self.kernel, 0)
        self.hsv = cv.cvtColor(self.blur_dir, cv.COLOR_BGR2HSV)
        self.mask = cv.dilate(
            cv.erode(
                cv.inRange(
                    self.hsv,
                    self.lower,
                    self.upper
                ),
                None,
                iterations=2
            ),
            None,
            iterations=2
        )
        self.contours_dir = cv.findContours(
            self.mask.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        self.contours_dir = imutils.grab_contours(self.contours_dir)
        self.center = None
        if len(self.contours_dir) > 0:
            # for c in self.contours_dir:
            c = max(self.contours_dir, key=cv.contourArea)
            (x, y, w, h) = cv.boundingRect(c)
            ((_, __), radius) = cv.minEnclosingCircle(c)
            M = cv.moments(c)
            X = int(M['m10']/M['m00'])
            Y = int(M['m01']/M['m00'])
            if radius > 10:
                cv.circle(self.img, (X, Y), 5, (0, 0, 255), -1)
                cv.rectangle(self.img, (x, y), ((x+w), (y+h)), (255, 0, 0), 2)
                self.points.appendleft((X, Y))
                for i in np.arange(1, len(self.points)):
                    if self.points[i - 1] is None or self.points[i] is None:
                        continue
                    thickness = int(np.sqrt(self.buffer / float(i + 1)) * 2.5)
                    cv.line(
                        self.img, self.points[i - 1], self.points[i], (0, 0, 255), thickness)
        return self.img

    def motion(self, frm: cv.Mat):
        self.img = frm
        self.direction(self.img.copy())
        self.frm = cv.cvtColor(frm, cv.COLOR_BGR2GRAY)
        if self.ref is not None:
            self.abs = cv.absdiff(self.frm, self.ref)
            # self.abs = cv.bitwise_xor(self.frm,self.ref)
            self.blur = cv.GaussianBlur(self.abs, self.kernel, 0)
            _, self.thres = cv.threshold(
                self.blur, self.thresh, 255, cv.THRESH_BINARY)
            self.contours, hierarchy = cv.findContours(
                self.thres, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)

            # cv.drawContours(self.img, self.contours, -1, (0, 0, 255), 2)
            for boxes in self.non_max_suppression(self.contours, 0.2):
                x, y, w, h = boxes
                if (w*h) > self.sensitivity:
                    cv.rectangle(self.img, (x, y), ((x+w), (y+h)), (255, 0,255), 4)
            # for contour in self.contours:
            #     rect = [x, y, w, h] = list(cv.boundingRect(contour))
            #     if cv.contourArea(contour) > self.sensitivity:
            #         cv.rectangle(self.img, (x, y), ((x+w), (y+h)), (255, 255, 0), 2)
            #         pick = self.non_max_suppression(rect,hierarchy,0.4)
            self.ref = self.frm
        else:
            self.ref = self.frm
        # cv.imshow('',self.img)
        return self.img

    def union(a, b):  # to merge rectangles
        x = min(a[0], b[0])
        y = min(a[1], b[1])
        w = max(a[0]+a[2], b[0]+b[2]) - x
        h = max(a[1]+a[3], b[1]+b[3]) - y
        return (x, y, w, h)
