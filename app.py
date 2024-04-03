from flask import Flask, render_template, Response, stream_with_context
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video_feed():
    return render_template('video.html')

#@app.route('/video/<filename>')
@app.route('/video1')
#def video(filename):
def video1():
    def generate():
        try:
            filename = "static/video/虽然是精神病但没关系_第1集.mp4"
            with open(f'{filename}', 'rb') as video:
                data = video.read(1024)
                while data:
                    yield data
                    data = video.read(1024)
        except Exception as e:
            print(str(e))
            return 'File not found'

    return Response(stream_with_context(generate()), mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True)