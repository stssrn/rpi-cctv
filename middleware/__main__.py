from flask import Flask, Response, render_template
from flask_socketio import SocketIO
from datetime import datetime as dt
from datetime import timedelta as td
from decouple import config
from emailsender import send

COOLDOWN = config("COOLDOWN_MINS", default=10, cast=float)

app = Flask(__name__, static_url_path="/static")
socketio = SocketIO(app)


# NOTE: global state isn't threadsafe
state = {
    "img": b"",  # jpeg image in bytes
    "last_notif_time": dt.now() - td(minutes=COOLDOWN),
}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("detected", namespace="/device")
def online():
    last_time = state["last_notif_time"]
    now = dt.now()
    if now - last_time > td(minutes=COOLDOWN):
        print("detected person! sending email...")
        state["last_notif_time"] = now
        send(state["img"])


@socketio.on("frame", namespace="/device")
def frame(jpeg):
    state["img"] = jpeg


def get_frame():
    prev = state["img"]
    while True:
        img = state["img"]
        if img != prev:
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
        prev = img


@app.route("/live")
def live():
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    HOST = config("MIDDLEWARE_HOST")
    PORT = config("MIDDLEWARE_PORT")
    socketio.run(app, port=PORT, host=HOST)
