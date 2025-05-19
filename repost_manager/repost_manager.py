import os
import subprocess
import requests
from flask import Flask, request, jsonify
from urllib.parse import urlparse

app = Flask(__name__)

UPLOAD_DIR = "videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class VideoTransformer:
    def __init__(self, input_path, output_path="output.mp4"):
        self.input_path = input_path
        self.output_path = output_path
        self.filters = []

    def flip_vertical(self):
        self.filters.append("vflip")

    def flip_horizontal(self):
        self.filters.append("hflip")

    def set_aspect_ratio(self, width, height):
        scale = f"scale={width}:{height}:force_original_aspect_ratio=decrease"
        pad = f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        self.filters.extend([scale, pad])

    def add_subtitles(self, subtitle_path):
        self.filters.append(f"subtitles='{subtitle_path}'")

    def run(self):
        filter_str = ",".join(self.filters)
        cmd = [
            "ffmpeg",
            "-i", self.input_path,
            "-vf", filter_str,
            "-c:a", "copy",
            self.output_path
        ]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=True)

def download_file(url, dest_folder):
    filename = os.path.basename(urlparse(url).path)
    local_path = os.path.join(dest_folder, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path

@app.route("/transform", methods=["POST"])
def transform_video():
    data = request.json
    video_url = data.get("video_url")
    subtitle_url = data.get("subtitle_url")
    flip_h = data.get("flip_horizontal", False)
    flip_v = data.get("flip_vertical", False)
    width = data.get("target_width")
    height = data.get("target_height")

    if not video_url:
        return jsonify({"error": "Missing video_url"}), 400

    try:
        input_path = download_file(video_url, UPLOAD_DIR)
        output_path = os.path.join(UPLOAD_DIR, f"processed_{os.path.basename(input_path)}")
        vt = VideoTransformer(input_path, output_path)

        if flip_h:
            vt.flip_horizontal()
        if flip_v:
            vt.flip_vertical()
        if width and height:
            vt.set_aspect_ratio(width, height)
        if subtitle_url:
            subtitle_path = download_file(subtitle_url, UPLOAD_DIR)
            vt.add_subtitles(subtitle_path)

        vt.run()

        return jsonify({
            "status": "success",
            "output_video": f"/static/{os.path.basename(output_path)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve processed videos
@app.route('/static/<filename>')
def serve_file(filename):
    return app.send_static_file(filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
