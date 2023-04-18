import cv2
import cvzone
import pyfirmata as pf
import time
from twilio.rest import Client
import winsound
def buzzer():
    frequency = 2500  # Set Frequency To 2500 Hertz
    duration = 500  # Set Duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
    # time.sleep(1.5)
#SMS API Configuration
account_sid = 'ACb89cbf8b26ea01d557870be5c19183af'
auth_token = '1b65c7d1940ab12f2c923feed83b3aed'
client = Client(account_sid, auth_token)

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

@run_once
def send_msg(msg, receiver=7981606977, sent = False):

		message = client.messages \
						.create(
							body = msg,
							from_ = '+18582992819',
							to = '+91' + str(receiver)
						)
		print('Sent:', msg,"\nf'{message.sid}'")
#Detection algorithm start
if __name__=='__main__':
    url = 0 #IP address of the Camera server
    classNames = []
    classFile = './mini/coco.names' #Class lablels
    with open(classFile, 'rt') as f:
        classNames = f.read().split('\n')
    configPath = './config_files/ssd.pbtxt' #data.yaml config file required by yolo framework
    weightsPath = "./mini/mini.pb" #The trained frozen weights file
    net = cv2.dnn_DetectionModel(weightsPath, configPath) #Configurantion of detection algorithm
    net.setInputSize(320, 320)
    net.setInputScale(1.0 / 127.5)
    net.setInputMean((127.5, 127.5, 127.5))
    net.setInputSwapRB(True)
    thres = 0.55
    nmsThres = 0.2
    cap = cv2.VideoCapture(url) #Reading video
    #Resizing and compressing of the incoming video
    cap.set(3, 640)
    cap.set(4, 480)
    while 1:
            isTrue, img = cap.read() #Read frames from video
            img = cv2.flip(img, 1) #Flip frame to avoid mirrored text
            if img is not None:
                classIds, confs, bbox = net.detect(
                    img, confThreshold=thres, nmsThreshold=nmsThres) #Configure detection threshold
                try:
                    for classId, conf, box in zip(classIds.flatten(), confs.flatten(), bbox):
                        id = classNames[classId - 1] #Extract class name
                        print(confs)
                        if id=='drone':
                            # send_msg('Drone detected') #Send SMS to registered user
                            # buzzer() #Ring alarm
                            cv2.imwrite('Drone.jpg',img) #Save image of drone
                        cvzone.cornerRect(img, box)
                        cv2.putText(img, f'{classNames[classId - 1].upper()} {round(conf * 100, 2)}',
                                    (box[0] + 10, box[1] +
                                    30), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                    1, (0, 255, 0), 2)
                    frame = img
                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()
                    cv2.imshow('',img)
                    if cv2.waitKey(20)&0xff==ord(' '):
                        break
                except:
                    pass
            else:
                break