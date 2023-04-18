from tuners.Reader import *
from tuners.Viewer import *
from tuners.Camera import *
# import cv2 as cv
import cvzone

import cv2

class BoundingBox:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def draw(self, frame):
        cv2.rectangle(frame, (self.x, self.y), (self.x+self.w, self.y+self.h), (0, 255, 0), 2)

    def get_roi(self, frame):
        return frame[self.y:self.y+self.h, self.x:self.x+self.w]

class Webcam:
    def __init__(self, device=0):
        self.cap = cv2.VideoCapture(device)

    def __del__(self):
        self.cap.release()

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

webcam = Webcam()
bounding_box = BoundingBox(100, 100, 200, 200)

while True:
    frame = webcam.get_frame()
    if frame is None:
        break

    bounding_box.draw(frame)

    roi = bounding_box.get_roi(frame)
    cv2.imshow('ROI', roi)

    cv2.imshow('Webcam', frame)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

# class Detect:
#     def __init__(self, weights='./mini/frozen_inference_graph.pb',
#                  config='./mini/ssd.pbtxt',
#                  thres=0.55,
#                  nms_thres=0.2):
#         self.model = cv.dnn_DetectionModel(weights, config)
#         self.model.setInputSize(320, 320)
#         self.model.setInputScale(1.0/127.5)
#         self.model.setInputMean((127.5, 127.5, 127.5))
#         self.model.setInputSwapRB(True)
#         self.thres = thres
#         self.nms_thres = nms_thres
#         self.stopped = False

#     def run(self, frame):
#         self.frame = frame
#         if self.frame is not None and not self.stopped:
#             ids, confs, bbox = self.model.detect(
#                 self.frame, confThreshold=self.thres, nmsThreshold=self.nms_thres)
#             try:
#                 if len(confs) > 0:
#                     for conf, box in zip(confs.flatten(), bbox):
#                         cvzone.cornerRect(self.frame, box)
#                         cv.putText(self.frame, f'DRONE {round(conf * 100, 2)}',
#                                    (box[0] + 10, box[1] + 30), cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)

#             except Exception as e:
#                 print(e)
#                 pass
#             finally:
#                 return self.frame


# Camera('http://192.168.85.7:81/stream').start()