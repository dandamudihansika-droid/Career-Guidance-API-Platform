import os
import sqlite3
import pandas as pd
from app.config import DATABASE, DATASET_PATH
from app.db import init_database

def load_dataset():
    if not os.path.exists(DATASET_PATH):
        return []
    
    df = pd.read_csv(DATASET_PATH)
    records = []
    
    for _, row in df.iterrows():
        records.append((
            str(row.get("internship_id") or "").strip(),
            str(row.get("profile") or row.get("Profile") or "").strip(),
            str(row.get("company") or "").strip(),
            str(row.get("Location") or row.get("location") or "").strip(),
            str(row.get("Start Date") or row.get("start_date") or "Immediately").strip(),
            str(row.get("Stipend") or row.get("stipend") or "").strip(),
            str(row.get("Duration") or row.get("duration") or "").strip(),
            str(row.get("Apply by Date") or row.get("apply_by") or "Flexible").strip(),
            str(row.get("Offer") or row.get("offer") or "").strip(),
            str(row.get("Education") or row.get("education") or "").strip(),
            str(row.get("Skills") or row.get("skills") or "").strip(),
            str(row.get("Perks") or row.get("perks") or "").strip(),
            str(row.get("description") or row.get("Description") or "").strip(),
        ))
    return records

def populate_internships():
    # Make sure students and internships tables are active
    init_database()
    
    records = load_dataset()
    if not records:
        print("No internship records found in internships.csv.")
        return
        
    conn = sqlite3.connect(DATABASE)
    conn.execute("DELETE FROM internships")
    
    conn.executemany(
        """INSERT OR REPLACE INTO internships (
            internship_id, profile, company, location, start_date, 
            stipend, duration, apply_by, offer, education, skills, 
            perks, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        records
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
    conn.close()
    
    print(f"Loaded {count} internship records into database at {DATABASE}.")

if __name__ == "__main__":
    populate_internships()
