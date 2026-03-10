from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import zipfile
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)


# 🔹 Function: Convert PNG → WebP (Keep Transparency)
def png_to_webp_keep_transparency(input_path, output_path):
    img = Image.open(input_path)

    # Preserve transparency if present
    if img.mode not in ("RGBA", "RGB"):
        img = img.convert("RGBA")

    img.save(output_path, "WEBP", lossless=True, method=6)


@app.route("/")
def home():
    return render_template("index.html")


# 🔹 Single Image Convert
@app.route("/convert", methods=["POST"])
def convert_image():
    file = request.files["image"]

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)

    file.save(input_path)

    output_filename = filename.rsplit(".", 1)[0] + ".webp"
    output_path = os.path.join(CONVERTED_FOLDER, output_filename)

    png_to_webp_keep_transparency(input_path, output_path)

    return send_file(output_path, as_attachment=True)


# 🔹 Folder / Multiple Image Convert
@app.route("/convert-folder", methods=["POST"])
def convert_folder():
    files = request.files.getlist("images")

    zip_path = os.path.join(CONVERTED_FOLDER, "converted_images.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:

            if not file.filename.lower().endswith(".png"):
                continue

            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)

            file.save(input_path)

            output_filename = filename.rsplit(".", 1)[0] + ".webp"
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)

            png_to_webp_keep_transparency(input_path, output_path)

            zipf.write(output_path, output_filename)

    return send_file(zip_path, as_attachment=True)


if __name__ == "__main__":
   app.run(debug=True, port=5001)