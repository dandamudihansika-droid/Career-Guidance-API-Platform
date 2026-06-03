import os
from flask import Blueprint, jsonify, request, session, current_app
from werkzeug.utils import secure_filename
from .db import get_user_by_id, update_profile
from .utils import load_internships, allowed_file, extract_text_from_pdf, extract_skills
from .recommender import calculate_match, trending_skills

api_bp = Blueprint("api", __name__)

@api_bp.route("/api/recommendations", methods=["GET"])
def get_recommendations():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = get_user_by_id(session["user_id"])
    if not user or not user["completed_profile"]:
        return jsonify({"error": "Profile incomplete", "code": "PROFILE_INCOMPLETE"}), 400

    profile = dict(user)
    internships = load_internships()
    ranked = []
    
    for item in internships:
        match_details = calculate_match(profile, item)
        ranked.append({**item, **match_details})
        
    ranked.sort(key=lambda x: x["score"], reverse=True)
    
    limit_val = request.args.get("limit", "5")
    if limit_val.lower() == "all":
        results = ranked
    else:
        try:
            results = ranked[:int(limit_val)]
        except ValueError:
            results = ranked[:5]
            
    return jsonify({
        "recommendations": results,
        "completed": True
    })

@api_bp.route("/api/trending", methods=["GET"])
def get_trending():
    internships = load_internships()
    trending = trending_skills(internships)
    return jsonify({"trending": trending})

@api_bp.route("/api/profile", methods=["POST"])
def save_profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    user = get_user_by_id(session["user_id"])
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Extract form fields
    goal = request.form.get("career_goal", "").strip()
    domains = request.form.get("preferred_domains", "").strip()
    locs = request.form.get("preferred_locations", "").strip()
    interests = request.form.get("interests", "").strip()
    skills = request.form.get("technical_skills", "").strip()
    prefs = request.form.get("preferences", "").strip()
    start = request.form.get("availability_start", "Immediately").strip()
    dur = request.form.get("availability_duration", "Flexible").strip()
    type_pref = request.form.get("availability_type", "Any").strip()
    pref_company = request.form.get("preferred_company", "Any").strip()

    resume_text = user["resume_text"] or ""
    ext_skills = user["extracted_skills"] or ""
    
    resume_file = request.files.get("resume")
    if resume_file and resume_file.filename:
        if allowed_file(resume_file.filename):
            filename = secure_filename(resume_file.filename)
            upload_dir = current_app.config["UPLOAD_FOLDER"]
            os.makedirs(upload_dir, exist_ok=True)
            
            path = os.path.join(upload_dir, filename)
            resume_file.save(path)
            
            resume_text = extract_text_from_pdf(path)
            ext_skills = ", ".join(extract_skills(resume_text))
        else:
            return jsonify({"error": "Only PDF files are supported"}), 400

    update_profile(
        user["id"], goal, domains, locs, interests, skills, prefs,
        resume_text, ext_skills, start, dur, type_pref, pref_company
    )

    # Spawn background thread for match recommendations notification email
    try:
        updated_profile = {
            "technical_skills": skills, "extracted_skills": ext_skills, "interests": interests,
            "preferred_company": pref_company, "preferred_domains": domains, "career_goal": goal,
            "preferred_locations": locs, "availability_type": type_pref, "availability_start": start,
            "availability_duration": dur
        }
        from .email_service import send_profile_matches_email
        import threading
        
        ranked = [{**item, **calculate_match(updated_profile, item)} for item in load_internships()]
        ranked.sort(key=lambda x: x["score"], reverse=True)
        
        threading.Thread(
            target=send_profile_matches_email,
            args=(user["email"], user["name"], pref_company, ranked[:3]),
            daemon=True
        ).start()
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to spawn matching email thread: {e}")

    return jsonify({"message": "Profile saved successfully", "success": True})

@api_bp.route("/api/profile/skills", methods=["PUT"])
def update_skills_only():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    new_skills = (request.get_json() or {}).get("skills", "").strip()
    from .db import query_db
    query_db("UPDATE students SET technical_skills = ? WHERE id = ?", (new_skills, session["user_id"]))
    return jsonify({"message": "Skills updated successfully via PUT", "skills": new_skills})

@api_bp.route("/api/profile/resume", methods=["DELETE"])
def delete_resume_only():
    if "user_id" not in session: return jsonify({"error": "Unauthorized"}), 401
    from .db import query_db
    query_db("UPDATE students SET resume_text = NULL, extracted_skills = NULL WHERE id = ?", (session["user_id"],))
    return jsonify({"message": "Resume data cleared successfully via DELETE"})

@api_bp.route("/api/test-email", methods=["POST"])
def test_email_endpoint():
    data = request.get_json(silent=True, force=True) or {}
    to_email = (data.get("email") or request.form.get("email") or "").strip()
    if not to_email: return jsonify({"error": "Email parameter is required"}), 400
    from .email_service import send_html_email
    subj, fall = "SMTP Test Connection", "Test email from Career Guidance."
    html = "<html><body><h2>SMTP Connection Working!</h2></body></html>"
    if send_html_email(to_email, subj, html, fall):
        return jsonify({"success": True, "message": f"SMTP test sent to {to_email}", "mode": "SMTP"})
    from .config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD
    missing = [k for k, v in [("SMTP_SERVER", SMTP_SERVER), ("SMTP_PORT", SMTP_PORT), ("SMTP_EMAIL", SMTP_EMAIL), ("SMTP_PASSWORD", SMTP_PASSWORD)] if not v]
    return jsonify({"success": False, "message": f"SMTP failed. Missing variables: {', '.join(missing)}" if missing else "SMTP failed. Check console trace.", "mode": "Demo"}), 500
