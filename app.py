import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

from FileLoader import read_pdf_file, read_word_file
from TextCleaner import clean_text
from ExamParser import parse_exam
from JSONBulider import clean_and_validate_exam

# ========================
# Configuration
# ========================
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ========================
# Utility Functions
# ========================
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================
# Routes
# ========================

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "success",
        "message": "Exam Parsing API is running successfully"
    }), 200


@app.route("/parse-exam", methods=["POST"])
def parse_exam_api():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    try:
        if filename.lower().endswith(".pdf"):
            raw_text = read_pdf_file(filepath)
        else:
            raw_text = read_word_file(filepath)

        if not raw_text or len(raw_text.strip()) < 50:
            return jsonify({"error": "File contains too little readable text"}), 400

        cleaned_text = clean_text(raw_text)
        exam_json_text = parse_exam(cleaned_text)

        if not exam_json_text or not exam_json_text.strip():
            return jsonify({"error": "LLM returned empty response"}), 500

        exam_data = clean_and_validate_exam(exam_json_text)
        return jsonify(exam_data), 200

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)


# ========================
# App Entry Point
# ========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

