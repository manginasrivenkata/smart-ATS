import streamlit as st
import google.generativeai as gi
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from wordcloud import wordcloud
import matplotlib.pyplot as mp
import seaborn as sea

st.set_page_config(page_title =" ATS RESUME EXPERT", layout ='wide')
load_dotenv()
gi.configure(api_key=os.getenv("api_key"))
def get_gemini_response(prompt,pdf_content, jd):
 model = gi.GenerativeModel('gemini-pro')
 response = model.generate_content([prompt, pdf_content, jd])
 return response.text
    
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text
def calculate_match(prompt, pdf_content, jd):
    response = get_gemini_repsonse(prompt, pdf_content, jd)
    match_percentage_str = response.split('\n')[0].split(':')[1].strip()
    try:
        match_percentage = float(match_percentage_str.replace('%', ''))  # Remove '%' and convert to float
    except ValueError:
        match_percentage = 0
    return match_percentage, response

left, right = st.columns([1.3,1])

with left:
    st.title("Smart ATS")
    st.text("Improve Your Resume ATS")
    jd = st.text_area("Paste the Job Description")
    uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True, help="Please upload PDF resumes")

    submit = st.button("Submit")





# st.title("hello world")
# st.write("this is me")

 