import cvzone
import cv2 as cv
import time
from multiprocessing import Process

class Detect:
    def __init__(self, weights: str, config: str, thres: float, nms_thres: float):
        self.model = cv.dnn_DetectionModel(weights, config)
        self.model.setInputSize(320, 320)
        self.model.setInputScale(1.0/127.5)
        self.model.setInputMean((127.5, 127.5, 127.5))
        self.model.setInputSwapRB(True)
        self.thres = thres
        self.nms_thres = nms_thres
        self.stopped = False

    

    def run(self, frame: cv.Mat):
        self.frame = frame
        if frame is not None:
            ids, confs, bbox = self.model.detect(
                frame, confThreshold=self.thres, nmsThreshold=self.nms_thres)
            try:
                for conf, box in zip(confs.flatten(), bbox):
                    cvzone.cornerRect(frame, box)
                    cv.putText(frame, f'DRONE {round(conf*100,2)}',
                               (box[0]+10, box[1]+30), cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)
                return frame
            except Exception as e:
                print(e)
                pass
                return frame
