// Escape untrusted text before it goes into innerHTML (added 2026-11 audit)
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
function safeUrl(u) { try { const x = new URL(u); return (x.protocol === 'https:' || x.protocol === 'http:') ? x.href : '#'; } catch (e) { return '#'; } }

const WORKER_URL = "https://cybergrind-ip-worker.wacker-jason.workers.dev";

async function lookupIP() {
  const ip = document.getElementById("ip-input").value.trim();
  const resultDiv = document.getElementById("result");

  if (!ip) return;

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Looking up " + esc(ip) + "...</p>";

  try {
    const res = await fetch(`${WORKER_URL}?ip=${encodeURIComponent(ip)}`);
    const data = await res.json();

    if (data.error) {
      resultDiv.innerHTML = `<p style="color:#ff4444;">Error: ${esc(data.error)}</p>`;
      return;
    }

    resultDiv.innerHTML = `
      <h3>${esc(data.ip)}</h3>
      <table class="result-table">
        <tr><td>Risk Level</td><td><strong class="risk-${esc(data.risk_level)}">${esc(data.risk_level)}</strong></td></tr>
        <tr><td>Abuse Confidence</td><td><strong>${esc(data.abuse_confidence)}%</strong></td></tr>
        <tr><td>Country</td><td>${esc(data.country)}</td></tr>
        <tr><td>ISP</td><td>${esc(data.isp)}</td></tr>
        <tr><td>Domain</td><td>${esc(data.domain || "N/A")}</td></tr>
        <tr><td>Usage Type</td><td>${esc(data.usage_type || "N/A")}</td></tr>
        <tr><td>Total Reports</td><td>${esc(data.total_reports)}</td></tr>
        <tr><td>Last Reported</td><td>${data.last_reported ? new Date(data.last_reported).toLocaleDateString() : "Never"}</td></tr>
        <tr><td>Tor Exit Node</td><td>${data.is_tor ? "Yes" : "No"}</td></tr>
      </table>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${esc(err.message)}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("lookup-btn").addEventListener("click", lookupIP);
  document.getElementById("ip-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") lookupIP();
  });
});