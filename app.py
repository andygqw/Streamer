from flask import Flask, render_template, Response, stream_with_context, request, send_from_directory, abort, url_for
from werkzeug.utils import safe_join
import re
import os
import mimetypes


app = Flask(__name__)

# Constants
BASE_FOLDER = '/Volumes/Andys_SSD/'
EXTENSIONS = {'.mp4', '.mov', '.jpg', '.jpeg', '.png', '.pdf'}
VIDEO_EXTENSIONS = {'.mp4', '.mov'}

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
                if any(item.endswith(ext) for ext in EXTENSIONS):
                    items['files'].append(item)
        return render_template('index.html', items=items, path=subpath)
    

@app.route('/handle/<path:filePath>')
def handle(filePath):

    fileName = os.path.basename(filePath)

    _, ext = os.path.splitext(fileName)

    ext = ext.lower()

    if ext in VIDEO_EXTENSIONS:
        return render_template('video.html', path = filePath, fileName = fileName)
    elif ext == '.pdf':
       return send_from_directory(os.path.dirname(os.path.join(BASE_FOLDER, filePath)), fileName, as_attachment=False)

    return render_template('video.html', filePath, fileName)

# Video manip
@app.route('/video/<path:filePath>')
def video(filePath):

    filePath = os.path.join(BASE_FOLDER, filePath)

    # Guess MIME type based on file extension, default to 'video/mp4'
    mime_type, _ = mimetypes.guess_type(os.path.basename(filePath))
    if mime_type is None:
        mime_type = 'video/mp4'  # Default MIME type

    range_header = request.headers.get('Range', None)
    if not range_header:  # Browser doesn't support range requests
        print('Browser doesn\'t support range requests')
        return Response(stream_with_context(generate_video(filePath)), mimetype=mime_type)

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
                  mimetype=mime_type,
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