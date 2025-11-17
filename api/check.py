from flask import Flask, request, jsonify
import base64
import cv2
import numpy as np

app = Flask(__name__)

@app.route('/api/check', methods=['POST'])
def check_image():
    data = request.json

    if not data or "image" not in data:
        return jsonify({"status": False, "msg": "Missing image field"}), 400

    try:
        # Decode Base64 → Image
        img_data = base64.b64decode(data["image"])
        img_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"status": False, "msg": "Invalid image"}), 400

        # ---- ANALISA: cek warna background + warna text (contoh sederhana) ----
        # ambil pixel tengah
        h, w, _ = img.shape
        mid_pixel = img[h//2, w//2].tolist()      # [B,G,R]

        # asumsikan background warna dominan
        avg_color = np.mean(img.reshape(-1, 3), axis=0).tolist()  # [B,G,R]

        return jsonify({
            "status": True,
            "info": {
                "middle_pixel_BGR": mid_pixel,
                "average_color_BGR": avg_color
            }
        })

    except Exception as e:
        return jsonify({"status": False, "msg": str(e)}), 500


def handler(event, context):
    return app(event, context)
