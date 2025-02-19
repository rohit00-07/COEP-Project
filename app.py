import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from PIL import Image
import concurrent.futures

client = Groq(api_key='')

# Function to extract text from PDF in chunks
def extract_text_from_pdf(pdf_path, chunk_size=2000):
    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    
    # Splitting text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return chunks

# Summarizing function (handles large PDFs)
def summarize_chunk(chunk):
    try:
        summary_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Summarize the following text in short: {chunk}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return summary_response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def summarize_text(text_chunks):
    summaries = []
    try:
        # Using ThreadPoolExecutor to parallelize the summarization process
        with concurrent.futures.ThreadPoolExecutor() as executor:
            summaries = list(executor.map(summarize_chunk, text_chunks))
        return " ".join(summaries)  # Joining all summaries
    except Exception as e:
        return f"An error occurred: {e}"

# Question Answering function (can also be parallelized)
def ask_question(context_chunks, question):
    answers = []
    try:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            answers = list(executor.map(lambda chunk: ask_question_chunk(chunk, question), context_chunks))
        return " ".join(answers)
    except Exception as e:
        return f"An error occurred: {e}"

def ask_question_chunk(chunk, question):
    try:
        answer_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context: {chunk} Question: {question}"}
            ],
            model="llama-3.1-8b-instant",
        )
        return answer_response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

st.title("Intelligent Text Summarization")
image = Image.open('1.jpeg')
st.image(image, use_container_width=True, width=800)

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    pdf_chunks = extract_text_from_pdf(uploaded_file)
    
    st.subheader("Preview of Extracted Text:")
    st.write(pdf_chunks[0][:500])  # Show only the first chunk preview

    if st.button("Summarize Text"):
        with st.spinner('Summarizing...'):
            summary = summarize_text(pdf_chunks)
        st.subheader("Summary:")
        st.write(summary)

    question = st.text_input("Ask a question about the PDF:")
    if question:
        with st.spinner('Getting the answer...'):
            answer = ask_question(pdf_chunks, question)
        st.subheader("Answer:")
        st.write(answer)