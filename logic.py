import re
from io import BytesIO
from fpdf import FPDF

CAREERS = {
    "Software Development": {
        "interest": "Software",
        "skills": ["Python", "Java", "SQL", "Git", "Problem Solving"],
        "tips": [
            "Build practical coding projects.",
            "Practise programming and problem solving.",
            "Maintain a GitHub portfolio."
        ]
    },
    "Business Management": {
        "interest": "MBA",
        "skills": ["Communication", "Excel", "Leadership", "Presentation"],
        "tips": [
            "Improve communication and leadership skills.",
            "Explore business-related internships.",
            "Research MBA entrance examinations."
        ]
    },
    "Research and Higher Studies": {
        "interest": "Research",
        "skills": ["Python", "Research", "Data Analysis", "Writing"],
        "tips": [
            "Explore research papers.",
            "Work on academic projects.",
            "Research postgraduate opportunities."
        ]
    },
    "Government Sector": {
        "interest": "Government",
        "skills": ["Aptitude", "Reasoning", "General Knowledge"],
        "tips": [
            "Select a suitable government examination.",
            "Study its official syllabus.",
            "Practise previous-year papers."
        ]
    },
    "International Opportunities": {
        "interest": "Abroad",
        "skills": ["Communication", "Research", "Writing", "English"],
        "tips": [
            "Research international universities and opportunities.",
            "Prepare relevant entrance or language examinations.",
            "Build a strong academic profile."
        ]
    },
    "Entrepreneurship": {
        "interest": "Startup",
        "skills": ["Leadership", "Communication", "Marketing", "Finance"],
        "tips": [
            "Identify a real-world problem.",
            "Develop a minimum viable product.",
            "Learn basic marketing and finance."
        ]
    }
}

RESOURCES = {
    "Python": "https://www.py4e.com/",
    "Java": "https://dev.java/learn/",
    "SQL": "https://sqlbolt.com/",
    "Git": "https://git-scm.com/doc",
    "Excel": "https://support.microsoft.com/excel",
    "Communication": "https://www.toastmasters.org/",
    "Problem Solving": "https://www.hackerrank.com/",
    "Data Analysis": "https://www.kaggle.com/learn",
    "Leadership": "https://www.coursera.org/",
    "Presentation": "https://support.microsoft.com/powerpoint"
}


def normalize(text):
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def has_term(text, term):
    return bool(re.search(
        r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)",
        normalize(text)
    ))


def analyze_resume(resume_text):
    text = normalize(resume_text)
    all_skills = set()

    for career in CAREERS.values():
        all_skills.update(career["skills"])

    detected = sorted(
        skill for skill in all_skills
        if has_term(text, skill)
    )

    sections = [
        "education", "experience", "projects",
        "skills", "achievements"
    ]

    found = [
        section.title() for section in sections
        if has_term(text, section)
    ]

    return {
        "word_count": len(resume_text.split()),
        "skills": detected,
        "sections_found": found,
        "has_contact_info": bool(re.search(
            r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
            resume_text
        ))
    }


def grade_resume(resume_text):
    analysis = analyze_resume(resume_text)
    score = 0.0
    tips = []

    score += len(analysis["sections_found"])

    for section in [
        "Education", "Experience", "Projects",
        "Skills", "Achievements"
    ]:
        if section not in analysis["sections_found"]:
            tips.append(f"Consider adding a {section} section.")

    score += min(len(analysis["skills"]) * 0.4, 2)

    if len(analysis["skills"]) < 3:
        tips.append("Mention more relevant skills.")

    if analysis["has_contact_info"]:
        score += 1
    else:
        tips.append("Include a professional email address.")

    if analysis["word_count"] >= 150:
        score += 1
    else:
        tips.append("Add more relevant resume details.")

    if any(term in normalize(resume_text) for term in [
        "improved", "achieved", "increased", "award", "%"
    ]):
        score += 1
    else:
        tips.append("Include measurable achievements.")

    if not tips:
        tips.append("Keep your resume updated and relevant.")

    return round(min(score, 10), 1), tips


