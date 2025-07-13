# logic.py
from fpdf import FPDF
import random

def clean_text(text):
    return text.encode('latin-1', 'ignore').decode('latin-1')

def process_resume(resume_text, interests, skills):
    score = round(random.uniform(0.4, 0.95), 2)
    suggested_path = "Based on your skills and interests, Software Development is a great match."
    tips = [
        "Explore open source contributions",
        "Join coding communities",
        "Build strong LinkedIn profile"
    ]
    return {
        "score": score,
        "path": suggested_path,
        "tips": tips
    }

def grade_resume(resume_text):
    grade = round(random.uniform(5, 10), 1)
    suggestions = [
        "Add measurable achievements",
        "Improve keyword targeting",
        "Use a cleaner resume format"
    ]
    return grade, suggestions

def generate_pdf(name, path, interests, skills, match_percent, tips, grade, grade_tips):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, clean_text("PathFinder AI Career Report"), ln=1)

    pdf.set_font("Arial", '', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.multi_cell(0, 10, clean_text(
        f"Name: {name}\nMatch Score: {match_percent}%\n\nCareer Path: {path}\n\nInterests: {', '.join(interests)}\nSkills: {skills}"
    ))

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text("Career Tips:"), ln=1)
    pdf.set_font("Arial", '', 12)
    for tip in tips:
        pdf.cell(0, 10, clean_text(f"- {tip}"), ln=1)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, clean_text("Resume Grade & Suggestions:"), ln=1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, clean_text(f"Grade: {grade}/10"), ln=1)
    for gtip in grade_tips:
        pdf.cell(0, 10, clean_text(f"- {gtip}"), ln=1)

    filename = f"{name}_career_report.pdf"
    pdf.output(filename)
    return filename

def pathbot_answer(user_input):
    if "gate" in user_input.lower():
        return "If you enjoy deep learning and core tech, GATE is a good option."
    elif "mba" in user_input.lower():
        return "MBA is great if you're interested in management and leadership roles."
    elif "job" in user_input.lower():
        return "Getting a job helps gain experience early; consider internships too."
    else:
        return "Explore your interests, list your priorities, and talk to mentors."
