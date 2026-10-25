from fpdf import FPDF
import re


# --------------------------------------------------
# 1. CAREER KNOWLEDGE BASE
# --------------------------------------------------

CAREER_DATA = {
    "Software Development": {
        "interests": ["software", "startup", "research"],
        "keywords": [
            "python", "java", "c++", "programming", "developer",
            "software", "web development", "javascript", "coding",
            "html", "css", "git", "database", "sql"
        ],
        "required_skills": [
            "Python", "Data Structures", "Git", "SQL"
        ],
        "tips": [
            "Build practical software projects.",
            "Contribute to open-source repositories.",
            "Practice coding and problem-solving.",
            "Create a portfolio of your projects."
        ]
    },

    "MBA and Business Management": {
        "interests": ["mba", "startup"],
        "keywords": [
            "management", "business", "marketing", "finance",
            "leadership", "mba", "communication", "sales",
            "analytics", "economics"
        ],
        "required_skills": [
            "Communication", "Business Analytics",
            "Financial Fundamentals"
        ],
        "tips": [
            "Explore business case studies.",
            "Develop communication and leadership skills.",
            "Learn basic business analytics.",
            "Research MBA entrance examinations."
        ]
    },

    "Research and Higher Studies": {
        "interests": ["research", "abroad"],
        "keywords": [
            "research", "publication", "thesis", "machine learning",
            "artificial intelligence", "data analysis", "laboratory",
            "scientific", "academic"
        ],
        "required_skills": [
            "Research Methodology", "Technical Writing",
            "Data Analysis"
        ],
        "tips": [
            "Explore research projects in your field.",
            "Read relevant academic papers.",
            "Develop technical writing skills.",
            "Investigate postgraduate opportunities."
        ]
    },

    "Government and Competitive Examinations": {
        "interests": ["government"],
        "keywords": [
            "government", "public service", "civil services",
            "competitive examination", "gate", "public sector"
        ],
        "required_skills": [
            "Aptitude", "Reasoning", "General Awareness"
        ],
        "tips": [
            "Identify examinations relevant to your qualification.",
            "Create a realistic study timetable.",
            "Practice previous examination papers.",
            "Track your mock-test performance."
        ]
    },

    "Data Analytics": {
        "interests": ["software", "research", "mba"],
        "keywords": [
            "data analysis", "data analytics", "statistics",
            "sql", "excel", "power bi", "tableau", "pandas",
            "visualization", "machine learning"
        ],
        "required_skills": [
            "SQL", "Statistics", "Python", "Data Visualization"
        ],
        "tips": [
            "Practice analyzing real datasets.",
            "Learn SQL and spreadsheet analysis.",
            "Build data visualization projects.",
            "Develop a portfolio of analytical work."
        ]
    }
}


# --------------------------------------------------
# 2. TEXT PROCESSING
# --------------------------------------------------

def normalize(text):
    """Normalize text for consistent keyword matching."""
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def clean_text(text):
    """Keep text compatible with the standard FPDF font."""
    return str(text).encode("latin-1", "replace").decode("latin-1")


# --------------------------------------------------
# 3. RESUME ANALYSIS TOOL
# --------------------------------------------------

def analyze_resume(resume_text):
    """
    Extract useful information using transparent,
    rule-based text analysis.
    """

    text = normalize(resume_text)

    detected_skills = [
        "Python", "Java", "C++", "JavaScript", "HTML", "CSS",
        "SQL", "Git", "React", "Machine Learning",
        "Data Analysis", "Excel", "Power BI", "Communication",
        "Leadership", "AWS", "Docker"
    ]

    found_skills = []

    for skill in detected_skills:
        if normalize(skill) in text:
            found_skills.append(skill)

    sections = {
        "education": any(
            word in text
            for word in ["education", "degree", "bachelor", "b.tech", "b.e."]
        ),
        "projects": any(
            word in text for word in ["project", "developed", "built"]
        ),
        "experience": any(
            word in text
            for word in ["experience", "internship", "intern", "employment"]
        ),
        "skills_section": "skills" in text,
        "achievements": any(
            word in text
            for word in ["achievement", "award", "certification", "certified"]
        )
    }

    return {
        "skills": found_skills,
        "sections": sections,
        "word_count": len(text.split())
    }


# --------------------------------------------------
# 4. RESUME GRADING TOOL
# --------------------------------------------------

def grade_resume(resume_text):
    """
    Calculate a deterministic heuristic completeness score.
    This is not a validated professional resume assessment.
    """

    profile = analyze_resume(resume_text)
    sections = profile["sections"]

    score = 0

    # Resume sections: 5 criteria, 1 point each.
    score += sum(sections.values())

    # Skills identified in the resume: maximum 2 points.
    score += min(len(profile["skills"]) / 3, 2)

    # Resume content length: maximum 2 points.
    word_count = profile["word_count"]

    if word_count >= 250:
        score += 2
    elif word_count >= 150:
        score += 1.5
    elif word_count >= 75:
        score += 1
    elif word_count >= 30:
        score += 0.5

    # Achievement evidence: maximum 1 point.
    if sections["achievements"]:
        score += 1

    grade = round(min(score, 10), 1)

    suggestions = []

    if not sections["education"]:
        suggestions.append("Add your education and qualifications.")

    if not sections["skills_section"] or not profile["skills"]:
        suggestions.append(
            "Add a clearly organized skills section with relevant skills."
        )

    if not sections["projects"]:
        suggestions.append(
            "Include academic or personal projects with clear outcomes."
        )

    if not sections["experience"]:
        suggestions.append(
            "Include relevant internships, experience, or practical work."
        )

    if not sections["achievements"]:
        suggestions.append(
            "Include relevant certifications or measurable achievements."
        )

    if not suggestions:
        suggestions.append(
            "Review your resume for measurable achievements and clarity."
        )

    return grade, suggestions


# --------------------------------------------------
# 5. CAREER RECOMMENDATION AGENT
# --------------------------------------------------

def process_resume(resume_text, interests, skills):
    """
    Select a career using resume keywords, user interests,
    and explicitly entered skills.
    """

    text = normalize(resume_text)
    user_skills = normalize(skills)

    combined_text = f"{text} {user_skills}"

    scores = {}

    for career, details in CAREER_DATA.items():
        score = 0

        # Explicit user interest receives greater weight.
        for interest in interests:
            if normalize(interest) in details["interests"]:
                score += 3

        # Match the profile against career-related keywords.
        for keyword in details["keywords"]:
            if normalize(keyword) in combined_text:
                score += 1

        # Match required skills already present in the profile.
        for skill in details["required_skills"]:
            if normalize(skill) in combined_text:
                score += 1

        scores[career] = score

    # Stable ordering makes ties deterministic.
    best_career = max(
        scores,
        key=lambda career: scores[career]
    )

    # Avoid making a confident recommendation from no evidence.
    if scores[best_career] == 0:
        best_career = "Software Development"

        recommendation = (
            "There is not enough matching information for a confident "
            "recommendation. Software Development is shown as a starting "
            "option; provide more skills and interests for a better match."
        )
    else:
        recommendation = (
            f"Based on your resume, skills, and interests, "
            f"{best_career} is a career option worth exploring."
        )

    career_data = CAREER_DATA[best_career]

    # Identify missing skills using the user's supplied profile.
    missing_skills = []

    for skill in career_data["required_skills"]:
        if normalize(skill) not in combined_text:
            missing_skills.append(skill)

    # Normalize career-fit scores for visualization.
    maximum_score = max(scores.values())

    if maximum_score == 0:
        fit_scores = {
            career: 0 for career in CAREER_DATA
        }
    else:
        fit_scores = {
            career: round(score / maximum_score * 100)
            for career, score in scores.items()
        }

    return {
        "path": recommendation,
        "career": best_career,
        "score": scores[best_career],
        "scores": scores,
        "fit_scores": fit_scores,
        "tips": career_data["tips"],
        "missing_skills": missing_skills
    }


# --------------------------------------------------
# 6. LEARNING RESOURCE TOOL
# --------------------------------------------------

RESOURCE_URLS = {
    "Python": "https://www.python.org/about/gettingstarted/",
    "Data Structures": "https://www.geeksforgeeks.org/data-structures/",
    "Git": "https://git-scm.com/doc",
    "SQL": "https://www.w3schools.com/sql/",
    "Communication": "https://www.coursera.org/",
    "Business Analytics": "https://www.coursera.org/",
    "Financial Fundamentals": "https://www.coursera.org/",
    "Research Methodology": "https://www.coursera.org/",
    "Technical Writing": "https://www.coursera.org/",
    "Data Analysis": "https://www.kaggle.com/learn",
    "Statistics": "https://www.khanacademy.org/math/statistics-probability",
    "Data Visualization": "https://www.kaggle.com/learn",
    "Aptitude": "https://www.indiabix.com/",
    "Reasoning": "https://www.indiabix.com/",
    "General Awareness": "https://www.coursera.org/"
}


def recommend_courses(missing_skills):
    """Map identified skill gaps to learning-resource URLs."""

    recommendations = []

    for skill in missing_skills:
        recommendations.append({
            "skill": skill,
            "url": RESOURCE_URLS.get(
                skill,
                "https://www.coursera.org/"
            )
        })

    return recommendations


