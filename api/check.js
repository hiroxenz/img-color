import Jimp from "jimp";

// Convert RGB → HSV (scaled 0-255 seperti OpenCV)
function rgbToHsv(r, g, b) {
  r /= 255; g /= 255; b /= 255;

  let max = Math.max(r, g, b),
      min = Math.min(r, g, b);
  let h, s, v = max;
  let d = max - min;

  s = max === 0 ? 0 : d / max;

  if (max === min) {
    h = 0;
  } else {
    switch (max) {
      case r:
        h = (g - b) / d + (g < b ? 6 : 0);
        break;
      case g:
        h = (b - r) / d + 2;
        break;
      case b:
        h = (r - g) / d + 4;
        break;
    }
    h /= 6;
  }

  return {
    h: Math.round(h * 255),
    s: Math.round(s * 255),
    v: Math.round(v * 255)
  };
}

export default async function handler(req, res) {
  try {
    const { imageUrl } = req.query;

    if (!imageUrl)
      return res.status(400).json({ error: "imageUrl is required" });

    const img = await Jimp.read(imageUrl);

    let matchCount = 0;
    let totalPixels = img.bitmap.width * img.bitmap.height;

    // HSV range (sama seperti Python kamu)
    const low = { h: 30, s: 120, v: 0 };
    const high = { h: 255, s: 255, v: 255 };

    img.scan(0, 0, img.bitmap.width, img.bitmap.height, function (x, y, idx) {
      const r = this.bitmap.data[idx + 0];
      const g = this.bitmap.data[idx + 1];
      const b = this.bitmap.data[idx + 2];

      const hsv = rgbToHsv(r, g, b);

      if (
        hsv.h >= low.h && hsv.h <= high.h &&
        hsv.s >= low.s && hsv.s <= high.s &&
        hsv.v >= low.v && hsv.v <= high.v
      ) {
        matchCount++;
      }
    });

    // Jika banyak pixel sesuai → valid
    const percentage = matchCount / totalPixels;
    const isValid = percentage > 0.02; // threshold 2%

    res.status(200).json({
      valid: isValid,
      matchedPixels: matchCount,
      totalPixels,
      percentage
    });

  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
