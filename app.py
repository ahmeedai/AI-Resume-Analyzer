import streamlit as st
import PyPDF2
import io
from openai import OpenAI
# Streamlit page settings
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📃", layout="centered")
st.title("📃 AI Resume Analyzer")
st.markdown("Upload your resume and get feedback powered by AI!")

# --- Helper Functions ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in pdf_reader.pages)

def extract_text(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

def generate_feedback(text, job_role, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"""
Please analyze this resume and provide constructive feedback. 
Focus on:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. Improvements for {job_role or 'general applications'}
Resume:
{text}
Give a clear and structured analysis.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert resume reviewer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    return response.choices[0].message.content

# --- UI ---
st.markdown("🔑 Enter your OpenAI API Key to continue:")
api_key = st.text_input("API Key", type="password")
uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")
analyze = st.button("Analyze Resume")

if analyze:
    if not api_key:
        st.error("Please enter your OpenAI API key.")
    elif not uploaded_file:
        st.error("Please upload a resume file.")
    else:
        with st.spinner("Analyzing resume..."):
            try:
                content = extract_text(uploaded_file)
                if not content.strip():
                    st.error("The uploaded file is empty.")
                    st.stop()
                feedback = generate_feedback(content, job_role, api_key)
                st.success("Done!")
                st.markdown("### 📝 Feedback:")
                st.markdown(feedback)
                st.download_button(
                    label="📥 Download Feedback Report",
                    data=feedback,
                    file_name="resume_feedback.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
