// Client-side Dashboard View Renderer
export function renderDashboardCards(ranked, limit, onShowMore) {
  const recContainer = document.getElementById("recommendations-container");
  if (!recContainer) return;
  recContainer.innerHTML = "";
  
  const slice = ranked.slice(0, limit);
  slice.forEach(item => {
    const skills = item.skills || item.Skills || "";
    const skillsRow = skills.split(/[\n,;]+/).slice(0, 5)
      .map(s => `<span class="badge secondary">${s.trim()}</span>`).join("");
    
    let mismatch = "";
    if (item.score < 100.0 && item.lagging_reasons && item.lagging_reasons.length > 0) {
      mismatch = `<div class="mismatch-card"><p class="mismatch-title">Match Gaps</p>
        ${item.lagging_reasons.map(r => `<p class="mismatch-item">⚠️ ${r}</p>`).join("")}</div>`;
    }

    const card = document.createElement("article");
    card.className = "internship-card";
    card.innerHTML = `
      <div class="internship-header">
        <div>
          <h3>${item.profile || item.Profile || "Internship Opportunity"}</h3>
          <p class="muted">${item.company || "Unknown Company"} · ${item.location || "Remote"}</p>
        </div>
        <div class="score-area">
          <div class="score-bar-bg"><div class="score-bar-fill" style="width: ${item.score}%"></div></div>
          <span class="score-num">${item.score}%</span>
        </div>
      </div>
      <div class="details-row">
        <span>📅 Start: ${item.start_date || item["Start Date"] || "Immediately"}</span>
        <span>⏱️ Duration: ${item.duration || item.Duration || "Flexible"}</span>
        <span>💰 Stipend: ${item.stipend || item.Stipend || "Unspecified"}</span>
      </div>
      <div class="tag-row">${skillsRow}</div>
      ${mismatch}
    `;
    recContainer.appendChild(card);
  });

  if (limit === 5 && ranked.length > 5) {
    const showMore = document.createElement("button");
    showMore.className = "button primary";
    showMore.style.width = "100%";
    showMore.style.marginTop = "1rem";
    showMore.textContent = "Show More Matches (Top 25)";
    showMore.onclick = onShowMore;
    recContainer.appendChild(showMore);
  }
}

export function renderTrendingSkills(internships) {
  const container = document.getElementById("trending-container");
  if (!container) return;
  const counts = {};
  internships.forEach(item => {
    const skills = item.skills || item.Skills || "";
    skills.split(/[\n,;]+/).forEach(s => {
      const normalized = s.trim().toLowerCase();
      if (normalized) counts[normalized] = (counts[normalized] || 0) + 1;
    });
  });
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 8);
  container.innerHTML = sorted.map(([skill]) => 
    `<span class="badge">${skill.charAt(0).toUpperCase() + skill.slice(1)}</span>`).join("");
}

export function renderCoursePathways(topMatch) {
  const container = document.getElementById("courses-container");
  if (!container) return;
  if (!topMatch || !topMatch.missing || topMatch.missing.length === 0) {
    container.innerHTML = "<p class='loading-placeholder'>No skill gaps detected. You are 100% matched!</p>";
    return;
  }
  
  const recCourses = {
    "python": ["Python Beginners - Coursera", "Automate with Python"],
    "sql": ["SQL fundamentals - Khan Academy", "SQL for Data Science"],
    "excel": ["Excel for data analysis", "Advanced spreadsheets"],
    "html": ["HTML & CSS for Beginners", "Responsive Web Design"],
    "css": ["Modern CSS layouts & Grid", "Responsive Web Design"],
    "javascript": ["JavaScript Deep Dive", "JS and DOM scripting"],
    "react": ["React Web Fundamentals", "Modern SPAs with React"]
  };

  container.innerHTML = "";
  topMatch.missing.slice(0, 3).forEach(skill => {
    const list = recCourses[skill.toLowerCase()] || ["Build portfolio projects in this domain"];
    container.innerHTML += `
      <div class="course-item">
        <p>${skill} <span style="font-size: 0.8rem; font-weight: normal; color: #94a3b8;">(Required by ${topMatch.company})</span></p>
        <ul class="course-list">${list.map(c => `<li>• ${c}</li>`).join("")}</ul>
      </div>`;
  });
}
