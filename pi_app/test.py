from threading import Thread
from flask import Flask, render_template, Response
import cv2 as cv
from video_server import Video

app = Flask(__name__)


def cv_to_flask():
    web = Video(0).start()
    while True:
        frm = web.stream.read()
             


@app.route('/video_feed')
def web_feed():
    web = Video(0).start()
    return Response(web.cv_to_flask(), mimetype='multipart/x-mixed-replace; boundary=frame')

 
@app.route('/video_feed1')
def usb_feed():
    usb = Video(1).start()
    return Response(usb.cv_to_flask(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def esp_feed():
    usb = Video('http://192.168.55.7:81/stream').start()
    return Response(usb.cv_to_flask(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
