const WORKER_URL = "https://cybergrind-epss-worker.wacker-jason.workers.dev";

async function lookupCVE() {
  const cve = document.getElementById("cve-input").value.trim();
  const resultDiv = document.getElementById("result");

  if (!cve) return;

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Looking up " + cve + "...</p>";

  try {
    const res = await fetch(`${WORKER_URL}?cve=${encodeURIComponent(cve)}`);
    const data = await res.json();

    if (data.error) {
      resultDiv.innerHTML = `<p style="color:#ff4444;">Error: ${data.error}</p>`;
      return;
    }

    resultDiv.innerHTML = `
      <h3>${data.cve}</h3>
      <p>EPSS Score: <strong>${(data.epss_score * 100).toFixed(2)}%</strong></p>
      <p>Percentile: <strong>${(data.percentile * 100).toFixed(1)}th</strong></p>
      <p>Risk Level: <strong class="risk-${data.risk_level}">${data.risk_level}</strong></p>
      <p style="color:#888; font-size:0.85rem;">Data as of ${data.date}</p>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("lookup-btn").addEventListener("click", lookupCVE);
  document.getElementById("cve-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") lookupCVE();
  });
});