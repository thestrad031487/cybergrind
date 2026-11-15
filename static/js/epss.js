// Escape untrusted text before it goes into innerHTML (added 2026-11 audit)
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function safeUrl(u) { try { const x = new URL(u); return (x.protocol === 'https:' || x.protocol === 'http:') ? x.href : '#'; } catch (e) { return '#'; } }

const WORKER_URL = "https://cybergrind-epss-worker.wacker-jason.workers.dev";

async function lookupCVE() {
  const cve = document.getElementById("cve-input").value.trim();
  const resultDiv = document.getElementById("result");

  if (!cve) return;

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Looking up " + esc(cve) + "...</p>";

  try {
    const res = await fetch(`${WORKER_URL}?cve=${encodeURIComponent(cve)}`);
    const data = await res.json();

    if (data.error) {
      resultDiv.innerHTML = `<p style="color:#ff4444;">Error: ${esc(data.error)}</p>`;
      return;
    }

    resultDiv.innerHTML = `
      <h3>${esc(data.cve)}</h3>
      <p>EPSS Score: <strong>${(data.epss_score * 100).toFixed(2)}%</strong></p>
      <p>Percentile: <strong>${(data.percentile * 100).toFixed(1)}th</strong></p>
      <p>Risk Level: <strong class="risk-${esc(data.risk_level)}">${esc(data.risk_level)}</strong></p>
      <p style="color:#888; font-size:0.85rem;">Data as of ${esc(data.date)}</p>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${esc(err.message)}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("lookup-btn").addEventListener("click", lookupCVE);
  document.getElementById("cve-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") lookupCVE();
  });
});