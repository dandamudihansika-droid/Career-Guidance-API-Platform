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

export async function initPortal() {
  profileData = localStorage.getItem("career_profile") ? JSON.parse(localStorage.getItem("career_profile")) : DEFAULT_PROFILE;
  renderProfileFields();
  setupEventListeners();
  
  try {
    const res = await fetch("../backend/data/internships.csv");
    if (!res.ok) throw new Error("CSV fetch failed");
    const text = await res.text();
    internshipsData = parseCSV(text);
    renderDashboard(5);
  } catch (err) {
    document.getElementById("recommendations-container").innerHTML = 
      `<p class="loading-placeholder" style="color:#f87171;">⚠️ Failed to load dataset.</p>`;
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
  document.getElementById("extracted-display").textContent = profileData.extracted_skills || "None";

  const t = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val || "Not specified"; };
  t("sum-goal", profileData.career_goal);
  t("sum-locations", profileData.preferred_locations);
  t("sum-start", profileData.availability_start);
  t("sum-mode", profileData.availability_type + " · " + profileData.availability_duration);

  const renderBadges = (id, text) => {
    const el = document.getElementById(id);
    if (!el) return;
    if (!text || text.toLowerCase() === "none" || text.toLowerCase() === "not specified") {
      el.innerHTML = `<span class="muted" style="font-size:0.8rem;color:#94a3b8;">None</span>`;
      return;
    }
    el.innerHTML = text.split(/[\n,;]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0)
      .map(s => `<span class="badge secondary" style="font-size:0.75rem;margin-right:0.25rem;margin-bottom:0.25rem;">${s}</span>`)
      .join("");
  };
  renderBadges("sum-skills", profileData.technical_skills);
  renderBadges("sum-extracted", profileData.extracted_skills);
}

function setupEventListeners() {
  const switchTab = (tab) => {
    const act = (id, show) => document.getElementById(id).classList.toggle("active", show);
    act("tab-dash", tab === "dash"); act("tab-profile", tab === "profile");
    act("btn-dash", tab === "dash"); act("btn-profile", tab === "profile");
  };

  document.getElementById("btn-dash").onclick = () => switchTab("dash");
  document.getElementById("btn-profile").onclick = () => switchTab("profile");

  document.getElementById("profile-form").onsubmit = (e) => {
    e.preventDefault();
    const fd = {
      name: document.getElementById("p-name").value,
      email: document.getElementById("p-email").value,
      career_goal: document.getElementById("p-goal").value,
      preferred_domains: document.getElementById("p-domains").value,
      preferred_locations: document.getElementById("p-locations").value,
      interests: document.getElementById("p-interests").value,
      technical_skills: document.getElementById("p-skills").value,
      availability_start: document.getElementById("p-start").value,
      availability_duration: document.getElementById("p-dur").value,
      availability_type: document.getElementById("p-type").value
    };
    saveProfile(fd);
    switchTab("dash");
  };

  document.getElementById("p-resume").onchange = (e) => {
    if (e.target.files.length > 0) handleResumeUpload(e.target.files[0]);
  };
}

function saveProfile(formData) {
  const newProfile = { ...profileData, ...formData, completed_profile: true };
  localStorage.setItem("career_profile", JSON.stringify(newProfile));
  profileData = newProfile;
  renderProfileFields();
  renderDashboard(5);
  showToast("Profile recalculated!");
}

async function handleResumeUpload(file) {
  showToast("Extracting PDF skills...");
  try {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let text = "";
    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      text += content.items.map(item => item.str).join(" ") + "\n";
    }
    profileData.extracted_skills = extractSkills(text).join(", ");
    localStorage.setItem("career_profile", JSON.stringify(profileData));
    renderProfileFields();
    renderDashboard(5);
    showToast("PDF parsed successfully!");
  } catch (err) {
    showToast("⚠️ Error parsing PDF.", true);
  }
}

function renderDashboard(limit = 5) {
  if (internshipsData.length === 0) return;
  const ranked = internshipsData.map(item => {
    return { ...item, ...calculateMatch(profileData, item) };
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
