from PIL import Image
import os

src = "/Users/pinea/cv/cv/static/cv/images/IMG_3343.JPG"
img = Image.open(src)

# ── Crop parameters ──────────────────────────────────────────────
# Move center_x left to bring in your left shoulder,
# or increase crop_w to widen the frame (will also shift both edges out).
center_x = 2900   # horizontal center of crop (0 = far left, 4752 = far right)
top       = 100   # pixels from top of original (increase to trim headroom)
crop_w    = 2000  # width of crop in original pixels (3:4 → height = crop_w * 4/3)
# ─────────────────────────────────────────────────────────────────

crop_h = round(crop_w * 4 / 3)
left   = center_x - crop_w // 2
right  = left + crop_w
bottom = top + crop_h

print(f"Original: {img.size}")
print(f"Crop box: ({left}, {top}, {right}, {bottom})  →  {crop_w}×{crop_h}")

cropped = img.crop((left, top, right, bottom))
resized = cropped.resize((700, 933), Image.LANCZOS)

out_path = "/Users/pinea/cv/cv/static/cv/images/cv-portrait.jpg"
resized.save(out_path, "JPEG", quality=82, optimize=True, progressive=True)
print(f"Saved: {out_path}  ({os.path.getsize(out_path) / 1024:.0f} KB)")