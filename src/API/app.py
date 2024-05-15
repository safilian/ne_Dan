from flask import Flask, flash, request, redirect, session
from werkzeug.utils import secure_filename
from pathlib import Path


from ACT.src.act import ACTTree
from ACT.src.text_validity_check import get_sections_from_file, validate_section_order
from job.sample_job import enqueue_sample_job


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


# ACT routes
@app.route("/build-act", methods=["GET", "POST"])
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
            try:
                act_tree = ACTTree(save_path)
            except Exception as e:
                return f"Error: {e}"
            export_path = Path(app.config["JSON_FOLDER"]) / filename
            act_tree.export_json(export_path.with_suffix(".json"))
            # act_tree.generate_goal_using_job(export_path.with_suffix(".json"))
            enqueue_sample_job(str(export_path.with_suffix(".json")))
            return act_tree.json_serial()
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    """


# Sample job route
@app.route("/job", methods=["GET", "POST"])
def run_job():
    if request.method == "POST":
        # Run the job
        if "input_str" in request.form:
            input_str = request.form["input_str"]
            enqueue_sample_job(input_str)
            return "Job enqueued"
        return "Job is running"
    return """
    <!doctype html>
    <title>Run Job</title>
    <h1>Run Job</h1>
    <form method=post>
    input_str: <input type=text name=input_str>
      <input type=submit value=Run>
    </form>
    """


# Text validity check route
@app.route("/text-validity-check", methods=["GET", "POST"])
def text_validity_check():
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
            save_path = Path(app.config["UPLOAD_FOLDER"]) / "text" / filename
            file.save(save_path)
            sections = get_sections_from_file(save_path)
            is_valid = validate_section_order(sections)
            return f"Text is valid: {is_valid}"
    return """
    <!doctype html>
    <title>Text Validity Check</title>
    <h1>Text Validity Check</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Check>
    </form>
    """


if __name__ == "__main__":
    app.debug = True
    app.run()
