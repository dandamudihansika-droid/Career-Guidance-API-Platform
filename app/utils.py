import re
import os
import pandas as pd
from PyPDF2 import PdfReader
from .config import SKILL_KEYWORDS, DATASET_PATH

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() == "pdf"

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
    return "\n".join(pages)

def extract_skills(text):
    lower = (text or "").lower()
    found = set()
    for keyword in SKILL_KEYWORDS:
        if keyword in lower:
            # We match full word or sub-word bounds
            found.add(keyword.title())
    return sorted(found)

def normalize_list(text):
    if not text:
        return []
    return [item.strip() for item in re.split(r"[\n,;]+", str(text)) if item.strip()]

def build_skill_set(profile):
    skills = set(normalize_list(profile.get("technical_skills", "")))
    skills |= set(normalize_list(profile.get("extracted_skills", "")))
    skills |= set(normalize_list(profile.get("interests", "")))
    return {skill.lower() for skill in skills}

def map_db_row_to_dict(row):
    return {
        "id": row["internship_id"] or str(row["id"]),
        "title": row["profile"] or "Internship Opportunity",
        "profile": row["profile"],
        "company": row["company"],
        "location": row["location"],
        "description": row["description"],
        "requirements": row["description"],
        "skills": normalize_list(row["skills"]),
        "stipend": row["stipend"],
        "duration": row["duration"],
        "start_date": row["start_date"] or "Immediately",
        "apply_by": row["apply_by"] or "Flexible"
    }

def load_internships():
    from .db import check_internships_table_exists, get_db
    if check_internships_table_exists():
        conn = get_db()
        rows = conn.execute("SELECT * FROM internships").fetchall()
        conn.close()
        return [map_db_row_to_dict(row) for row in rows]
    
    if not os.path.exists(DATASET_PATH):
        return []
    
    df = pd.read_csv(DATASET_PATH)
    internships = []
    for _, row in df.iterrows():
        title = str(row.get("profile") or row.get("Profile") or "").strip()
        internships.append({
            "id": str(row.get("internship_id") or row.get("id") or "").strip(),
            "title": title or "Internship Opportunity",
            "profile": title,
            "company": str(row.get("company") or row.get("Company") or "Unknown").strip(),
            "location": str(row.get("Location") or row.get("location") or "Remote").strip(),
            "description": str(row.get("description") or row.get("Description") or "").strip(),
            "requirements": str(row.get("requirements") or row.get("Requirements") or "").strip(),
            "skills": normalize_list(row.get("Skills") or row.get("skills") or ""),
            "stipend": str(row.get("Stipend") or row.get("stipend") or "Not specified").strip(),
            "duration": str(row.get("Duration") or row.get("duration") or "Flexible").strip(),
            "start_date": str(row.get("Start Date") or row.get("start_date") or "Immediately").strip(),
            "apply_by": str(row.get("Apply by Date") or row.get("apply_by") or "Flexible").strip()
        })
    return internships
