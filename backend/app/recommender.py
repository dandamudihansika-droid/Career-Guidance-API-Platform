import re
from .config import COURSE_RECOMMENDATIONS
from .utils import build_skill_set, normalize_list

def extract_months(duration_str):
    if not duration_str:
        return 0
    # Search for digits in strings like "3 Months" or "6 Months"
    match = re.search(r"\d+", str(duration_str))
    return int(match.group()) if match else 0

def calculate_match(profile, internship):
    score = 0.0
    reasons = []

    # 1. Skills Matching (Max 40 points)
    p_skills = build_skill_set(profile)
    i_skills = {s.lower() for s in internship["skills"]}
    common = p_skills & i_skills
    missing = i_skills - p_skills
    
    skill_score = 40.0 * (len(common) / max(len(i_skills), 1))
    score += skill_score
    if missing:
        reasons.append(f"Missing required skills: {', '.join(sorted([s.title() for s in missing]))}")

    # 1.1. Preferred Company Matching (Max 10 points)
    pref_company = (profile.get("preferred_company") or "").strip().lower()
    company_score = 10.0
    if pref_company and pref_company != "any" and pref_company != "any company":
        i_company = internship["company"].lower()
        if pref_company in i_company:
            company_score = 10.0
        else:
            company_score = 0.0
            reasons.append(f"Company mismatch: Role is at '{internship['company']}', but you prefer '{profile.get('preferred_company')}'")
    score += company_score

    # 2. Domain & Career Goal Matching (Max 15 points)
    domains = [d.lower() for d in normalize_list(profile.get("preferred_domains", ""))]
    goal = (profile.get("career_goal") or "").lower()
    title = internship["profile"].lower()
    
    domain_match = any(d in title for d in domains) if domains else False
    goal_words = [w.strip() for w in goal.split() if len(w.strip()) > 2]
    goal_match = any(w in title for w in goal_words) if goal_words else False

    if domain_match or goal_match:
        score += 15.0
    else:
        reasons.append(f"Domain mismatch: Role '{internship['profile']}' does not match your preferred domains or career goals.")

    # 3. Location/Mode Matching (Max 15 points)
    pref_locs = [l.lower() for l in normalize_list(profile.get("preferred_locations", ""))]
    type_pref = (profile.get("availability_type") or "Any").lower()
    i_loc = internship["location"].lower()

    mode_match = True
    if "home" in type_pref or "remote" in type_pref:
        if "home" not in i_loc and "remote" not in i_loc:
            mode_match = False
            reasons.append(f"Location mode mismatch: Internship is on-site in '{internship['location']}', but you prefer WFH.")

    loc_match = any(loc in i_loc for loc in pref_locs) if pref_locs else True
    if not loc_match and mode_match:
        reasons.append(f"City mismatch: Internship is in '{internship['location']}', but your preferred cities are: {profile.get('preferred_locations')}.")
        
    if mode_match and loc_match:
        score += 15.0

    # 4. Start Date Matching (Max 10 points)
    p_start = (profile.get("availability_start") or "Immediately").lower()
    i_start = (internship.get("start_date") or "Immediately").lower()

    if "immed" in p_start or "immed" in i_start or p_start == i_start:
        score += 10.0
    else:
        reasons.append(f"Start date gap: Internship starts '{internship.get('start_date')}', but you are available '{profile.get('availability_start')}'.")

    # 5. Duration Matching (Max 10 points)
    p_dur = profile.get("availability_duration") or "Flexible"
    i_dur = internship["duration"]
    
    p_months = extract_months(p_dur)
    i_months = extract_months(i_dur)

    if "flex" in str(p_dur).lower() or p_months >= i_months:
        score += 10.0
    else:
        reasons.append(f"Duration gap: Internship requires '{i_dur}', but you are available for '{p_dur}'.")

    return {
        "score": round(score, 1),
        "common": sorted([s.title() for s in common]),
        "missing": sorted([s.title() for s in missing]),
        "lagging_reasons": reasons
    }

def recommend_courses(missing_skills):
    suggestions = []
    for skill in missing_skills:
        key = skill.lower()
        if key in COURSE_RECOMMENDATIONS:
            suggestions.append({"skill": skill, "courses": COURSE_RECOMMENDATIONS[key]})
    if not suggestions:
        suggestions.append({
            "skill": "Career readiness",
            "courses": [
                "Build a strong portfolio of project work",
                "Follow guided internship preparation pathways"
            ]
        })
    return suggestions

def trending_skills(internships):
    counter = {}
    for internship in internships:
        for skill in internship["skills"]:
            normalized = skill.strip().lower()
            if normalized:
                counter[normalized] = counter.get(normalized, 0) + 1
    sorted_skills = sorted(counter.items(), key=lambda item: item[1], reverse=True)
    return [skill.title() for skill, _ in sorted_skills[:8]]
