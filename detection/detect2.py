import yolov5 as y5
import cv2 as cv
from threading import Thread
import sys


model = y5.load('./config_files/drones.pt', autoshape=True)
# img = cv.imread('./drone.jpg')
# res = model(img)
# bnd = res.pred[0]
# bbox = [int(i) for i in bnd.tolist()[0]][:4]
# print(*bbox)
# cv.rectangle(img, (bbox[0], bbox[1]),
#              (bbox[0] + bbox[2], bbox[1] + bbox[3]), (180, 0, 0), 2)
# cv.imshow(' ', img)
# # cv.waitKey(0)
# cv.destroyAllWindows()


def vid(src):
    Thread(target=vid, args=(src,)).start()
    x = cv.VideoCapture(src)
    return 

    
vi = vid(0)
while True:
    try:
        _, img = vi.read()
        if cv.waitKey(10)&0xff==ord(' '):
            break
        res = model(img)
        bnd = res.pred[0]
        bbox = [int(i) for i in bnd.tolist()[0]][:4]
        cv.rectangle(img, (bbox[0], bbox[1]),
                    (bbox[0] + bbox[2], bbox[1] + bbox[3]), (180, 0, 0), 2)
        cv.imshow('', img)
    except Exception as e:
        print('Error',e)
        pass