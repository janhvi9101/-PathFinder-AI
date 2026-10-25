import streamlit as st
import fitz
import plotly.graph_objects as go

from logic import (
    analyze_resume,
    process_resume,
    grade_resume,
    generate_pdf,
    pathbot_answer,
    recommend_courses
)

st.set_page_config(
    page_title="PathFinder AI",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #ffffff !important;
    color: #111111 !important;
    font-family: 'Segoe UI', sans-serif;
}
.stDownloadButton > button, .stButton > button {
    background-color: #52ab98;
    color: white;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color:#f5f5f5;padding:20px;
border-radius:12px;text-align:center;">
<h1 style="color:#2b6777;">
🚀 PathFinder AI - Your Intelligent Career Assistant
</h1>
<p>Your personalized career guidance agent</p>
</div>
""", unsafe_allow_html=True)

st.divider()

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Upload Resume",
    "📌 Career Suggestion",
    "📊 Visualization",
    "💬 PathBot Chat"
])

# Initialize session state.
if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------------------------------------------------
# TAB 1: RESUME UPLOAD
# --------------------------------------------------

with tab1:
    st.subheader("Upload Your Resume")

    uploaded_file = st.file_uploader(
        "Upload your resume in PDF format",
        type=["pdf"],
        key="resume_upload"
    )

    if uploaded_file is not None:
        try:
            with fitz.open(
                stream=uploaded_file.getvalue(),
                filetype="pdf"
            ) as doc:
                resume_text = "\n".join(
                    page.get_text() for page in doc
                )

            if not resume_text.strip():
                st.warning(
                    "No selectable text was found. "
                    "Please upload a text-based PDF resume."
                )
            else:
                st.session_state.resume_text = resume_text

                profile = analyze_resume(resume_text)

                st.success("Resume uploaded successfully!")

                st.write(
                    f"**Words detected:** {profile['word_count']}"
                )

                st.write(
                    "**Recognized skills:**",
                    ", ".join(profile["skills"])
                    if profile["skills"]
                    else "No recognized skills found."
                )

        except Exception as error:
            st.error(
                f"Unable to read this PDF. Please try another file. "
                f"Details: {error}"
            )

# --------------------------------------------------
# TAB 2: CAREER SUGGESTION
# --------------------------------------------------

with tab2:
    st.subheader("Personalized Career Analysis")

    if not st.session_state.get("resume_text"):
        st.info("Upload your resume in the first tab to continue.")

    else:
        with st.form("career_form"):
            name = st.text_input("Enter your name")

            linkedin = st.text_input(
                "Enter your LinkedIn profile URL (optional)"
            )

            interests = st.multiselect(
                "Select your interests",
                [
                    "Software",
                    "MBA",
                    "Research",
                    "Government",
                    "Abroad",
                    "Startup"
                ]
            )

            skills = st.text_input(
                "Enter your skills, separated by commas"
            )

            submitted = st.form_submit_button(
                "🔍 Analyze My Career Path"
            )

        if submitted:
            if not interests and not skills.strip():
                st.warning(
                    "Select at least one interest or enter your skills "
                    "to receive a more personalized recommendation."
                )

            else:
                with st.spinner("Analyzing your career profile..."):
                    resume_text = st.session_state.resume_text

                    resume_profile = analyze_resume(resume_text)

                    result = process_resume(
                        resume_text,
                        interests,
                        skills
                    )

                    grade, grade_tips = grade_resume(resume_text)

                    courses = recommend_courses(
                        result["missing_skills"]
                    )

                    st.session_state.analysis = {
                        "name": name,
                        "linkedin": linkedin,
                        "interests": interests,
                        "skills": skills,
                        "path": result["path"],
                        "career": result["career"],
                        "score": result["score"],
                        "fit_scores": result["fit_scores"],
                        "tips": result["tips"],
                        "missing_skills": result["missing_skills"],
                        "courses": courses,
                        "match_percent": result["fit_scores"][
                            result["career"]
                        ],
                        "grade": grade,
                        "grade_tips": grade_tips,
                        "resume_profile": resume_profile
                    }

                    st.session_state.chat_history = []

        data = st.session_state.analysis

        if data:
            st.markdown("### 📌 Recommended Career Path")
            st.success(data["path"])

            st.caption(
                "This recommendation uses predefined rules matching "
                "your interests, skills, and resume keywords."
            )

            st.markdown("### 🧠 Career Tips")

            for tip in data["tips"]:
                st.markdown(f"- {tip}")

            st.markdown("### 🔧 Skill Gap Suggestions")

            if data["missing_skills"]:
                for course in data["courses"]:
                    st.markdown(
                        f"- Learn **{course['skill']}** — "
                        f"[Learning resource]({course['url']})"
                    )
            else:
                st.success(
                    "No skill gaps were identified by the current rules."
                )

            grade = data["grade"]

            if grade >= 9:
                st.success("🏆 Career Guru: Excellent completeness score!")
            elif grade >= 7:
                st.success("🎖️ Resume Hero: Good completeness score!")
            elif grade >= 5:
                st.info("📘 Learner Badge: Keep improving your resume!")
            else:
                st.warning("🌱 New Explorer: Your resume needs more detail.")

# --------------------------------------------------
# TAB 3: VISUALIZATION AND REPORT
# --------------------------------------------------

with tab3:
    st.subheader("Resume Grading Report")

    data = st.session_state.analysis

    if not data:
        st.info(
            "Upload a resume and complete your career analysis "
            "to view your report."
        )

    else:
        st.metric(
            "Resume Completeness Score",
            f"{data['grade']} / 10"
        )

        st.caption(
            "This score is a rule-based completeness indicator, "
            "not a professional resume evaluation."
        )

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Score", "Remaining"],
                    values=[
                        data["grade"],
                        max(0, 10 - data["grade"])
                    ],
                    hole=0.6
                )
            ]
        )

        fig.update_layout(
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20),
            height=320
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📊 Career Fit by Domain")

        categories = list(data["fit_scores"].keys())

        values = [
            data["fit_scores"][category]
            for category in categories
        ]

        radar = go.Figure()

        radar.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill="toself",
                name="Profile Match"
            )
        )

        radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=False
        )

        st.plotly_chart(radar, use_container_width=True)

        st.caption(
            "Career-fit values are relative keyword and interest matches. "
            "They are not probabilities of career success."
        )

        st.markdown("### 📥 Download Career Report")

        try:
            filename = generate_pdf(
                data["name"],
                data["path"],
                data["interests"],
                data["skills"],
                data["match_percent"],
                data["tips"],
                data["grade"],
                data["grade_tips"],
                data["missing_skills"]
            )

            with open(filename, "rb") as pdf_file:
                st.download_button(
                    "Download Career Report (PDF)",
                    data=pdf_file.read(),
                    file_name=filename,
                    mime="application/pdf"
                )

        except Exception as error:
            st.error(f"Could not generate the PDF report: {error}")

# --------------------------------------------------
# TAB 4: PATHBOT CHAT
# --------------------------------------------------

with tab4:
    st.subheader("💬 Ask PathBot for Career Advice")

    st.write(
        "Ask questions about career choices, skills, GATE, MBA, "
        "placements, or your recommended career."
    )

    data = st.session_state.analysis

    if data:
        st.caption(
            f"Current career recommendation: {data['career']}"
        )
    else:
        st.info(
            "You can ask general questions now. Complete your career "
            "analysis for profile-aware responses."
        )

    with st.form("pathbot_form", clear_on_submit=True):
        user_question = st.text_input(
            "Enter your career question",
            placeholder="Should I prepare for GATE or apply for jobs?"
        )

        ask_button = st.form_submit_button("Ask PathBot")

    if ask_button and user_question.strip():
        career_profile = None

        if data:
            career_profile = {
                "career": data["career"],
                "skills": data["skills"],
                "interests": data["interests"],
                "missing_skills": data["missing_skills"]
            }

        answer = pathbot_answer(
            user_question,
            career_profile
        )

        st.session_state.chat_history.append(
            {
                "question": user_question,
                "answer": answer
            }
        )

    for chat in st.session_state.chat_history:
        st.markdown(f"**You:** {chat['question']}")
        st.success(f"🤖 PathBot: {chat['answer']}")

    if st.session_state.chat_history:
        chat_text = "\n\n".join(
            f"Q: {chat['question']}\nA: {chat['answer']}"
            for chat in st.session_state.chat_history
        )

        st.download_button(
            "Download PathBot Conversation",
            data=chat_text,
            file_name="career_chat.txt",
            mime="text/plain"
        )
```

