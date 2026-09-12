from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

try:
    font = ImageFont.truetype("arial.ttf", 20)
except OSError:
    font = ImageFont.load_default()

folder = Path("data/sample_patient_01")
for name in ["doctor_notes", "lab_report", "prescription"]:
    text = (folder / f"{name}.txt").read_text()
    img = Image.new("RGB", (1000, 900), color="white")
    draw = ImageDraw.Draw(img)
    draw.multiline_text((40, 40), text, fill="black", font=font, spacing=10)
    output_path = folder / f"{name}_scan.png"
    img.save(output_path)
    print(f"Saved: {output_path}")