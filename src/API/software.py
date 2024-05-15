import json
from flask import Flask, flash, jsonify, request, redirect
import requests
from werkzeug.utils import secure_filename
from pathlib import Path


from ACT.src.act import ACTTree
from log.log import Log


UPLOAD_FOLDER = (
    Path(__file__).parent.parent.parent / "uploads"
)  # Path to the uploads folder
JSON_FOLDER = Path(__file__).parent.parent.parent / "data" / "processed" / "act"
ALLOWED_EXTENSIONS = {"txt", "pdf", "json"}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["JSON_FOLDER"] = JSON_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


logger = Log("software", "software.log")

# ACT routes
@app.route("/software/act", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        # check if the post request has the file part
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = Path(app.config["UPLOAD_FOLDER"]) / "act" / filename
            file.save(save_path)

            logger.info(f"File saved at {save_path}, processing...")

            # Prepare request
            url = "http://127.0.0.1:5000/build-act"
            files = {"file": open(save_path, "rb")}  # Open file in binary mode
            headers = {"Content-Type": "application/pdf"}

            try:
                response = requests.post(url, files=files)
                response.raise_for_status()  # Raise an exception for bad responses (4xx and 5xx)
                return jsonify(response.json())  # Return the response from the webhook

            except requests.exceptions.RequestException as e:
                logger.error(f"Error forwarding to webhook: {e}")
                return f"Error forwarding to webhook: {e}"
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


@app.route("/software/act_webhook", methods=["POST"])
def handle_webhook():
    if request.headers["Content-Type"] == "application/json":
        try:
            json_data = request.get_json()
            act_tree = ACTTree(json_data)  # Assuming you have from_json in ACTTree

            # Now you have the act_tree object, process it as needed
            print(act_tree.print_tree())

            # You might want to validate the ACT tree structure here if required

            # After processing, you can return a suitable response

            logger.info("ACT tree received and processed")
            return jsonify(
                {"status": "success", "message": "ACT tree received and processed"}
            )

        except json.JSONDecodeError as e:
            logger.info(f"Invalid JSON format: {e}")
            return (
                jsonify({"status": "error", "message": f"Invalid JSON format: {e}"}),
                400,
            )
    else:
        logger.info("Unsupported content type")
        return jsonify({"status": "error", "message": "Unsupported content type"}), 415


if __name__ == "__main__":
    # Quick test configuration. Please use proper Flask configuration options
    # in production settings, and use a separate file or environment variables
    # to manage the secret key!

    app.debug = True
    app.run(host="127.0.0.1", port=6000)
