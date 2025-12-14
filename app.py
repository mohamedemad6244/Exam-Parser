import os
import json
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS

from FileLoader import read_pdf_file, read_word_file
from TextCleaner import clean_text
from ExamParser import parse_exam , parse_exam_test ,check_gemini_api
from JSONBulider import clean_and_validate_exam

# ========================
# Configuration
# ========================
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "docx"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

CORS(app)

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
    """
    Simple GET route to check if server is running and parsing route works.
    Returns dummy exam JSON.
    """
    try:
        # Use dummy parser instead of real Gemini API
        exam_json = parse_exam_test()
        return jsonify({"status": "success", "message": "API is running", "exam_preview": json.loads(exam_json)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/check-gemini", methods=["GET"])
def check_gemini():
    """
    Route to check if Gemini API is reachable and working.
    """
    result = check_gemini_api()
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code



@app.route("/parse-exam", methods=["POST"])
def parse_exam_route():
    """
    POST /parse-exam
    Body: form-data with key 'file' (PDF or DOCX)
    Returns: structured JSON exam output
    """
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
        # Read file content
        if filename.lower().endswith(".pdf"):
            raw_text = read_pdf_file(filepath)
        else:
            raw_text = read_word_file(filepath)

        if not raw_text or len(raw_text.strip()) < 50:
            return jsonify({"error": "File contains too little readable text"}), 400

        cleaned_text = clean_text(raw_text)

        # Check Gemini API before parsing
        gemini_status = check_gemini_api()
        if not gemini_status["success"]:
            return jsonify({"error": "Gemini API not working", "details": gemini_status}), 500

        # Parse the exam using Gemini
        exam_json_text = parse_exam(cleaned_text)

        if not exam_json_text or not exam_json_text.strip():
            return jsonify({"error": "Gemini returned empty response"}), 500

        # Clean and validate JSON structure
        exam_data = clean_and_validate_exam(exam_json_text)

        return jsonify(exam_data), 200

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)





# ========================
# App Entry Point
# ========================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )






