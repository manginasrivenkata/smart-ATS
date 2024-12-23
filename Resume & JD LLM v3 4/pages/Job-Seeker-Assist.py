import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="ATS Resume Expert", layout='wide')

load_dotenv() ## load all our environment variables

genai.configure(api_key=os.getenv("api_key"))

def get_gemini_repsonse(prompt, pdf_content):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content([prompt, pdf_content])
    return response.text

def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page = reader.pages[page]
        text += str(page.extract_text())
    return text


seeker_prompt = """
As an experienced ATS Resume Parser assistant, your objective is to review the below pasted resume content and provide a comprehensive summary enriched with keywords and recommendations for suitable job applications. 
Your aim is to provide a response that allows the individual to leverage this analysis to refine the resume and maximize career prospects.
The response should include an in-depth analysis of the resume, highlighting key areas of strength and areas for improvement. Additionally, provide the top five job roles the individual can apply for in a step-by-step format as follows:
1: Resume Summary: {}
2: Top Keywords: {}
3: Recommended Job Roles: {}
"""




left, right = st.columns([1.3,1])

with left:
    st.title("Job Seeker - Smart ATS")
    st.text("Improve Your Resume ATS")
    uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload PDF resume")

    submit = st.button("Submit")

    if submit:
        if uploaded_file is not None:
            pdf_content = input_pdf_text(uploaded_file)
            response = get_gemini_repsonse(seeker_prompt, pdf_content)
            st.write(response)

            with right:
                # Generate word cloud for resume summary
                summary_start_idx = response.find("Resume Summary:") + len("Resume Summary:")
                summary_end_idx = response.find("=======", summary_start_idx)
                summary = response[summary_start_idx:summary_end_idx].strip()

                fig, ax = plt.subplots(figsize=(8, 6))
                wordcloud = WordCloud(width=800, height=400, background_color="white").generate(summary)
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                ax.set_title(f"Top words in the resume: {uploaded_file.name}")
                st.pyplot(fig)
            