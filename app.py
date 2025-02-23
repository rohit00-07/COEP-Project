import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from PIL import Image
import concurrent.futures

# Initialize Groq client (ensure API key is set)
client = Groq(api_key='')

# Set Streamlit page config
st.set_page_config(page_title="PDF Summarizer & QA", layout="wide", page_icon="📄")

# Custom CSS for professional look
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        html, body, [class*="st"] {
            font-family: 'Inter', sans-serif;
            color: #333333;
        }
        .main {
            background-color: #f4f4f4;
            padding: 20px;
        }
        .stSidebar {
            background-color: #1C1C1C !important;
            color: white !important;
            padding: 20px !important;
            border-radius: 8px;
        }
        .stSidebar h1, .stSidebar h2, .stSidebar h3 {
            color: #FFD700 !important;
            text-align: center;
        }
        .stButton>button {
            background-color: #007BFF !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 10px !important;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3 !important;
        }
        .stTextInput>div>div>input, .stTextArea>div>textarea {
            border-radius: 8px !important;
            border: 2px solid #007BFF !important;
            padding: 8px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Add a main heading
st.title("📘 Advanced PDF Summarizer & Question Answering")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file, chunk_size=2000):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = "".join([page.get_text() for page in doc])
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Summarization function
def summarize_chunk(chunk):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "system", "content": "Summarize concisely."},
                      {"role": "user", "content": chunk}],
            model="llama-3.1-8b-instant",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"

def summarize_text(chunks):
    with st.spinner("Summarizing PDF... Please wait."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return " ".join(executor.map(summarize_chunk, chunks))

# Sidebar for file upload and options
st.sidebar.header("📂 Upload Your PDF")
uploaded_file = st.sidebar.file_uploader("Choose a PDF file", type="pdf")
option = st.sidebar.radio("Select Action", ["📄 Summarize PDF", "❓ Ask a Question"])

if uploaded_file:
    text_chunks = extract_text_from_pdf(uploaded_file)
    st.sidebar.success("✅ PDF Uploaded Successfully!")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📜 PDF Preview")
        st.text_area("Extracted Text", "\n".join(text_chunks[:2]), height=300)
    
    with col2:
        st.subheader("🔍 Processed Results")
        if option == "📄 Summarize PDF":
            if st.button("🔎 Summarize Now"):
                summary = summarize_text(text_chunks)
                st.markdown("### 📑 Summary")
                st.info(summary)
        else:
            question = st.text_input("💬 Ask a question about the PDF:")
            if st.button("🤖 Get Answer"):
                answer = summarize_text([question + "\n" + chunk for chunk in text_chunks])
                st.markdown("### 💡 Answer")
                st.success(answer)