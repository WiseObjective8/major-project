import sys
from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2 as cv
import numpy as np
import imutils
from collections import deque
import cvzone
from mini.mini import *
from multiprocessing import Process
import pyfirmata as pf
from colorama import Fore
from motion import Tracker
import time

class Signals(QObject):
    vid_sig = pyqtSignal(np.ndarray, str)
    thread_dead = pyqtSignal(bool)
    cam_open = pyqtSignal(bool, str)
    vid_empty = pyqtSignal(bool)
    update_accessed = pyqtSignal(bool)
    direction = pyqtSignal(str, str)
    ard = pyqtSignal(str, bool)
    thread_alive = pyqtSignal(bool)


class Arduino:
    def __init__(self):
        self.board = pf.Arduino('COM9')
        self.board.digital[4].write(0)
        self.stopped = False

    def buzzer(self):
        if not self.stopped:
            pass
            # self.board.digital[4].write(1)

    def stop(self):
        self.stopped = True
        self.board.digital[4].write(0)

try:
    arduino = Arduino()
except: pass



class Tracking():
    def __init__(self, lower=(0, 52, 0), upper=(255, 255, 99)):
        super().__init__()
        self.lower = lower
        self.upper = upper
        self.stopped = False
        self.pts = deque(maxlen=32)
        self.counter = 0
        self.direction = ""

    def stop(self):
        self.stopped = True

    def run(self, frame):
        self.frame = frame
        (dX, dY) = (0, 0)
        direction = "Not moving"
        if frame is not None:
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
                        cv.RETR_TREE,
                        cv.CHAIN_APPROX_SIMPLE))
                self.cen = None
                if len(self.conts) > 0:
                    conts = max(self.conts, key=cv.contourArea)
                    (x, y, w, h) = list(cv.boundingRect(conts))
                    ((_, __), self.rad) = cv.minEnclosingCircle(conts)
                    self.M = cv.moments(conts)
                    self.X = int(self.M['m10']/self.M['m00'])
                    self.Y = int(self.M['m01']/self.M['m00'])
                    if self.rad > 10:
                        #arduino.buzzer()
                        cv.circle(self.frame, (self.X, self.Y),
                                  7, (255, 255, 255), -1)
                        cv.rectangle(self.frame, (x, y),
                                     (x + w, y + h), (0, 255, 255), 2)
                        self.pts.appendleft((self.X, self.Y))
                        for i in range(1, len(self.pts)):
                            if self.pts[i - 1] is None or self.pts[i] is None:
                                continue
                            if self.counter >= 10 and i == 1 and self.pts[-10] is not None:
                                dX = self.pts[-10][0] - self.pts[i][0]
                                dY = self.pts[-10][1] - self.pts[i][1]
                                (dirX, dirY) = ("", "")
                                if np.abs(dX) > 20:
                                    dirX = "East" if np.sign(
                                        dX) == 1 else "West"
                                else:
                                    dirX = ""
                                if np.abs(dY) > 20:
                                    dirY = "North" if np.sign(
                                        dY) == 1 else "South"
                                else:
                                    dirY = ""
                                if dirX and dirY:
                                    direction = f"{dirY}-{dirX}"
                                elif dirX:
                                    direction = dirX
                                elif dirY:
                                    direction = dirY
                                else:
                                    direction = "Stationary"

                            # cv.line(
                                # self.frame, self.pts[i - 1], self.pts[i], (0, 0, 255), 1)
                            cv.putText(self.frame, direction, (x, y - 10),
                                       cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                            self.direction = direction
                            # arduino.stop()
                # arduino.stop()
                return self.frame, self.direction

            except Exception as e:
                print("{} : Tracking Class".format(e))
                pass
        else:
            self.frame = np.zeros((480, 640), dtype=np.uint8)
            print('Cannot start process')
            return self.frame, ""


# class Detect():
#     def __init__(self, thres= 0.5, nms_thres=0.2):
#         self.weights = './mini/mini.pb'
#         self.config = './mini/ssd.pbtxt'
#         self.thres = thres,
#         self.nms_thres = nms_thres
#         self.model = cv.dnn_DetectionModel(self.weights, self.config)
#         self.model.setInputSize(320, 320)
#         self.model.setInputScale(1.0/127.5)
#         self.model.setInputMean((127.5, 127.5, 127.5))
#         self.model.setInputSwapRB(True)

#     def detect(self, frame: cv.Mat):
#         if frame is not None:
#             ids, confs, bbox = self.model.detect(
#                 frame, confThreshold=self.thres, nmsThreshold=self.nms_thres)
#             try:
#                 if len(confs) > 0:
#                     for conf, box in zip(confs.flatten(), bbox):
#                        ** cvzone.cornerRect(frame, box)
#                         cv.putText(frame, f'DRONE {round(conf*100,2)}',
#                                    (box[0]+10, box[1]+30), cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)

#             except Exception as e:
#                 print(e)
#                 pass
#         else:
#             print("Can't read frame")
#             pass
#         return frame


class Worker(QRunnable):

    def __init__(self, src, key: str):
        super().__init__()
        self.worker_key = key
        self.src = src
        self.width = 640
        self.height = 480
        self.sig = Signals()
        self.end = False
        self.stream = cv.VideoCapture(self.src)
        self.track = Tracking()
    @pyqtSlot()
    def run(self):
        while not self.end:
            self.track.counter += 1
            _, self.frm = self.stream.read()
            self.sig.cam_open.emit(_, self.worker_key)
            if self.frm is None:
                self.frm = np.zeros((self.height, self.width), dtype=np.uint8)
            if _:
                try:
                    self.img = cv.flip(cv.cvtColor(
                        self.frm.copy(), cv.COLOR_BGR2RGB), 1)
                    self.img, self.dir = self.track.run(self.img)
                    self.sig.vid_sig.emit(self.img, self.worker_key)
                    if self.dir: self.sig.ard.emit(self.worker_key, True)
                    else: self.sig.ard.emit(self.worker_key, False)
                    self.sig.direction.emit(self.dir, self.worker_key)
                except Exception as e:
                    print(f'{e} Video Class')
                    self.stream.release()
                    pass
            else:
                _ = self.end
                self.sig.vid_empty.emit(not _)
                break


class App(QMainWindow):
    CAM_KEYS = {'web': 0,
                'usb': 1,
                'esp': 'http://192.168.150.7:81/stream'
                }
    key = pyqtSignal(str)

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        # self.arduino = Arduino()
        self.label_timer = time.time()
        self.setWindowTitle('Camera Montoring Application')
        self.width_, self.height_ = 320, 240
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.grid = QGridLayout(self.central_widget)
        self.cord = ((0, 0), (0, 1), (1, 0), (1, 1))
        self.widgets = {
            'web': QWidget(),
            'esp': QWidget(),
            'usb': QWidget(),
            'data': QWidget()
        }

        self.labels = {
            'web': QLabel(self),
            'esp': QLabel(self),
            'usb': QLabel(self),
            'data': QLabel()
        }
        self.workers = {
            'web': Worker(self.CAM_KEYS['web'], 'web'),
            'esp': Worker(self.CAM_KEYS['esp'], 'esp'),
            'usb': Worker(self.CAM_KEYS['usb'], 'usb')
        }
        for key, (r, c) in zip(self.widgets, self.cord):
            self.labels[key].setMinimumWidth(self.width_)
            self.labels[key].setMinimumHeight(self.height_)
            self.labels[key].setMaximumHeight(self.height_ * 2)
            self.labels[key].setMaximumWidth(self.width_ * 2)
            self.labels[key].resize(int(self.width_), int(self.height_))
            self.grid.addWidget(self.widgets[key], r, c)

            print(f'Widget created: {key}')
        # self.data_layout()
        for c, r in zip(range(2), range(2)):
            self.grid.setColumnStretch(c, 1)
            self.grid.setRowStretch(r, 1)
        for key in self.widgets:
            self.box = QVBoxLayout(self.widgets[key])
            self.box.addWidget(self.labels[key])
        self.start_workers()

    def data_layout(self, widget: QWidget):
        print('Widget created: data')
        ...

    def start_workers(self):
        self.threadpool = QThreadPool.globalInstance()
        print("Maximum %d threads" % self.threadpool.maxThreadCount())
        for key in self.workers:
            try:
                self.threadpool.start(self.workers[key])
                self.workers[key].sig.vid_sig.connect(self.show_frm)
                self.workers[key].sig.cam_open.connect(self.set_gray)
                self.workers[key].sig.direction.connect(self.direction)
                # self.workers[key].sig.ard.connect(self.buzzer)
            except:
                self.labels[key]
                pass

    # @pyqtSlot(str, bool)
    # def buzzer(self, key, state):
    #     if state:
    #         self.arduino.buzzer()
    #     else:
    #         self.arduino.stop()
    #     ...

    @pyqtSlot(bool, str)
    def set_gray(self, cam_open, key):
        if not cam_open:
            self.image = QImage(
                self.width_*2, self.height_*2, QImage.Format_RGB888)
            self.image.fill(0)
            self.labels[key].setPixmap(QPixmap.fromImage(self.image))
            self.labels[key].setAlignment(Qt.AlignCenter)
            self.labels[key].setText('Camera Offline')
            ...
        else:
            pass

    @pyqtSlot(cv.Mat, str)
    def show_frm(self, frm, key):
        self.qimage = QImage(
            frm.data, frm.shape[1], frm.shape[0],
            QImage.Format_RGB888).scaled(self.width_*2, self.height_*2,
                                         Qt.KeepAspectRatio)
        self.labels[key].setPixmap(QPixmap.fromImage(self.qimage))

    @pyqtSlot(str, str)
    def direction(self, dir: str, key: str):
        timer = time.time()
        strings = {
            'web': '<br><br><br>',
            'usb': '<br><br><br>',
            'esp': '<br><br><br>'
        }
        temp = ""
        temp_1 = ""
        temp_2 = ""
        text,res = "",""
        self.labels['data'].setAlignment(Qt.AlignTop)
        for kkey in strings:
            if kkey == key:
                temp = dir
                temp_1 = f'drone not detected<br>'.upper()
                temp_2 = f'Location of drone: {kkey} camera'
            else:
                continue
            res = f"{temp_1}Direction at {key} camera: {temp}<br>{temp_2}<br><br><br>"
            text += f"{temp_1}Direction: {temp}<br>{temp_2}<br><br><br>"
            # print(text)
        if timer - self.label_timer >= 1:
            send_msg(text)
            # buzzer()
            self.labels['data'].setText(text)
            self.label_timer = timer
        else:
            pass



if __name__ == '__main__':
    a = QApplication(sys.argv)
    app = App()
    app.setStyleSheet("QLabel{font-size: 16pt;}")
    app.show()
    # arduino.stop()
    sys.exit(a.exec_())

