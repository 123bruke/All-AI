import os, uuid, shutil
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from utils import copilot_api, gpt_api, medical_utils
import json, re

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","gif","bmp","tiff","webp"}
MAX_CONTENT_LENGTH = 50*1024*1024

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
app.secret_key = os.getenv("FLASK_SECRET_KEY","super-secret-change-me")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS

def save_files(files):
    saved = []
    for f in files:
        if f and allowed_file(f.filename):
            fname = secure_filename(f.filename)
            unique_name = f"{uuid.uuid4().hex}_{fname}"
            path = os.path.join(app.config["UPLOAD_FOLDER"], unique_name)
            f.save(path)
            saved.append(path)
    return saved

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question","").strip()
    files = request.files.getlist("images")
    if not question:
        flash("Please provide a question.")
        return redirect(url_for("index"))

    saved_paths = save_files(files)

    if not medical_utils.appears_medical_text_simple(question):
        verify_prompt = f"You are a classifier: Return MEDICAL or NON-MEDICAL only. Input: {question}"
        verify_resp = gpt_api.ask_gpt5(verify_prompt)
        classification = verify_resp.get("text","").upper()
        if "MEDICAL" not in classification:
            for p in saved_paths: os.remove(p)
            return "<h2>Non-medical question denied.</h2>", 400

    copilot_info = copilot_api.analyze_images(saved_paths)

    combined_context = f"User question: {question}\n\nImage analysis:\n"
    for info in copilot_info:
        combined_context += f"- {info['caption']}, objects: {','.join(info['objects'])}\n"

    prompt = f"Provide JSON response with recommendation, next_steps, youtube, website, note. Context:\n{combined_context}"
    gpt_resp = gpt_api.ask_gpt5(prompt)
    assistant_text = gpt_resp.get("text","")

    parsed = None
    try:
        m = re.search(r"(\{.*\})", assistant_text, re.S)
        if m: parsed = json.loads(m.group(1))
    except: parsed=None

    if not parsed:
        rec_obj = medical_utils.choose_recommendation(question)
        parsed = {
            "recommendation": rec_obj["rec"],
            "next_steps": "Seek medical care if symptoms worsen.",
            "youtube": rec_obj["youtube"],
            "website": rec_obj["website"],
            "note": "Fallback recommendation"
        }

    photo_url = url_for("uploaded_file", filename=os.path.basename(saved_paths[0])) if saved_paths else None

    html = f"<h2>Results</h2><p>{parsed['recommendation']}</p><p>Next steps: {parsed['next_steps']}</p>"
    html += f"<p>YouTube: <a href='{parsed['youtube']}' target='_blank'>{parsed['youtube']}</a></p>"
    html += f"<p>Website: <a href='{parsed['website']}' target='_blank'>{parsed['website']}</a></p>"
    html += "<ul>Image analysis:"
    for info in copilot_info: html += f"<li>{info['caption']}</li>"
    html += "</ul>"
    if photo_url: html += f"<img src='{photo_url}' style='max-width:320px;border-radius:8px;'/>"
    html += "<p>Note: Informational only. Not a substitute for medical care.</p>"
    html += "<p><a href='/'>Ask another question</a></p>"
    return html

@app.route("/admin/clear_uploads", methods=["POST"])
def clear_uploads():
    try:
        shutil.rmtree(app.config["UPLOAD_FOLDER"])
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        return "Cleared",200
    except Exception as e:
        return str(e),500

if __name__ == "__main__":
    print("Visit http://127.0.0.1:5000")
    app.run(debug=True,host="0.0.0.0",port=int(os.getenv("PORT","5000")))
