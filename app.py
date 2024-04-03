from flask import Flask, render_template, Response, stream_with_context
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/<filename>')
def video(filename):
    def generate():
        with open(f'static/videos/{filename}', 'rb') as video:
            data = video.read(1024)
            while data:
                yield data
                data = video.read(1024)

    return Response(stream_with_context(generate()), mimetype='video/mp4')


if __name__ == '__main__':
    app.run(debug=True)