from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import pdfplumber

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Load the Pegasus model
model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text

def summarize_text(text):
    # Truncate text to avoid exceeding token limit
    inputs = tokenizer(
        text, return_tensors="pt", truncation=True, max_length=1024
    )
    
    if len(inputs["input_ids"][0]) == 0:
        return "Error: Input text is too short or not properly tokenized."

    summary_ids = model.generate(
        **inputs,
        max_length=250,
        min_length=50,
        length_penalty=2.0,
        num_beams=4,
        early_stopping=True
    )

    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

@app.route("/summarize", methods=["POST"])
def summarize():
    """API endpoint to summarize a document."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    text = extract_text_from_pdf(file)
    if not text:
        return jsonify({"error": "No text found in the document"}), 400

    summary = summarize_text(text)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)