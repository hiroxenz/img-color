import json
import requests
from io import BytesIO
from PIL import Image

def rgb_to_hsv(r, g, b):
    r /= 255
    g /= 255
    b /= 255

    maxc = max(r, g, b)
    minc = min(r, g, b)
    diff = maxc - minc

    if diff == 0:
        h = 0
    elif maxc == r:
        h = (g - b) / diff + (6 if g < b else 0)
    elif maxc == g:
        h = (b - r) / diff + 2
    else:
        h = (r - g) / diff + 4
    h = (h / 6) * 255

    s = 0 if maxc == 0 else (diff / maxc) * 255
    v = maxc * 255

    return int(h), int(s), int(v)


def handler(request):
    try:
        query = request.get("query", {})
        image_url = query.get("imageUrl")

        if not image_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "imageUrl required"})
            }

        # Download image
        resp = requests.get(image_url)
        img = Image.open(BytesIO(resp.content)).convert("RGB")

        width, height = img.size
        total_pixels = width * height
        match_pixels = 0

        low = (30, 120, 0)
        high = (255, 255, 255)

        pixels = img.load()

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y]
                h, s, v = rgb_to_hsv(r, g, b)

                if (
                    low[0] <= h <= high[0] and
                    low[1] <= s <= high[1] and
                    low[2] <= v <= high[2]
                ):
                    match_pixels += 1

        percentage = match_pixels / total_pixels
        valid = percentage > 0.02

        return {
            "statusCode": 200,
            "body": json.dumps({
                "valid": valid,
                "matchedPixels": match_pixels,
                "totalPixels": total_pixels,
                "percentage": percentage
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
