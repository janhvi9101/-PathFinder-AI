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
.stButton > button,
.stDownloadButton > button {
    background-color: #52ab98;
    color: white;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🚀 PathFinder AI")
st.subheader("Your Intelligent Career Assistant")
st.write(
    "Analyze your resume, explore career opportunities "
    "and receive personalized learning suggestions."
)

st.divider()

if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

if "resume_id" not in st.session_state:
    st.session_state.resume_id = None

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Upload Resume",
    "📌 Career Suggestion",
    "📊 Visualization",
    "💬 PathBot Chat"
])

# -----------------------------------------
# TAB 1 - UPLOAD RESUME
# -----------------------------------------

with tab1:
    st.header("Upload Your Resume")

    uploaded_file = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"]
    )

    if uploaded_file is not None:
        try:
            file_bytes = uploaded_file.getvalue()

            import hashlib
            file_id = hashlib.sha256(file_bytes).hexdigest()

            with fitz.open(
                stream=file_bytes,
                filetype="pdf"
            ) as doc:
                resume_text = "\n".join(
                    page.get_text() for page in doc
                )

            if not resume_text.strip():
                st.warning(
                    "No readable text found. Please upload "
                    "a text-based PDF resume."
                )
            else:
                if st.session_state.resume_id != file_id:
                    st.session_state.resume_id = file_id
                    st.session_state.resume_text = resume_text
                    st.session_state.analysis = None
                    st.session_state.chat_history = []

                st.success("Resume uploaded successfully!")

                profile = analyze_resume(resume_text)

                st.write(
                    "**Words detected:**",
                    profile["word_count"]
                )

                st.write("**Detected Skills:**")

                if profile["skills"]:
                    st.write(", ".join(profile["skills"]))
                else:
                    st.info("No predefined skills detected.")

                st.info(
                    "Now visit the Career Suggestion tab."
                )

        except Exception as error:
            st.error(f"PDF processing error: {error}")

# -----------------------------------------
# TAB 2 - CAREER SUGGESTION
# -----------------------------------------

with tab2:
    st.header("Personalized Career Recommendation")

    if not st.session_state.resume_text:
        st.warning("Please upload your resume first.")

    else:
        with st.form("career_form"):

            name = st.text_input("Enter Your Name")

            linkedin = st.text_input(
                "LinkedIn Profile URL (Optional)"
            )

            interests = st.multiselect(
                "Select Your Interests",
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
                "Enter Additional Skills (comma separated)"
            )

            submitted = st.form_submit_button(
                "🔍 Analyze My Career Path"
            )

        if submitted:

            if not interests:
                st.warning(
                    "Please select at least one interest."
                )

            else:
                try:
                    resume_text = st.session_state.resume_text

                    result = process_resume(
                        resume_text,
                        interests,
                        skills
                    )

                    grade, grade_tips = grade_resume(
                        resume_text
                    )

                    courses = recommend_courses(
                        result["missing_skills"]
                    )

                    match_percent = round(
                        result["score"] * 100
                    )

                    st.session_state.analysis = {
                        "name": name.strip() or "Student",
                        "linkedin": linkedin,
                        "interests": interests,
                        "skills": skills,
                        "result": result,
                        "grade": grade,
                        "grade_tips": grade_tips,
                        "courses": courses,
                        "match_percent": match_percent
                    }

                    st.success("Career analysis completed!")

                except Exception as error:
                    st.error(f"Analysis error: {error}")

        data = st.session_state.analysis

        if data:

            result = data["result"]

            st.markdown("### 📌 Recommended Path")
            st.success(result["path"])

            st.metric(
                "Career Match Score",
                f"{data['match_percent']}%"
            )

            st.markdown("### 🧠 Career Tips")

            for tip in result["tips"]:
                st.write("•", tip)

            st.markdown("### 🔧 Skill Gap Suggestions")

            if data["courses"]:
                for course in data["courses"]:
                    st.markdown(
                        f"- Learn **{course['skill']}** — "
                        f"[Free Learning Resource]({course['url']})"
                    )
            else:
                st.success(
                    "No skill gaps detected by the current rules."
                )

            st.markdown("### 🎖️ Learner Badge")

            grade = data["grade"]

            if grade >= 9:
                st.success("🏆 Career Guru")
            elif grade >= 7:
                st.success("🎖️ Resume Hero")
            elif grade >= 5:
                st.info("📘 Learner Badge")
            else:
                st.warning("🌱 New Explorer")

# -----------------------------------------
# TAB 3 - VISUALIZATION
# -----------------------------------------

with tab3:
    st.header("Resume Grading Report")

    data = st.session_state.analysis

    if data is None:
        st.info("Complete your career analysis first.")

    else:
        result = data["result"]
        grade = data["grade"]

        st.metric(
            "Resume Score",
            f"{grade} / 10"
        )

        fig = go.Figure(data=[
            go.Pie(
                labels=["Score", "Remaining"],
                values=[grade, max(0, 10 - grade)],
                hole=0.6
            )
        ])

        fig.update_layout(height=320)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown("### 📊 Career Fit by Domain")

        fit_scores = result["fit_scores"]

        categories = list(fit_scores.keys())
        values = list(fit_scores.values())

        radar = go.Figure()

        radar.add_trace(
            go.Scatterpolar(
                r=values + [values[0]],
                theta=categories + [categories[0]],
                fill="toself",
                name="Career Fit"
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

        st.plotly_chart(
            radar,
            use_container_width=True
        )

        st.caption(
            "Scores are based on predefined skill and interest "
            "matching rules, not random values or employment probabilities."
        )

        st.markdown("### Resume Improvement Suggestions")

        for tip in data["grade_tips"]:
            st.write("•", tip)

        st.markdown("### 📥 Download Career Report")

        try:
            pdf_bytes = generate_pdf(
                data["name"],
                result["path"],
                data["interests"],
                data["skills"],
                data["match_percent"],
                result["tips"],
                data["grade"],
                data["grade_tips"],
                result["missing_skills"]
            )

            st.download_button(
                label="Download Career Report (PDF)",
                data=pdf_bytes,
                file_name="PathFinder_Career_Report.pdf",
                mime="application/pdf"
            )

        except Exception as error:
            st.error(f"Report generation error: {error}")

# -----------------------------------------
# TAB 4 - PATHBOT
# -----------------------------------------

with tab4:
    st.header("💬 Ask PathBot for Career Advice")

    st.write(
        "Ask about GATE, MBA, internships, placements, "
        "resumes, courses or career recommendations."
    )

    data = st.session_state.analysis

    profile = {}

    if data:
        profile = {
            "career": data["result"]["career"],
            "skills": data["skills"],
            "interests": data["interests"],
            "missing_skills": data["result"]["missing_skills"]
        }

    with st.form("chat_form", clear_on_submit=True):

        user_question = st.text_input(
            "Enter your career question"
        )

        ask = st.form_submit_button("Ask PathBot")

    if ask and user_question.strip():

        answer = pathbot_answer(
            user_question,
            profile
        )

        st.session_state.chat_history.append({
            "question": user_question,
            "answer": answer
        })

    for chat in st.session_state.chat_history:

        st.markdown(
            f"**You:** {chat['question']}"
        )

        st.success(
            f"🤖 PathBot: {chat['answer']}"
        )

    if st.session_state.chat_history:

        chat_text = "\n\n".join(
            f"Q: {chat['question']}\nA: {chat['answer']}"
            for chat in st.session_state.chat_history
        )

        st.download_button(
            "Download PathBot Conversation",
            data=chat_text,
            file_name="PathBot_Chat.txt",
            mime="text/plain"
        )
