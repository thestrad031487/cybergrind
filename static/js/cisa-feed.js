const CISA_FEED_URL = "https://cybergrind-cisa-worker.wacker-jason.workers.dev";

async function loadCISAFeed() {
  const status = document.getElementById("kev-feed-status");
  const cards = document.getElementById("kev-cards");

  try {
    const res = await fetch(CISA_FEED_URL);
    const data = await res.json();

    cards.innerHTML = data.recent.map(v => `
      <div class="kev-card">
        <a class="kev-card-cve" href="https://nvd.nist.gov/vuln/detail/${v.cveID}" target="_blank" rel="noopener">${v.cveID}</a>
        <div class="kev-card-name">${v.vulnerabilityName}</div>
        <div class="kev-card-vendor">${v.vendorProject} — ${v.product}</div>
        <div class="kev-card-desc">${v.shortDescription}</div>
        <div class="kev-card-meta">
          <span class="kev-badge kev-badge-date">Added ${new Date(v.dateAdded).toLocaleDateString()}</span>
          <span class="kev-badge kev-badge-due">Due ${new Date(v.dueDate).toLocaleDateString()}</span>
          <span class="kev-badge ${v.ransomware === 'Known' ? 'kev-badge-ransomware-known' : 'kev-badge-ransomware-unknown'}">
            ${v.ransomware === 'Known' ? '⚠ Ransomware' : 'Ransomware Unknown'}
          </span>
        </div>
      </div>
    `).join("");

    status.style.display = "none";

  } catch (err) {
    status.textContent = "Failed to load CISA feed: " + err.message;
  }
}

document.addEventListener("DOMContentLoaded", loadCISAFeed);