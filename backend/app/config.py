import os

# Base paths
# Points to the main project root folder
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CONFIG_DIR)
PROJECT_ROOT = os.path.dirname(BASE_DIR)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, "uploads")
DATABASE = os.path.join(BASE_DIR, "career_guidance.db")
DATASET_PATH = os.path.join(BASE_DIR, "data", "internships.csv")

# Flask configurations
ALLOWED_EXTENSIONS = {"pdf"}
SECRET_KEY = os.environ.get("SECRET_KEY", "career-guidance-secret")
SESSION_LIFETIME_DAYS = 7

# Supported skills dictionary for PDF text parsing
SKILL_KEYWORDS = [
    "python", "sql", "java", "html", "css", "javascript",
    "react", "node", "django", "flask", "data analytics",
    "excel", "power bi", "tableau", "machine learning",
    "nlp", "azure", "aws", "git", "linux", "c++", "c#", "r", "matlab",
    "communication", "project management", "social media", "content creation",
    "digital marketing", "video editing", "graphic design", "sales", "finance"
]

# Educational suggestions mapped to skill keywords
COURSE_RECOMMENDATIONS = {
    "python": [
        "Python for Beginners on Coursera",
        "Automate tasks with Python"
    ],
    "sql": [
        "SQL Fundamentals from Khan Academy",
        "Databases and SQL for Data Science"
    ],
    "excel": [
        "Excel for data analysis",
        "Advanced spreadsheet skills"
    ],
    "power bi": [
        "Power BI data visualization",
        "Power BI for business analysts"
    ],
    "tableau": [
        "Data visualization with Tableau",
        "Tableau for Analytics"
    ],
    "html": [
        "HTML and CSS for Beginners",
        "Responsive Web Design"
    ],
    "css": [
        "Modern CSS Layout & Grid",
        "Responsive Web Design"
    ],
    "javascript": [
        "JavaScript Deep Dive on Udemy",
        "Advanced JS and Dom scripting"
    ],
    "react": [
        "React Native & Web Fundamentals",
        "Build modern SPAs with React"
    ],
    "communication": [
        "Business communication skills",
        "Professional presentation training"
    ]
}
