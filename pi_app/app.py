from flask import Flask, render_template, Response
import cv2 as cv
from threading import Thread


if __name__ == '__main__':
    app = Flask(__name__)

    def test(src):
        x = cv.VideoCapture(src)
        Thread(target=test, args=(src,)).start()
        while True:
            _, frm = x.read()
            try:

                _, buffer = cv.imencode('.jpg', frm)
                flask_frm = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + flask_frm + b'\r\n')
            except:
                pass

    @app.route('/video_feed')
    def web_feed():
        return Response(test(0), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/video_feed1')
    def usb_feed():
        return Response(test(1), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/video_feed2')
    def esp_feed():
        return Response(test('http://192.168.55.7:81/stream'), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/')
    def index():
        return render_template('index.html')
    app.run(debug=True,host='0.0.0.0')
