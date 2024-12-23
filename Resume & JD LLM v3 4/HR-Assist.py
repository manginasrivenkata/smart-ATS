import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns


st.set_page_config(page_title="ATS Resume Expert", layout='wide')

load_dotenv() 

genai.configure(api_key=os.getenv("api_key"))

def get_gemini_repsonse(prompt, pdf_content, jd):
    model = genai.GenerativeModel('gemini-pro')
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

# Prompt Template
hr_prompt = """
You are skilled and experienced ATS(Application Tracking System) parser with a deep understanding of tech field, software engineering, data science, data analyst and big data engineer. 
Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide best assistance for improving thr resumes. Assign the percentage Matching based on Job Description, missing keywords with high accuracy and a concise summary on the provided resume.
I want to have the response in the following structure:
1. JD Match in %:
2. Missing Keywords:
3. Resume Summary:
"""

## streamlit app
left, right = st.columns([1.3,1])

with left:
    st.title("Smart ATS")
    st.text("Improve Your Resume ATS")
    jd = st.text_area("Paste the Job Description")
    uploaded_files = st.file_uploader("Upload Your Resumes", type="pdf", accept_multiple_files=True, help="Please upload PDF resumes")

    submit = st.button("Submit")

    if submit:
        if uploaded_files is not None:
            match_data = []
            responses = []
            for uploaded_file in uploaded_files:
                pdf_content = input_pdf_text(uploaded_file)
                match_percentage, response = calculate_match(hr_prompt, pdf_content, jd)
                match_data.append({"Resume": uploaded_file.name, "Match Percentage": match_percentage})
                responses.append(response)

            # Sort resumes based on match percentage
            sorted_match_data = sorted(match_data, key=lambda x: x["Match Percentage"], reverse=True)

            # Display responses for each resume
            num_resumes = len(uploaded_files)
            columns = st.columns(num_resumes)
            for idx, resume_data in enumerate(sorted_match_data):
                resume_name = resume_data["Resume"]
                response = responses[idx]
                columns[idx].write(f"Response for {resume_name}:")
                columns[idx].write(response)


            with right:

                st.write("Resume Match Rankings:")
                st.dataframe(sorted_match_data, use_container_width=True)


                top_5_resumes = sorted_match_data[:5]
                top_resume_names = [data["Resume"] for data in top_5_resumes]
                top_match_percentages = [data["Match Percentage"] for data in top_5_resumes]
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.barplot(x=top_match_percentages, y=top_resume_names, palette="viridis", ax=ax)
                ax.set_xlabel("Match Percentage")
                ax.set_ylabel("Resume")
                ax.set_title("Top 5 Resumes by Match Percentage")
                st.pyplot(fig)


                for idx, resume_data in enumerate(sorted_match_data):
                    resume_name = resume_data["Resume"]
                    response = responses[idx]

                    summary_start_idx = response.find("Resume Summary:") + len("Resume Summary:")
                    summary_end_idx = response.find("=======", summary_start_idx)
                    summary = response[summary_start_idx:summary_end_idx].strip()

                    fig, ax = plt.subplots(figsize=(8, 6))
                    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(summary)
                    ax.imshow(wordcloud, interpolation="bilinear")
                    ax.axis("off")
                    ax.set_title(f"Top words in the resume: {resume_name}")
                    st.pyplot(fig)
                

                st.write("Visualization of Match Percentages")
                match_percentages = [data["Match Percentage"] for data in sorted_match_data]
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.boxplot(y=match_percentages, ax=ax)
                ax.set_ylabel("Match Percentage")
                st.pyplot(fig)
