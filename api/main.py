from flask import Flask, request
import os

UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def cleaner():
    files = os.listdir("uploads")
    for file in files:
        os.remove("uploads/" + file)


@app.route("/resume", methods=["POST"])
def uploadedResume():
    if "file" not in request.args:
        return "No file found"
    file = request.files["file"]

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

        return "File uploaded successfully!"

    return "default, shits wrong"


if __name__ == "__main__":
    # cleaner()
    app.run()
