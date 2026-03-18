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


# 🔹 Convert Image → WebP (Compressed)
def image_to_webp(input_path, output_path):
    img = Image.open(input_path)

    # Resize large images (reduce size MB → KB)
    img.thumbnail((1200, 1200))

    # Handle transparency
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
    else:
        img = img.convert("RGB")

    # Save compressed WebP
    img.save(output_path, "WEBP", quality=80, method=6)


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

    image_to_webp(input_path, output_path)

    # Delete original file
    if os.path.exists(input_path):
        os.remove(input_path)

    return send_file(output_path, as_attachment=True)


# 🔹 Folder / Multiple Image Convert
@app.route("/convert-folder", methods=["POST"])
def convert_folder():
    files = request.files.getlist("images")

    if not files:
        return "No files uploaded"

    # 🔥 Get folder name from first file
    first_file = files[0].filename

    if "/" in first_file:
        folder_name = first_file.split("/")[0]
    else:
        folder_name = "converted_images"

    folder_name = secure_filename(folder_name)

    zip_path = os.path.join(CONVERTED_FOLDER, f"{folder_name}.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:

            if not file.filename.lower().endswith((".png", ".jpg", ".jpeg")):
                continue

            # Remove folder path
            filename = secure_filename(os.path.basename(file.filename))

            input_path = os.path.join(UPLOAD_FOLDER, filename)

            # Save original file
            file.save(input_path)

            # Convert
            output_filename = filename.rsplit(".", 1)[0] + ".webp"
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)

            image_to_webp(input_path, output_path)

            # Add to ZIP
            zipf.write(output_path, output_filename)

            # 🔥 Delete original file
            if os.path.exists(input_path):
                os.remove(input_path)

    return send_file(zip_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, port=5001)