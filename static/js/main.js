document.addEventListener("DOMContentLoaded", () => {
  const recContainer = document.getElementById("recommendations-container");
  const trendingContainer = document.getElementById("trending-container");
  const coursesContainer = document.getElementById("courses-container");
  const profileForm = document.getElementById("profile-form");
  const fileInput = document.getElementById("resume");

  if (fileInput) {
    fileInput.addEventListener("change", (e) => {
      const infoText = document.querySelector(".file-info-text");
      if (e.target.files.length > 0) {
        infoText.textContent = `Selected file: ${e.target.files[0].name}`;
        infoText.style.color = "#3D52A0";
      }
    });
  }

  if (profileForm) {
    profileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = profileForm.querySelector("button[type='submit']");
      submitBtn.textContent = "Saving Profile & Calculations...";
      submitBtn.disabled = true;
      try {
        const formData = new FormData(profileForm);
        const res = await fetch("/api/profile", { method: "POST", body: formData });
        const data = await res.json();
        if (data.success) window.location.href = "/dashboard";
        else {
          alert(`Error saving profile: ${data.error}`);
          submitBtn.textContent = "Save Profile & Recalculate Matches";
          submitBtn.disabled = false;
        }
      } catch (err) {
        alert("Failed to submit profile to backend API.");
        submitBtn.disabled = false;
      }
    });
  }

  if (recContainer) loadDashboardData(5);

  async function loadDashboardData(limit = 5) {
    try {
      const recRes = await fetch(`/api/recommendations?limit=${limit}`);
      const recData = await recRes.json();

      if (recData.error) {
        if (recData.code === "PROFILE_INCOMPLETE") {
          recContainer.innerHTML = `<div class="loading-spinner-wrapper"><p>Please <a href="/profile" style="color:#3D52A0;font-weight:600;">complete your profile</a> to receive recommendations.</p></div>`;
          coursesContainer.innerHTML = "<p class='loading-placeholder'>Profile incomplete</p>";
        } else recContainer.innerHTML = `<p class='loading-placeholder'>Error: ${recData.error}</p>`;
        return;
      }

      const list = recData.recommendations || [];
      if (list.length === 0) {
        recContainer.innerHTML = "<p class='loading-placeholder'>No matching internships found.</p>";
        coursesContainer.innerHTML = "<p class='loading-placeholder'>All set</p>";
        return;
      }

      recContainer.innerHTML = "";
      list.forEach(item => {
        const skillsRow = item.skills.slice(0, 5).map(s => `<span class="badge secondary">${s}</span>`).join("");
        let mismatchSection = "";
        if (item.score < 100.0 && item.lagging_reasons && item.lagging_reasons.length > 0) {
          mismatchSection = `<div class="mismatch-card"><p class="mismatch-title">Match Gaps</p>${item.lagging_reasons.map(r => `<p class="mismatch-item">⚠️ ${r}</p>`).join("")}</div>`;
        }

        const card = document.createElement("article");
        card.className = "internship-card";
        card.innerHTML = `
          <div class="internship-header">
            <div>
              <h3>${item.title}</h3>
              <p class="muted">${item.company} · ${item.location}</p>
            </div>
            <div class="score-area">
              <div class="score-bar-bg"><div class="score-bar-fill" style="width: ${item.score}%"></div></div>
              <span class="score-num">${item.score}%</span>
            </div>
          </div>
          <div class="details-row">
            <span>📅 Start: ${item.start_date}</span>
            <span>⏱️ Duration: ${item.duration}</span>
            <span>💰 Stipend: ${item.stipend || 'Unspecified'}</span>
          </div>
          <div class="tag-row">${skillsRow}</div>
          ${mismatchSection}
        `;
        recContainer.appendChild(card);
      });

      if (limit === 5) {
        const showMoreBtn = document.createElement("button");
        showMoreBtn.className = "button primary";
        showMoreBtn.style.width = "100%";
        showMoreBtn.style.marginTop = "1rem";
        showMoreBtn.textContent = "Show More Matches (Top 25)";
        showMoreBtn.addEventListener("click", () => loadDashboardData(25));
        recContainer.appendChild(showMoreBtn);
      }

      const trendRes = await fetch("/api/trending");
      const trendData = await trendRes.json();
      trendingContainer.innerHTML = (trendData.trending || []).map(skill => `<span class="badge">${skill}</span>`).join("");

      // Draw Suitability Radar Chart
      const selfSkills = document.querySelector('.welcome-summary div:nth-child(5) .summary-val')?.textContent || "";
      const parsedSkills = document.querySelector('.welcome-summary div:nth-child(6) .summary-val')?.textContent || "";
      if (window.initDomainChart) {
        window.initDomainChart(selfSkills + ", " + parsedSkills);
      }

      const topMatch = list[0];
      if (topMatch && topMatch.missing && topMatch.missing.length > 0) {
        coursesContainer.innerHTML = "";
        const recCourses = {
          "python": ["Python Beginners - Coursera", "Automate with Python"],
          "sql": ["SQL fundamentals - Khan Academy", "SQL for Data Science"],
          "excel": ["Excel for data analysis", "Advanced spreadsheets"],
          "html": ["HTML & CSS for Beginners", "Responsive Web Design"],
          "css": ["Modern CSS layouts & Grid", "Responsive Web Design"],
          "javascript": ["JavaScript Deep Dive", "JS and DOM scripting"],
          "react": ["React Web Fundamentals", "Modern SPAs with React"]
        };

        topMatch.missing.slice(0, 3).forEach(skill => {
          const key = skill.toLowerCase();
          const listCourses = recCourses[key] || ["Build portfolio projects in this domain"];
          coursesContainer.innerHTML += `
            <div class="course-item">
              <p>${skill}</p>
              <ul class="course-list">${listCourses.map(c => `<li>• ${c}</li>`).join("")}</ul>
            </div>`;
        });
      } else {
        coursesContainer.innerHTML = "<p class='loading-placeholder'>No skill gaps detected. You are 100% matched!</p>";
      }
    } catch (err) {
      console.error(err);
      recContainer.innerHTML = "<p class='loading-placeholder'>Error fetching dynamic data.</p>";
    }
  }
});