def process_resume(resume_text, interests=None, skills=None):
    interests = interests or []

    if isinstance(interests, str):
        interests = [interests]

    if isinstance(skills, str):
        skills = [
            item.strip() for item in skills.split(",")
            if item.strip()
        ]
    else:
        skills = skills or []

    analysis = analyze_resume(resume_text)

    known_skills = {
        normalize(skill)
        for skill in analysis["skills"] + skills
    }

    fit_scores = {}
    raw_scores = {}

    for career_name, career in CAREERS.items():
        required = career["skills"]

        matched = sum(
            normalize(skill) in known_skills
            for skill in required
        )

        interest_match = any(
            normalize(interest) == normalize(career["interest"])
            for interest in interests
        )

        # 60% skill matching and 40% interest matching.
        score = (
            (matched / len(required)) * 60
            + (40 if interest_match else 0)
        )

        raw_scores[career_name] = score
        fit_scores[career_name] = round(score)

    best = max(raw_scores, key=raw_scores.get)
    selected = CAREERS[best]

    missing = [
        skill for skill in selected["skills"]
        if normalize(skill) not in known_skills
    ]

    return {
        "career": best,
        "path": (
            f"Based on your resume, skills and interests, "
            f"{best} is your recommended career path."
        ),
        "score": round(raw_scores[best] / 100, 2),
        "fit_scores": fit_scores,
        "tips": selected["tips"],
        "missing_skills": missing
    }


def recommend_courses(missing_skills):
    return [
        {
            "skill": skill,
            "course": f"Learn {skill}",
            "url": RESOURCES.get(
                skill, "https://www.coursera.org/"
            )
        }
        for skill in missing_skills
    ]


def pathbot_answer(user_input, profile=None):
    question = normalize(user_input)
    profile = profile or {}

    career = profile.get("career", "")
    missing = profile.get("missing_skills", [])

    if not question:
        return "Please enter a career-related question."

    if "internship" in question:
        return (
            "Look for internships related to your interests. "
            "Build projects, improve your resume and check eligibility."
        )

    if "gate" in question:
        return (
            "GATE is useful for eligible postgraduate and technical "
            "opportunities. Check the official examination requirements."
        )

    if "mba" in question:
        return (
            "An MBA may suit students interested in business, "
            "management and leadership."
        )

    if "job" in question or "placement" in question:
        return (
            "Prepare your resume, practise interviews, "
            "develop relevant skills and apply for suitable roles."
        )

    if "resume" in question or "cv" in question:
        return (
            "Improve your resume by highlighting relevant skills, "
            "projects, education and measurable achievements."
        )

    if any(word in question for word in [
        "skill", "course", "learn"
    ]):
        if missing:
            return (
                "Based on your profile, consider learning: "
                + ", ".join(missing)
            )
        return "Choose your career goal and develop its required skills."

    if any(phrase in question for phrase in [
        "my career", "recommended career", "career path"
    ]):
        if career:
            return f"Your current recommended career is {career}."
        return "Complete your resume analysis to receive career guidance."

    if career:
        return (
            f"Your current recommendation is {career}. "
            "Consider your skills, interests and long-term goals."
        )

    return (
        "I can help with resumes, career selection, GATE, MBA, "
        "placements, internships and skill development."
    )


def generate_pdf(
    name, path, interests, skills, match_percent,
    tips, grade, grade_tips, missing_skills=None
):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def safe(value):
        return str(value).encode(
            "latin-1", "replace"
        ).decode("latin-1")

    def line(value):
        pdf.multi_cell(0, 8, safe(value))

    pdf.set_font("Arial", "B", 16)
    line("PathFinder AI - Career Report")
    pdf.ln(5)

    pdf.set_font("Arial", "", 11)

    line(f"Name: {name}")
    line(f"Recommended Path: {path}")
    line(f"Career Match: {match_percent}%")
    line(f"Resume Score: {grade}/10")
    line(f"Interests: {', '.join(interests)}")
    line(f"Skills: {skills}")

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    line("Career Tips")
    pdf.set_font("Arial", "", 11)

    for tip in tips:
        line("- " + tip)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    line("Skill Gap Suggestions")
    pdf.set_font("Arial", "", 11)

    for skill in missing_skills or []:
        line("- Learn " + skill)

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    line("Resume Improvement Tips")
    pdf.set_font("Arial", "", 11)

    for tip in grade_tips:
        line("- " + tip)

    output = pdf.output(dest="S")
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)
