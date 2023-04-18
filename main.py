from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import cv2 as cv
import yolov5 as y5  # needs revisiting
import sys
from collections import deque
from misc import Tracking
import cvzone
# from alerts.sms import SMS

# '''
#     1. Simultaenous feeds are running with no interruptions.
#     2. ESP camera feed is lagging cause could be unstable
#        power supply.
#     3. Simultaneous tracking of pixel clusters and blobs
#        is successful.
#     4. Detection using yolov5 model is successful but the
#        fps of video feeds falls down to 1 - 2 fps.
#     5. Explore alternative architectures
#         a. ONNX
#         b. Tensorflow GraphDef
#     6. Alert system is working but needs revisiting for thread
#        synchronization and API optimization.
#     7. Movement for servo motors need to be configured. Possibly
#        on raspberry pi.
#     8. Need to host all video feeds using raspberry pi to
#        increase detection efficiency.

# '''
 
class Detect():
    def __init__(self,weights: str, config: str, thres: float, nms_thres: float):
        super().__init__()
        self.model = cv.dnn_DetectionModel(weights, config)
        self.model.setInputSize(320, 320)
        self.model.setInputScale(1.0/127.5)
        self.model.setInputMean((127.5, 127.5, 127.5))
        self.model.setInputSwapRB(True)
        self.thres = thres
        self.nms_thres = nms_thres
        self.stopped = False


    def run(self,frame:cv.Mat):
        self.frame = frame
        if self.frame is not None and not self.stopped:
            ids, confs, bbox = self.model.detect(
                self.frame, confThreshold=self.thres, nmsThreshold=self.nms_thres)
            try:
                for conf, box in zip(confs.flatten(), bbox):
                    cvzone.cornerRect(self.frame, box)
                    cv.putText(self.frame, f'DRONE {round(conf*100,2)}',
                               box[0]+10, box[1]+30, cv.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 255, 0), 2)

            except Exception as e:
                print(e)
                pass
        else:
            print("Can't read image")
            pass
        return self.frame
    def stop(self):
        self.stopped = True
        self.quit()
class vidReader(QThread):
    sig = pyqtSignal(QImage)

    def __init__(self, src=0):
        super().__init__()
        self.a = 640
        self.b = 480
        self.src = src
        self.stopped = False
        self.drone = False
        self.stream = cv.VideoCapture(self.src)

    def run(self):
        while not self.stopped:
            self.ret, self.frm = self.stream.read()
            if self.ret:
                try:
                    self.img = cv.flip(cv.cvtColor(
                        self.frm, cv.COLOR_BGR2RGB), 1)
                    if isinstance(self.src, str):
                        cv.resize(self.img, (640, 480))
                    self.qt = QImage(self.img.data, self.img.shape[1], self.img.shape[0],
                                     QImage.Format_RGB888)
                    self.temp = self.qt.scaled(
                        int(self.a), int(self.b), Qt.KeepAspectRatio)
                    self.sig.emit(self.qt)
                    self.img_ref = self.img
                except Exception as e:
                    print('{}: vidReader Class'.format(e))
                    pass

    def motion(self):
        self.diff = cv.absdiff(self.img_ref, self.img)
        self.diff_gray = cv.cvtColor(self.diff, cv.COLOR_BGR2GRAY)
        self.blur = cv.GaussianBlur(self.diff_gray, (5, 5), 0)
        _, self.thresh = cv.threshold(self.blur, 20, 255, cv.THRESH_BINARY)
        self.dilated = cv.dilate(self.thresh, None, iterations=3)
        self.contours, _ = cv.findContours(
            self.dilated, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for contour in self.contours:
            (x, y, w, h) = cv.boundingRect(contour)
            if cv.contourArea(contour) < 900:
                continue

    def draw_bbox(self, x, y, w, h):
        cv.rectangle(self.img_ref, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv.putText(self.img_ref, "Status: {}".format('Movement'), (10, 20), cv.FONT_HERSHEY_SIMPLEX,
                   1, (255, 0, 0), 3)

    def stop(self):
        self.stopped = True
        self.quit()


class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle('Camera Network')
        self.a, self.b = 320, 240
        self.cen = QWidget()
        self.setCentralWidget(self.cen)
        self.grid = QGridLayout(self.cen)
        self.keys = ('web', 'esp', 'usb')
        self.cord = ((0, 0), (0, 1), (1, 0), (1, 1))
        self.cams = {
            'web': 0,
            'esp': 'http://192.168.55.7:81/stream',
            'usb': 1,
            'data':0
        }
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
            'data': QLabel('Drone Location: 0\nDrone Direction: null',self)
        }
        self.threads = {
            'web': self.thread,
            'esp': self.thread,
            'usb': self.thread,
            'data': self.thread
        }
        for key, (r, c) in zip(self.widgets, self.cord):
            self.labels[key].setMinimumWidth(self.a)
            self.labels[key].setMinimumHeight(self.b)
            self.labels[key].setMaximumHeight(self.b*2)
            self.labels[key].setMaximumWidth(self.a*2)
            self.labels[key].resize(int(self.a), int(self.b))
            self.grid.addWidget(self.widgets[key], r, c)

        for c, r in zip(range(2), range(2)):
            self.grid.setColumnStretch(c, 1)
            self.grid.setRowStretch(r, 1)

        for key in self.labels:
            self.box = QVBoxLayout(self.widgets[key])
            self.box.addWidget(self.labels[key])
            print(self.labels[key].width(), self.labels[key].height())
            try:
                if key!='data':
                    self.threads[key] = vidReader(self.cams[key])
                    if key == "web":
                        self.threads[key].sig.connect(self.update_web)
                    if key == "usb":
                        self.threads[key].sig.connect(self.update_usb)
                    if key == "esp":
                        self.threads[key].sig.connect(self.update_esp)
                    self.threads[key].start()
                else:
                    pass
            except Exception as e:
                print('{}: App Class'.format(e))
                pass

    @pyqtSlot(QImage)
    def update_web(self, frame):
        try:
            self.labels['web'].setPixmap(QPixmap.fromImage(frame))
        except Exception as e:
            print('{}: update_web'.format(e))
            pass

    @pyqtSlot(QImage)
    def update_usb(self, frm):
        try:
            self.labels['usb'].setPixmap(QPixmap.fromImage(frm))
        except Exception as e:
            print('{}: update_usb'.format(e))
            pass

    @pyqtSlot(QImage)
    def update_esp(self, frm):
        try:
            self.labels['esp'].setPixmap(QPixmap.fromImage(frm))
        except Exception as e:
            print('{}: update_esp'.format(e))


if __name__ == '__main__':
    try:
        a = QApplication(sys.argv)
        app = App()
        app.showMaximized()
        sys.exit(a.exec_())
    except Exception as e:
        print('{} Main Method'.format(e))
        pass
