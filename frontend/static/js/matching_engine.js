// Client-side Availability and Skill Matching Engine
export const SKILL_KEYWORDS = [
  "python", "sql", "java", "html", "css", "javascript",
  "react", "node", "django", "flask", "data analytics",
  "excel", "power bi", "tableau", "machine learning",
  "nlp", "azure", "aws", "git", "linux", "c++", "c#", "r", "matlab",
  "communication", "project management", "social media", "content creation",
  "digital marketing", "video editing", "graphic design", "sales", "finance"
];

export function extractSkills(text) {
  const lower = (text || "").toLowerCase();
  const found = new Set();
  SKILL_KEYWORDS.forEach(keyword => {
    if (lower.includes(keyword)) {
      found.add(keyword.charAt(0).toUpperCase() + keyword.slice(1));
    }
  });
  return Array.from(found).sort();
}

function normalizeList(text) {
  if (!text) return [];
  return text.split(/[\n,;]+/).map(x => x.trim()).filter(x => x.length > 0);
}

function buildSkillSet(profile) {
  const skills = new Set();
  normalizeList(profile.technical_skills).forEach(s => skills.add(s.toLowerCase()));
  normalizeList(profile.extracted_skills).forEach(s => skills.add(s.toLowerCase()));
  normalizeList(profile.interests).forEach(s => skills.add(s.toLowerCase()));
  return skills;
}

function extractMonths(durationStr) {
  if (!durationStr) return 0;
  const match = String(durationStr).match(/\d+/);
  return match ? parseInt(match[0]) : 0;
}

export function calculateMatch(profile, internship) {
  let score = 0.0;
  const reasons = [];

  // 1. Skills Matching (Max 40 points)
  const pSkills = buildSkillSet(profile);
  const iSkills = new Set(normalizeList(internship.skills || internship.Skills).map(s => s.toLowerCase()));
  
  let commonCount = 0;
  const common = [];
  const missing = [];
  iSkills.forEach(s => {
    if (pSkills.has(s)) {
      commonCount++;
      common.push(s);
    } else {
      missing.push(s);
    }
  });

  const skillScore = 40.0 * (iSkills.size > 0 ? (commonCount / iSkills.size) : 1);
  score += skillScore;
  if (missing.length > 0) {
    reasons.push(`Missing skills: ${missing.map(s => s.charAt(0).toUpperCase() + s.slice(1)).sort().join(", ")}`);
  }

  // 1.1. Preferred Company Matching (Max 10 points)
  const prefCompany = (profile.preferred_company || "").trim().toLowerCase();
  let companyScore = 10.0;
  if (prefCompany && prefCompany !== "any" && prefCompany !== "any company") {
    const iCompany = (internship.company || "").toLowerCase();
    if (iCompany.includes(prefCompany)) {
      companyScore = 10.0;
    } else {
      companyScore = 0.0;
      reasons.push(`Company mismatch: Role is at '${internship.company}', but you prefer '${profile.preferred_company}'`);
    }
  }
  score += companyScore;

  // 2. Domain & Career Goal Matching (Max 15 points)
  const domains = normalizeList(profile.preferred_domains).map(d => d.toLowerCase());
  const goal = (profile.career_goal || "").toLowerCase();
  const title = (internship.profile || internship.Profile || "").toLowerCase();

  const domainMatch = domains.some(d => title.includes(d));
  const goalWords = goal.split(/\s+/).map(w => w.trim()).filter(w => w.length > 2);
  const goalMatch = goalWords.some(w => title.includes(w));

  if (domainMatch || goalMatch) {
    score += 15.0;
  } else {
    const displayRole = internship.profile || internship.Profile || "Role";
    reasons.push(`Domain mismatch: '${displayRole}' doesn't align with preferred domains or career goals.`);
  }

  // 3. Location/Mode Matching (Max 15 points)
  const prefLocs = normalizeList(profile.preferred_locations).map(l => l.toLowerCase());
  const typePref = (profile.availability_type || "Any").toLowerCase();
  const iLoc = (internship.location || internship.Location || "").toLowerCase();

  let modeMatch = true;
  if (typePref.includes("home") || typePref.includes("remote")) {
    if (!iLoc.includes("home") && !iLoc.includes("remote")) {
      modeMatch = false;
      const displayLoc = internship.location || internship.Location || "on-site";
      reasons.push(`Location mode mismatch: Internship is on-site in '${displayLoc}', but you prefer WFH.`);
    }
  }

  const locMatch = prefLocs.length > 0 ? prefLocs.some(loc => iLoc.includes(loc)) : true;
  if (!locMatch && modeMatch) {
    const displayLoc = internship.location || internship.Location || "another city";
    reasons.push(`City mismatch: Internship is in '${displayLoc}', but your preferred cities are: ${profile.preferred_locations}.`);
  }

  if (modeMatch && locMatch) {
    score += 15.0;
  }

  // 4. Start Date Matching (Max 10 points)
  const pStart = (profile.availability_start || "Immediately").toLowerCase();
  const iStart = (internship.start_date || internship["start date"] || "Immediately").toLowerCase();

  if (pStart.includes("immed") || iStart.includes("immed") || pStart === iStart) {
    score += 10.0;
  } else {
    const displayStart = internship.start_date || internship["start date"] || "Immediately";
    reasons.push(`Start date gap: Starts '${displayStart}', but you are available '${profile.availability_start}'.`);
  }

  // 5. Duration Matching (Max 10 points)
  const pDur = profile.availability_duration || "Flexible";
  const iDur = internship.duration || internship.Duration;

  const pMonths = extractMonths(pDur);
  const iMonths = extractMonths(iDur);

  if (pDur.toLowerCase().includes("flex") || pMonths >= iMonths) {
    score += 10.0;
  } else {
    reasons.push(`Duration gap: Requires '${iDur}', but you are available for '${pDur}'.`);
  }

  return {
    score: Math.round(score * 10) / 10,
    common: common.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
    missing: missing.map(s => s.charAt(0).toUpperCase() + s.slice(1)),
    lagging_reasons: reasons
  };
}
