import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
from PIL import Image


client = Groq(api_key='')

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(stream=pdf_path.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def summarize_text(text):
    try:
        summary_response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following text: {text}"
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return summary_response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"

def ask_question(context, question):
    try:
        answer_response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": f"Context: {context} Question: {question}"
                }
            ],
            model="llama-3.1-8b-instant",
        )
        return answer_response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {e}"


st.title("Intelligent Text Summarization...")
image = Image.open('1.jpeg')
st.image(image, use_container_width=True, width=800)

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file is not None:
    pdf_text = extract_text_from_pdf(uploaded_file)
    
    st.subheader("Text Extracted from PDF:")
    st.write(pdf_text[:500])  

    if st.button("Summarize Text"):
        with st.spinner('Summarizing...'):
            summary = summarize_text(pdf_text)
        st.subheader("Summary:")
        st.write(summary)

    question = st.text_input("Ask a question about the PDF:")
    if question:
        with st.spinner('Getting the answer...'):
            answer = ask_question(pdf_text, question)
        st.subheader("Answer:")
        st.write(answer)