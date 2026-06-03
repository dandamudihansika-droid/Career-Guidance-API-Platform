import sqlite3
from .config import DATABASE

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def get_user_by_email(email):
    return query_db("SELECT * FROM students WHERE email = ?", (email,), one=True)

def get_user_by_id(user_id):
    return query_db("SELECT * FROM students WHERE id = ?", (user_id,), one=True)

def save_user(name, email, password_hash):
    conn = get_db()
    conn.execute(
        "INSERT INTO students (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash),
    )
    conn.commit()
    conn.close()

def update_profile(user_id, goal, domains, locations, interests, skills, prefs, resume, ext_skills, start, dur, type_pref, pref_company):
    conn = get_db()
    conn.execute(
        """UPDATE students SET 
           career_goal=?, preferred_domains=?, preferred_locations=?, 
           interests=?, technical_skills=?, preferences=?, 
           resume_text=?, extracted_skills=?, availability_start=?, 
           availability_duration=?, availability_type=?, preferred_company=?, completed_profile=1 WHERE id=?""",
        (goal, domains, locations, interests, skills, prefs, resume, ext_skills, start, dur, type_pref, pref_company, user_id),
    )
    conn.commit()
    conn.close()

def check_internships_table_exists():
    conn = get_db()
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='internships'")
    exists = cur.fetchone() is not None
    conn.close()
    return exists

def get_all_internships():
    conn = get_db()
    rows = conn.execute("SELECT * FROM internships").fetchall()
    conn.close()
    return rows

def migrate_db(conn):
    # Perform column checking for dynamic updates
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in cursor.fetchall()]
    
    # Auto-add missing availability columns
    if "availability_start" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN availability_start TEXT")
    if "availability_duration" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN availability_duration TEXT")
    if "availability_type" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN availability_type TEXT")
    if "preferred_company" not in columns:
        conn.execute("ALTER TABLE students ADD COLUMN preferred_company TEXT")
    conn.commit()

def init_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password_hash TEXT,
            career_goal TEXT,
            preferred_domains TEXT,
            preferred_locations TEXT,
            interests TEXT,
            technical_skills TEXT,
            preferences TEXT,
            resume_text TEXT,
            extracted_skills TEXT,
            preferred_company TEXT,
            completed_profile INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            internship_id TEXT UNIQUE,
            profile TEXT,
            company TEXT,
            location TEXT,
            start_date TEXT,
            stipend TEXT,
            duration TEXT,
            apply_by TEXT,
            offer TEXT,
            education TEXT,
            skills TEXT,
            perks TEXT,
            description TEXT
        )
    """)
    conn.commit()
    migrate_db(conn)
    conn.close()

