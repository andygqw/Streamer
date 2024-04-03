from flask import Flask, render_template, Response, stream_with_context
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video_feed():
    return render_template('video.html')

@app.route('/video/<filePath>')
def video(filePath):
    filePath = 'static/video/虽然是精神病但没关系_第1集.mp4'
    return Response(stream_with_context(generate_video(filePath)), mimetype='video/mp4')

def generate_video(video_path):
    with open(video_path, "rb") as video_file:
        while True:
            data = video_file.read(1024 * 1024)
            if not data:
                break
            yield data




if __name__ == '__main__':
    app.run(debug=True)