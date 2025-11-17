from flask import Flask, request, jsonify
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)

@app.route("/api/check")
def check():
    image_url = request.args.get("image")
    
    if not image_url:
        return jsonify({"error": "image parameter is required"}), 400

    try:
        # download image
        img_bytes = requests.get(image_url).content
        img = Image.open(BytesIO(img_bytes)).convert("RGB")
        img_np = np.array(img)

        # convert ke HSV
        hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)

        low = np.array([30, 120, 0])
        high = np.array([255, 255, 255])
        mask = cv2.inRange(hsv, low, high)

        match_count = int(np.sum(mask > 0))
        total_pixels = mask.size
        percentage = match_count / total_pixels
        is_valid = percentage > 0.02  # 2%

        return jsonify({
            "valid": is_valid,
            "matchedPixels": match_count,
            "totalPixels": total_pixels,
            "percentage": percentage
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# WSGI handler untuk Vercel
def handler(request, context):
    return app(request, context)
