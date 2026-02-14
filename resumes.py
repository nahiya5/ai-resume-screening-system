import os
import re
import sqlite3
import unicodedata
from PyPDF2 import PdfReader
import pytesseract
from pdf2image import convert_from_path


DB_PATH = r"C:\Users\gayaz\resume_mentor.db"

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


SKILL_KEYWORDS = [
    "python", "sql", "java", "excel", "html", "css", "javascript",
    "django", "flask", "react", "node", "aws", "azure", "git",
    "linux", "machine learning", "data analysis", "rest api"
]


def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

   
    cursor.execute("DROP TABLE IF EXISTS resumes")
    cursor.execute("DROP TABLE IF EXISTS resume_skills")
    cursor.execute("DROP TABLE IF EXISTS jobs")
    cursor.execute("DROP TABLE IF EXISTS job_skills")

    
    cursor.execute("""
    CREATE TABLE resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_name TEXT,
        target_role TEXT,
        email TEXT,
        number TEXT,
        raw_text TEXT,
        clean_text TEXT,
        skills_extracted TEXT,
        tokens TEXT
    )
    """)

    
    cursor.execute("""
    CREATE TABLE resume_skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        skill_name TEXT,
        skill_type TEXT,
        proficiency_level TEXT
    )
    """)

   
    cursor.execute("""
    CREATE TABLE jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_title TEXT,
        company_name TEXT,
        location TEXT,
        required_skills TEXT,
        job_description TEXT,
        experience_level TEXT,
        clean_text TEXT
    )
    """)

    
    cursor.execute("""
    CREATE TABLE job_skills (
        job_skill_id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        skill_name TEXT,
        occurrence INTEGER
    )
    """)

    conn.commit()
    conn.close()




def read_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + " "
        if len(text.strip()) < 50:
            raise ValueError("Using OCR fallback")
        return text.strip()
    except Exception:
        images = convert_from_path(pdf_path)
        text = ""
        for img in images:
            text += pytesseract.image_to_string(img) + " "
        return text.strip()



def clean_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()



def extract_email(text):
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(com|in|org|net|edu)"
    match = re.search(pattern, text)
    return match.group(0) if match else None



def extract_phone(text):
    text = re.sub(r"[()\-\s]", "", text)
    pattern = r"(\+?\d{1,3})?\d{10}"
    match = re.search(pattern, text)
    return match.group(0) if match else None



def extract_skills(text):
    text = text.lower()
    return list(set([skill for skill in SKILL_KEYWORDS if skill in text]))



def process_resume(pdf_path):
    raw = read_pdf(pdf_path)
    cleaned = clean_text(raw)

    email = extract_email(raw)
    phone = extract_phone(raw)
    skills = extract_skills(cleaned)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO resumes (
            candidate_name, target_role, email, number,
            raw_text, clean_text, skills_extracted, tokens
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        None, None, email, phone,
        raw, cleaned, ", ".join(skills), None
    ))

    resume_id = cursor.lastrowid

    for skill in skills:
        cursor.execute("""
            INSERT INTO resume_skills (
                resume_id, skill_name, skill_type, proficiency_level
            )
            VALUES (?, ?, ?, ?)
        """, (resume_id, skill, "Technical", None))

    conn.commit()
    conn.close()

    return resume_id



def process_job_description(job_title, description):
    cleaned = clean_text(description)
    skills = extract_skills(cleaned)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs (
            job_title, company_name, location,
            required_skills, job_description,
            experience_level, clean_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        job_title, None, None,
        ", ".join(skills), description,
        None, cleaned
    ))

    job_id = cursor.lastrowid

    for skill in skills:
        cursor.execute("""
            INSERT INTO job_skills (
                job_id, skill_name, occurrence
            )
            VALUES (?, ?, ?)
        """, (job_id, skill, 1))

    conn.commit()
    conn.close()

    return job_id



def calculate_match(resume_id, job_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT skill_name FROM resume_skills WHERE resume_id=?", (resume_id,))
    resume_skills = {row[0].lower() for row in cursor.fetchall()}

    cursor.execute("SELECT skill_name FROM job_skills WHERE job_id=?", (job_id,))
    job_skills = {row[0].lower() for row in cursor.fetchall()}

    conn.close()

    if not job_skills:
        return 0, [], []

    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills
    percentage = (len(matched) / len(job_skills)) * 100

    return round(percentage, 2), list(matched), list(missing)



if __name__ == "__main__":

    initialize_database()

    resume_path = r"C:\Users\gayaz\Desktop\project\data\resume_samples\resume sample 2.pdf"

    resume_id = process_resume(resume_path)

    job_description_text = """
    We are hiring a Python Developer.
    Required skills: Python, SQL, Django, Git, Linux.
    Experience with AWS and REST API is preferred.
    """

    job_id = process_job_description("Python Developer", job_description_text)

    percentage, matched, missing = calculate_match(resume_id, job_id)

    print("\nMATCH RESULT : ")
    print("Match Percentage:", percentage, "%")
    print("Matched Skills:", matched)
    print("Missing Skills:", missing)

