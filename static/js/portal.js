// Client-side Application Controller
import { parseCSV } from "./csv_parser.js";
import { calculateMatch, extractSkills } from "./matching_engine.js";
import { renderDashboardCards, renderTrendingSkills, renderCoursePathways } from "./portal_view.js";

const DEFAULT_PROFILE = {
  name: "Guest Student", email: "guest@example.com", career_goal: "Software Developer",
  preferred_domains: "Web, Software", preferred_locations: "Bangalore, Remote",
  interests: "Coding, React", technical_skills: "HTML, CSS, JavaScript",
  extracted_skills: "Python, SQL", availability_start: "Immediately",
  availability_duration: "6 Months", availability_type: "Any", completed_profile: true
};

let internshipsData = [];
let profileData = DEFAULT_PROFILE;

function getProfile() {
  const local = localStorage.getItem("career_profile");
  if (local) return JSON.parse(local);
  localStorage.setItem("career_profile", JSON.stringify(DEFAULT_PROFILE));
  return DEFAULT_PROFILE;
}

export async function initPortal() {
  profileData = getProfile();
  renderProfileFields();
  
  try {
    const res = await fetch("data/internships.csv");
    if (!res.ok) throw new Error("CSV fetch failed");
    const text = await res.text();
    internshipsData = parseCSV(text);
    renderDashboard(5);
  } catch (err) {
    document.getElementById("recommendations-container").innerHTML = 
      `<p class="loading-placeholder" style="color:#f87171;">⚠️ Failed to load internships dataset. Please ensure 'data/internships.csv' is committed.</p>`;
  }
}

function renderProfileFields() {
  const f = (id) => document.getElementById(id);
  if (!f("p-name")) return;
  f("p-name").value = profileData.name || "";
  f("p-email").value = profileData.email || "";
  f("p-goal").value = profileData.career_goal || "";
  f("p-domains").value = profileData.preferred_domains || "";
  f("p-locations").value = profileData.preferred_locations || "";
  f("p-interests").value = profileData.interests || "";
  f("p-skills").value = profileData.technical_skills || "";
  f("p-start").value = profileData.availability_start || "Immediately";
  f("p-dur").value = profileData.availability_duration || "Flexible";
  f("p-type").value = profileData.availability_type || "Any";
  
  document.getElementById("extracted-display").textContent = 
    profileData.extracted_skills || "Upload a PDF resume below to extract skills.";
}

export function saveProfile(formData) {
  const newProfile = { ...profileData, ...formData, completed_profile: true };
  localStorage.setItem("career_profile", JSON.stringify(newProfile));
  profileData = newProfile;
  renderProfileFields();
  renderDashboard(5);
  showToast("Profile and availability preferences recalculated!");
}

export async function handleResumeUpload(file) {
  if (!file) return;
  showToast("Extracting skills from resume PDF...");
  try {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = "";
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map(item => item.str).join(" ") + "\n";
    }
    const skills = extractSkills(text);
    profileData.extracted_skills = skills.join(", ");
    localStorage.setItem("career_profile", JSON.stringify(profileData));
    renderProfileFields();
    renderDashboard(5);
    showToast("PDF parsed! Matches recalculated.");
  } catch (err) {
    showToast("⚠️ Error parsing PDF resume.", true);
  }
}

function renderDashboard(limit = 5) {
  if (internshipsData.length === 0) return;
  const ranked = internshipsData.map(item => {
    const details = calculateMatch(profileData, item);
    return { ...item, ...details };
  }).sort((a, b) => b.score - a.score);

  renderDashboardCards(ranked, limit, () => renderDashboard(25));
  renderTrendingSkills(internshipsData);
  renderCoursePathways(ranked[0]);
}

function showToast(msg, isErr = false) {
  const t = document.createElement("div");
  t.style = `position:fixed;bottom:24px;right:24px;background:${isErr?'#ef4444':'#3D52A0'};color:#fff;padding:12px 24px;border-radius:10px;font-weight:600;box-shadow:0 10px 25px rgba(0,0,0,0.15);z-index:9999;transition:all 0.3s;`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => { t.style.opacity = 0; setTimeout(() => t.remove(), 300); }, 3000);
}
