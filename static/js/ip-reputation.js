const WORKER_URL = "https://cybergrind-ip-worker.wacker-jason.workers.dev";

async function lookupIP() {
  const ip = document.getElementById("ip-input").value.trim();
  const resultDiv = document.getElementById("result");

  if (!ip) return;

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Looking up " + ip + "...</p>";

  try {
    const res = await fetch(`${WORKER_URL}?ip=${encodeURIComponent(ip)}`);
    const data = await res.json();

    if (data.error) {
      resultDiv.innerHTML = `<p style="color:#ff4444;">Error: ${data.error}</p>`;
      return;
    }

    resultDiv.innerHTML = `
      <h3>${data.ip}</h3>
      <table class="result-table">
        <tr><td>Risk Level</td><td><strong class="risk-${data.risk_level}">${data.risk_level}</strong></td></tr>
        <tr><td>Abuse Confidence</td><td><strong>${data.abuse_confidence}%</strong></td></tr>
        <tr><td>Country</td><td>${data.country}</td></tr>
        <tr><td>ISP</td><td>${data.isp}</td></tr>
        <tr><td>Domain</td><td>${data.domain || "N/A"}</td></tr>
        <tr><td>Usage Type</td><td>${data.usage_type || "N/A"}</td></tr>
        <tr><td>Total Reports</td><td>${data.total_reports}</td></tr>
        <tr><td>Last Reported</td><td>${data.last_reported ? new Date(data.last_reported).toLocaleDateString() : "Never"}</td></tr>
        <tr><td>Tor Exit Node</td><td>${data.is_tor ? "Yes" : "No"}</td></tr>
      </table>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("lookup-btn").addEventListener("click", lookupIP);
  document.getElementById("ip-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") lookupIP();
  });
});