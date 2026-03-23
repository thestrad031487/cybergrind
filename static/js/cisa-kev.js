const KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json";

let kevData = null;

async function loadKEV() {
  if (kevData) return kevData;
  const res = await fetch(KEV_URL);
  const data = await res.json();
  kevData = data.vulnerabilities;
  return kevData;
}

async function lookupKEV() {
  const cve = document.getElementById("cve-input").value.trim().toUpperCase();
  const resultDiv = document.getElementById("result");

  if (!cve) return;

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Checking CISA KEV catalog for " + cve + "...</p>";

  try {
    const vulns = await loadKEV();
    const match = vulns.find(v => v.cveID.toUpperCase() === cve);

    if (!match) {
      resultDiv.innerHTML = `
        <div class="not-found">
          <div class="status-badge not-in-kev">✗ Not in KEV Catalog</div>
          <p><strong>${cve}</strong> is not currently listed in the CISA Known Exploited Vulnerabilities catalog.</p>
          <p class="note">This does not mean the CVE is not dangerous — it means CISA has not confirmed active exploitation in the wild.</p>
        </div>
      `;
      return;
    }

    resultDiv.innerHTML = `
      <div class="found">
        <div class="status-badge in-kev">✓ In KEV Catalog</div>
        <h3>${match.cveID}</h3>
        <p class="vuln-name">${match.vulnerabilityName}</p>

        <table class="result-table">
          <tr><td>Vendor</td><td>${match.vendorProject}</td></tr>
          <tr><td>Product</td><td>${match.product}</td></tr>
          <tr><td>Date Added</td><td>${new Date(match.dateAdded).toLocaleDateString()}</td></tr>
          <tr><td>Due Date</td><td><strong class="due-date">${new Date(match.dueDate).toLocaleDateString()}</strong></td></tr>
          <tr><td>Ransomware Use</td><td class="${match.knownRansomwareCampaignUse === 'Known' ? 'ransomware-known' : 'ransomware-unknown'}">${match.knownRansomwareCampaignUse}</td></tr>
          <tr><td>Required Action</td><td>${match.requiredAction}</td></tr>
        </table>

        <div class="description">
          <h4>Description</h4>
          <p>${match.shortDescription}</p>
        </div>

        <a class="kev-link" href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" rel="noopener">
          View full KEV catalog →
        </a>
      </div>
    `;

  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("lookup-btn").addEventListener("click", lookupKEV);
  document.getElementById("cve-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") lookupKEV();
  });
});