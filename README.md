# Exam Parser API

Exam Parser API is a **Flask-based web service** that automates the extraction and structuring of exam content from PDF and Word documents. It is designed to convert exams containing multiple-choice, essay, or short-answer questions into **well-structured JSON** for easy analysis, evaluation, or integration with other educational systems.

This API is ideal for **educators, academic researchers, and developers** who want to automate exam processing, scoring, or analytics workflows.

---

## Key Features

* **Multi-format support:** Accepts PDF and DOCX files as input.
* **Structured JSON output:** Generates consistent JSON including `question_number`, `type`, `question`, `options`, and `answer` for four different models (A, B, C, D).
* **Question type flexibility:** Supports multiple-choice, essay, and short-answer questions.
* **Automated cleanup:** Uploaded files are automatically deleted after processing.
* **API-first design:** Easily integrates with other applications via HTTP endpoints.
* **Scalable architecture:** Can be extended with additional parsing logic or AI-based processing for complex exams.

---

## API Endpoints

### 1. Health Check

```http
GET /
```

**Response:**

```json
{
  "status": "success",
  "message": "Exam Parsing API is running successfully"
}
```

### 2. Parse Exam File

```http
POST /parse-exam
```

**Form-data:**

* `file` → PDF or DOCX exam file.

**Response Example:**

```json
{
  "subject": "Data Center Technologies",
  "instructor": "Dr. John Doe",
  "models": {
    "A": [
      {
        "question_number": 1,
        "type": "Essay",
        "question": "What are the core components of a data center?",
        "options": null,
        "answer": "1. Application ... 5. Storage"
      }
    ],
    "B": [...],
    "C": [...],
    "D": [...]
  }
}
```

---

## Project Structure

```
Exam-Parser/
├── FileLoader.py       # Functions to read PDF and Word files
├── TextCleaner.py      # Functions to clean extracted text
├── ExamParser.py       # Core parsing logic to generate structured JSON
├── ExamCleaner.py      # Validates and formats the JSON output
├── app.py              # Flask API application
├── requirements.txt    # Python dependencies
├── uploads/            # Temporary folder for uploaded files
└── README.md
```

---

## Setup & Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/exam-parser-api.git
cd exam-parser-api
```

2. **Create and activate a virtual environment:**

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Run the API:**

```bash
python app.py
```

Access the API locally at:

```
http://127.0.0.1:5000
```

---

## Testing the API

You can test the API using **Postman** or **cURL**:

```bash
curl -X POST http://127.0.0.1:5000/parse-exam \
-F "file=@example_exam.pdf"
```

---

## Notes

* JSON output is always structured with **Models A-D**.
* Supports both **essay and multiple-choice questions** (options are optional).
* Automatically deletes uploaded files after processing to keep the system clean.
* Easily extendable to include **AI-based parsing** or **advanced question validation**.

---

## License

This project is licensed under the **MIT License**.
© Mohamed Emad