# --------------------------------------------------
# 7. PATHBOT CONVERSATIONAL TOOL
# --------------------------------------------------

def pathbot_answer(user_input, profile=None):
    """
    Answer common career questions using keyword rules
    and optional analyzed student-profile information.
    """

    question = normalize(user_input)

    if not question:
        return "Please enter a career-related question."

    if profile is None:
        profile = {}

    career = profile.get("career", "")
    skills = profile.get("skills", "")
    interests = profile.get("interests", [])

    if "your recommended career" in question or "my career" in question:
        if career:
            return (
                f"Your current recommended career is {career}. "
                f"Consider your interests, existing skills, and long-term "
                f"goals before making a final decision."
            )

        return (
            "Upload your resume and complete the career analysis "
            "to receive a personalized career recommendation."
        )

    if "skill" in question or "learn" in question or "course" in question:
        missing = profile.get("missing_skills", [])

        if missing:
            return (
                "Based on your current career analysis, consider developing "
                + ", ".join(missing)
                + ". Prioritize the skills most relevant to your goal."
            )

        return (
            "Choose a target career first, then compare its required skills "
            "with your existing knowledge."
        )

    if "resume" in question or "cv" in question:
        return (
            "Improve your resume by highlighting relevant skills, projects, "
            "education, experience, and measurable achievements."
        )

    if "gate" in question:
        return (
            "GATE may be suitable if you are interested in postgraduate "
            "technical education or relevant technical recruitment. "
            "Check the eligibility and requirements for your target."
        )

    if "mba" in question:
        return (
            "An MBA may suit students interested in management, business, "
            "consulting, or leadership. Consider your interests, entrance "
            "examinations, and career goals."
        )

    if "job" in question or "placement" in question:
        return (
            "For job preparation, strengthen relevant technical skills, "
            "build projects, practice interviews, and apply for suitable "
            "internships and entry-level positions."
        )

    if "interest" in question or "career path" in question:
        if career:
            return (
                f"Your current recommendation is {career}. "
                f"Your selected interests are {', '.join(interests) if interests else 'not specified'}. "
                "Compare this option with your preferences before deciding."
            )

        return (
            "Identify your strongest skills, preferred work, and long-term "
            "goals. Your resume and interests can help narrow the options."
        )

    if career:
        return (
            f"Considering your current recommendation of {career} "
            f"and the skills you provided ({skills or 'not specified'}), "
            "start by identifying your immediate goal and the skills "
            "needed to achieve it."
        )

    return (
        "I can help with career selection, skill development, resumes, "
        "GATE, MBA, placements, and learning plans. Please ask a more "
        "specific question."
    )


# --------------------------------------------------
# 8. PDF CAREER REPORT
# --------------------------------------------------

def generate_pdf(
    name,
    path,
    interests,
    skills,
    match_percent,
    tips,
    grade,
    grade_tips,
    missing_skills=None
):
    """Generate a downloadable career report."""

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, clean_text("PathFinder AI Career Report"), ln=1)

    pdf.set_font("Arial", "", 11)
    pdf.ln(4)

    pdf.multi_cell(
        0,
        8,
        clean_text(
            f"Name: {name or 'Not provided'}\n"
            f"Career Match Indicator: {match_percent}%\n"
            f"Career Recommendation: {path}\n"
            f"Interests: {', '.join(interests) if interests else 'Not provided'}\n"
            f"Skills: {skills or 'Not provided'}"
        )
    )

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 9, "Career Tips", ln=1)

    pdf.set_font("Arial", "", 11)

    for tip in tips:
        pdf.multi_cell(0, 7, clean_text("- " + tip))

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 9, "Suggested Skill Development", ln=1)

    pdf.set_font("Arial", "", 11)

    for skill in (missing_skills or []):
        pdf.multi_cell(0, 7, clean_text("- " + skill))

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 9, "Resume Completeness Indicator", ln=1)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, clean_text(f"Heuristic score: {grade}/10"), ln=1)

    for suggestion in grade_tips:
        pdf.multi_cell(0, 7, clean_text("- " + suggestion))

    pdf.ln(5)
    pdf.set_font("Arial", "I", 9)

    pdf.multi_cell(
        0,
        6,
        clean_text(
            "Note: Career recommendations and scores are generated "
            "using predefined rules. They are guidance indicators, "
            "not guarantees of career suitability or employment."
        )
    )

    safe_name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        str(name or "Student")
    ).strip("_")

    filename = f"{safe_name or 'Student'}_career_report.pdf"

    pdf.output(filename)

    return filename
```
ernships too."
    else:
        return "Explore your interests, list your priorities, and talk to mentors."
