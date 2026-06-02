# Smart Career Guidance Platform

A polished student internship recommendation system built with **Flask**, **SQLite**, **Pandas**, and **PDF resume skill extraction**.

## What this project includes

- Secure student registration and login
- Complete profile creation: career goal, domains, locations, interests, skills, and preferences
- Resume upload in PDF format with automatic skill extraction
- Personalized internship matching using your profile and dataset requirements
- Missing skill analysis and course recommendations
- Trending technology skills from the internship dataset
- Clean dark theme frontend with responsive dashboard UI

## Setup

1. Open a terminal in this project folder.
2. Create a virtual environment:

```powershell
python -m venv venv
```

3. Activate the environment:

```powershell
venv\Scripts\Activate.ps1
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Initialize the database and load internship data from the CSV:

```powershell
python init_db.py
```

6. Start the application:

```powershell
python app.py
```

7. Open the app in your browser:

```text
http://127.0.0.1:5000
```

## Dataset

The internship dataset is stored in `data/internships.csv`.

The current dataset columns include:
- `internship_id`
- `profile`
- `company`
- `Location`
- `Skills`
- `Stipend`
- `Duration`
- `Offer`
- `Education`
- `Perks`

You can replace this file with another dataset as long as it contains the internship title, company, location, skills, and optional stipend/duration fields.

## Project structure

- `app.py` — Flask backend and recommendation engine
- `init_db.py` — database setup for SQLite
- `data/internships.csv` — internship dataset used for matching and trends
- `templates/` — HTML templates for login, registration, profile, and dashboard
- `static/css/style.css` — dark theme styles
- `static/js/main.js` — small UI enhancements

## Notes

- The recommendation engine is rule-based and does not rely on ML libraries.
- Resume parsing is done with `PyPDF2` and extracts keywords using a skill dictionary.
- The dashboard shows top internship matches, missing skills, and learning suggestions.

## Improvement ideas

- Add resume preview and more file validation
- Expand course recommendation logic for additional skill areas
- Add charts for skill gaps, internship trends, and match history
