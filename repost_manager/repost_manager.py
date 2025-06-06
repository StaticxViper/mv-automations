from flask import Flask, request, send_from_directory
import os, subprocess, requests
from uuid import uuid4

app = Flask(__name__)
UPLOAD_DIR = "/home/pi/video_app/static"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/')
def home():
    return "Video Processor Online"

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    url = data.get("video_url")
    if not url:
        return "Missing video_url", 400

    uid = uuid4().hex
    input_path = f"{UPLOAD_DIR}/in_{uid}.mp4"
    output_path = f"{UPLOAD_DIR}/out_{uid}.mp4"

    try:
        with open(input_path, "wb") as f:
            r = requests.get(url, stream=True)
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", input_path],
            stdout=subprocess.PIPE
        )
        w, h = map(int, result.stdout.decode().strip().split("x"))
        new_w, new_h = int(w * 0.99), int(h * 0.99)

        cmd = [
            "ffmpeg", "-i", input_path,
            "-vf", f"scale={new_w}:{new_h},pad={w}:{h}:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy", output_path
        ]
        subprocess.run(cmd, check=True)

        return f"http://your.pi.ip.addr:5000/static/out_{uid}.mp4"
    except Exception as e:
        return str(e), 500

@app.route('/static/<path:filename>')
def serve_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)
