# app.py
import streamlit as st
import fitz  # PyMuPDF
import plotly.graph_objects as go
import random
from logic import process_resume, grade_resume, generate_pdf, pathbot_answer

st.set_page_config(page_title="PathFinder AI", layout="wide")

# Base Style Reset (light background, standard text)
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        background-color: #ffffff !important;
        color: #111111 !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .stDownloadButton > button, .stButton > button {
        background-color: #52ab98;
        color: white;
        border-radius: 12px;
        padding: 10px 20px;
        border: none;
        font-weight: bold;
        transition: 0.3s ease-in-out;
    }
    .stDownloadButton > button:hover, .stButton > button:hover {
        background-color: #3f9184;
        transform: scale(1.03);
    }
    .stTextInput > div > input, .stSelectbox > div, .stMultiSelect > div {
        border-radius: 12px !important;
        padding: 8px !important;
        border: 1px solid #ccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Header with subtle background
title_html = """
    <div style='background-color: #f5f5f5; padding: 20px; border-radius: 12px; text-align: center;'>
        <h1 style='color: #2b6777;'>🧠 PathFinder AI - Your Smart Career Assistant</h1>
        <p style='color: #444;'>Your personalized AI that evaluates your resume, gives career advice, and helps you grow!</p>
    </div>
"""
st.markdown(title_html, unsafe_allow_html=True)

st.divider()

# --- Tabs for different app sections ---
tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload Resume", "📌 Career Suggestion", "📊 Visualization", "💬 PathBot Chat"])

with tab1:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF Only)", type=["pdf"])

with tab4:
    st.subheader("Ask PathBot for Career Advice")
    user_q = st.text_input("Type your career question here (e.g., 'Job vs GATE?')")
    if user_q:
        response = pathbot_answer(user_q)
        st.success(f"🤖 PathBot says: {response}")

if uploaded_file is not None:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        resume_text = "\n".join([page.get_text() for page in doc])

    with tab2:
        name = st.text_input("Enter your name")
        linkedin = st.text_input("Enter your LinkedIn profile URL")
        interests = st.multiselect("Select Your Interests", ["Software", "MBA", "Research", "Government", "Abroad", "Startup"])
        skills = st.text_input("Enter your key skills (comma separated)")

        if st.button("🔍 Analyze My Career Path"):
            with st.spinner("Analyzing your profile..."):
                result = process_resume(resume_text, interests, skills)
                match_percent = int(result['score'] * 100)
                grade, tips = grade_resume(resume_text)

            st.markdown("### 📌 Recommended Path")
            st.success(result['path'])
            st.markdown("### 🧠 Career Tips")
            for tip in result['tips']:
                st.markdown(f"- {tip}")

            st.markdown("### 🔧 Skill Gap Suggestions")
            missing_skills = ["Data Structures", "System Design", "Public Speaking"]
            for skill in missing_skills:
                st.markdown(f"- Learn **{skill}**➡️ [Free Resource](https://www.coursera.org)")

            # 🎖️ Gamification Layer
            if grade >= 9:
                st.balloons()
                st.success("🏆 Career Guru: Your resume is excellent!")
            elif grade >= 7:
                st.success("🎖️ Resume Hero: Strong resume! Keep going.")
            elif grade >= 5:
                st.info("📘 Learner Badge: You're getting there.")
            else:
                st.warning("🌱 New Explorer: Let's level up your profile!")

            st.session_state['analysis'] = {
                'name': name,
                'path': result['path'],
                'interests': interests,
                'skills': skills,
                'match_percent': match_percent,
                'tips': result['tips'],
                'grade': grade,
                'grade_tips': tips,
                'chat_q': user_q,
                'chat_a': response if user_q else ""
            }

    with tab3:
        if 'analysis' in st.session_state:
            data = st.session_state['analysis']
            st.markdown("### 📄 Resume Grading Report")
            st.write(f"🎯 **Score:** {data['grade']} / 10")

            fig = go.Figure(data=[go.Pie(
                labels=['Score', 'Remaining'],
                values=[data['grade'], 10 - data['grade']],
                hole=.6,
                marker=dict(colors=['#52ab98', '#eeeeee'])
            )])
            fig.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), width=300, height=300)
            st.plotly_chart(fig)

            st.markdown("### 📊 Career Fit by Domain")
            categories = ["Software", "MBA", "Research", "Government", "Abroad", "Startup"]
            values = [random.randint(40, 90) for _ in categories]
            radar = go.Figure()
            radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name='Fit'))
            radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False)
            st.plotly_chart(radar, use_container_width=True)

            filename = generate_pdf(
                data['name'], data['path'], data['interests'], data['skills'],
                data['match_percent'], data['tips'], data['grade'], data['grade_tips']
            )
            with open(filename, "rb") as f:
                st.download_button("📅 Download Career Report", f, file_name=filename)

            if data['chat_q']:
                st.download_button("💬 Download PathBot Chat", data=f"Q: {data['chat_q']}\nA: {data['chat_a']}", file_name="career_chat.txt")
