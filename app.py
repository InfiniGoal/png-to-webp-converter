from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import zipfile

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = "converted"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")


# 🔹 Single File Convert
@app.route("/convert", methods=["POST"])
def convert_image():
    file = request.files["image"]

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    img = Image.open(input_path)
    if img.mode != "RGB":
        img = img.convert("RGB")

    output_filename = file.filename.rsplit(".", 1)[0] + ".webp"
    output_path = os.path.join(CONVERTED_FOLDER, output_filename)

    img.save(output_path, "WEBP", quality=80, method=6)

    return send_file(output_path, as_attachment=True)


# 🔹 Folder / Multiple Images Convert
@app.route("/convert-folder", methods=["POST"])
def convert_folder():
    files = request.files.getlist("images")

    zip_path = os.path.join(CONVERTED_FOLDER, "converted_images.zip")

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files:
            if file.filename.endswith(".png"):
                input_path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(input_path)

                img = Image.open(input_path)
                if img.mode != "RGB":
                    img = img.convert("RGB")

                output_filename = file.filename.rsplit(".", 1)[0] + ".webp"
                output_path = os.path.join(CONVERTED_FOLDER, output_filename)

                img.save(output_path, "WEBP", quality=80, method=6)

                zipf.write(output_path, output_filename)

    return send_file(zip_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)