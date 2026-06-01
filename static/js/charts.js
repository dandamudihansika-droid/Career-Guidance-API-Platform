// Chart Analytics for Local Flask Application
window.initDomainChart = function(skillsStr) {
  const canvas = document.getElementById('domain-chart');
  if (!canvas) return;

  const skills = (skillsStr || "").toLowerCase();
  const domains = [
    { name: "Web Dev", keywords: ["html", "css", "javascript", "react", "node", "django", "flask"] },
    { name: "Data Analytics", keywords: ["python", "sql", "excel", "power bi", "tableau", "data analytics"] },
    { name: "Software Eng", keywords: ["java", "c++", "c#", "git", "linux"] },
    { name: "Marketing", keywords: ["marketing", "social media", "content", "sales", "communication"] },
    { name: "Design & UX", keywords: ["design", "graphic", "video", "editing", "photoshop", "figma"] }
  ];

  const scores = domains.map(d => {
    let matches = 0;
    d.keywords.forEach(k => { if (skills.includes(k)) matches++; });
    return Math.min(25 + (matches * 25), 100);
  });

  if (window.myDomainChart) {
    window.myDomainChart.destroy();
  }

  const ctx = canvas.getContext('2d');
  window.myDomainChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: domains.map(d => d.name),
      datasets: [{
        label: 'Domain Match Score %',
        data: scores,
        backgroundColor: 'rgba(61, 82, 160, 0.15)',
        borderColor: '#3D52A0',
        borderWidth: 2,
        pointBackgroundColor: '#7091E6',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#3D52A0',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        r: {
          angleLines: { color: 'rgba(61, 82, 160, 0.08)' },
          grid: { color: 'rgba(61, 82, 160, 0.08)' },
          pointLabels: {
            font: { family: 'Outfit', size: 10, weight: '700' },
            color: '#64748b'
          },
          ticks: { display: false, stepSize: 20 },
          min: 0,
          max: 100
        }
      }
    }
  });
}
