from flask import Flask, render_template
from flask_socketio import SocketIO
import speech_recognition as sr

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def listen_for_speech():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

        try:
            speech_text = recognizer.recognize_google(audio)
            print(f"Detected speech: {speech_text}")
            socketio.emit('speech_detected', {'speech': speech_text})
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

@socketio.on('connect')
def handle_connect():
    print("Client connected")

if __name__ == '__main__':
    from threading import Thread
    speech_thread = Thread(target=listen_for_speech)
    speech_thread.start()
    socketio.run(app)
