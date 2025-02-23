import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from PIL import Image

# Initialize Groq client
client = Groq(api_key='')

# Set Streamlit page config
st.set_page_config(page_title="Bureau of Indian Standards - AI PDF Summarizer", layout="wide", page_icon="📄")

# Custom CSS for better alignment and UI
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        html, body, [class*="st"] {
            font-family: 'Inter', sans-serif;
            color: #333;
        }
        .stApp {
            background-color: #f8f9fa;
        }
        .header-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
            padding: 10px;
            background: linear-gradient(to right, #003366, #00509E); 
            color: white;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .header-container img {
            width: 60px;
            height: auto;
        }
        .header-container h1 {
            font-size: 26px;
            margin: 0;
            font-weight: 600;
        }
        .summary-box {
            background: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            margin-top: 20px;
        }
        .preview-box {
            background: #e9ecef;
            padding: 10px;
            border-radius: 8px;
            font-size: 14px;
            color: #444;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Header Section with BIS Logo and Title
st.markdown("""
    <div class="header-container">
        <img src="https://upload.wikimedia.org/wikipedia/commons/f/f8/Bureau_of_Indian_Standards_Logo.svg">
        <h1>Bureau of Indian Standards</h1>
    </div>
""", unsafe_allow_html=True)

# Sidebar UI
st.sidebar.header("📂 Upload Your PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
option = st.sidebar.radio("Select Action", ["📄 Summarize PDF", "❓ Ask a Question"])

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file, chunk_size=2000):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)], text[:200]  # Return chunks & preview text

# Summarization function
def summarize_chunk(chunk):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": "Provide a detailed and structured summary."},
                      {"role": "user", "content": chunk}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

# Function to summarize all text chunks
def summarize_text(chunks):
    with st.spinner("Summarizing PDF... Please wait."):
        summaries = [summarize_chunk(chunk) for chunk in chunks]
    return " ".join(summaries)

# Question Answering function
def ask_question(chunks, question):
    answers = []
    with st.spinner("Searching for the answer... Please wait."):
        for chunk in chunks:
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Answer the question based on the given text."},
                        {"role": "user", "content": f"Context: {chunk}\nQuestion: {question}"}
                    ],
                    model="llama-3.1-8b-instant",
                )
                answers.append(response.choices[0].message.content)
            except Exception as e:
                answers.append(f"Error: {e}")
    return " ".join(answers)

# Main Content Area
if uploaded_file:
    text_chunks, preview_text = extract_text_from_pdf(uploaded_file)
    st.sidebar.success("✅ PDF Uploaded Successfully!")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📜 PDF Preview")
        st.markdown(f"<div class='preview-box'>{preview_text}...</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("🔍 Processed Results")
        if option == "📄 Summarize PDF":
            if st.button("🔎 Generate Summary"):
                summary = summarize_text(text_chunks)
                st.markdown("### 📑 Summary")
                st.markdown(f"<div class='summary-box'>{summary}</div>", unsafe_allow_html=True)
        else:
            question = st.text_input("💬 Ask a question about the PDF:")
            if st.button("🤖 Get Answer"):
                answer = ask_question(text_chunks, question)
                st.markdown("### 💡 Answer")
                st.markdown(f"<div class='summary-box'>{answer}</div>", unsafe_allow_html=True)