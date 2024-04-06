from flask import Flask, render_template, Response, stream_with_context, request, send_from_directory, abort
from werkzeug.utils import safe_join
import re
import os

app = Flask(__name__)


BASE_FOLDER = '/Volumes/Andys_SSD/'

@app.route('/')
@app.route('/browse/')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):

    full_path = safe_join(BASE_FOLDER, subpath)

    if not os.path.exists(full_path):
        print('Can\'t find folder: ' + full_path)
        abort(404)

    if os.path.isdir(full_path):
        items = {'folders': [], 'files': []}
        for item in os.listdir(full_path):
            if os.path.isdir(os.path.join(full_path, item)):
                items['folders'].append(item)
            else:
                if item.endswith('.mp4') or item.endswith('.mov') or item.endswith('.jpg') or item.endswith('.jpeg') or item.endswith('.png')or item.endswith('.pdf'):
                    items['files'].append(item)
        return render_template('index.html', items=items, path=subpath)
    else:
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))


@app.route('/video')
def video_feed():
    return render_template('video.html')

@app.route('/video/<filePath>')
def video(filePath):

    #filePath = '/Volumes/Andys_SSD/content/movies/虽然是精神病但没关系/虽然是精神病但没关系_第3集.mp4'

    range_header = request.headers.get('Range', None)
    if not range_header:  # Browser doesn't support range requests
        print('Browser doesn\'t support range requests')
        return Response(stream_with_context(generate_video(filePath)), mimetype='video/mp4')

    size = os.path.getsize(filePath)    
    byte1, byte2 = 0, None

    # Extract the range values
    m = re.search('(\d+)-(\d*)', range_header)
    g = m.groups()

    if g[0]:
        byte1 = int(g[0])
    if g[1]:
        byte2 = int(g[1])

    length = size - byte1
    if byte2 is not None:
        length = byte2 + 1 - byte1

    # Create the initial response
    data = None
    with open(filePath, 'rb') as f:
        f.seek(byte1)
        data = f.read(length)

    rv = Response(data, 
                  206,  # 206 Partial Content
                  mimetype='video/mp4',
                  direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(byte1, byte1 + length - 1, size))
    rv.headers.add('Accept-Ranges', 'bytes')

    return rv

def generate_video(video_path):
    with open(video_path, "rb") as video_file:
        while True:
            data = video_file.read(1024 * 1024)
            if not data:
                break
            yield data


if __name__ == '__main__':
    app.run(debug=True)