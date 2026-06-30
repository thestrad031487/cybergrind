const WORKER_URL = "https://repo-scanner.cybergrind.org";

function parseRepoInput(value) {
  value = value.trim();
  const urlMatch = value.match(/github\.com\/([^\/]+)\/([^\/\s]+)/);
  if (urlMatch) return urlMatch[1] + "/" + urlMatch[2].replace(/\.git$/, "");
  if (/^[\w.-]+\/[\w.-]+$/.test(value)) return value;
  return null;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function renderResults(data) {
  const resultDiv = document.getElementById("result");
  const sev = data.summary.bySeverity;

  let html = `
    <div class="summary-grid">
      <div class="summary-card summary-critical"><div class="count">${sev.critical || 0}</div><div class="label">Critical</div></div>
      <div class="summary-card summary-high"><div class="count">${sev.high || 0}</div><div class="label">High</div></div>
      <div class="summary-card summary-medium"><div class="count">${sev.medium || 0}</div><div class="label">Medium</div></div>
      <div class="summary-card summary-low"><div class="count">${sev.low || 0}</div><div class="label">Low</div></div>
    </div>
    <div class="scan-meta">
      <span>${escapeHtml(data.repo)} (${escapeHtml(data.branch)}) — ${data.filesScanned} files scanned</span>
      ${data.scanComplete ? "" : '<span class="partial-flag">⚠ Partial scan — file limit reached</span>'}
    </div>
  `;

  if (data.findings.length === 0) {
    html += `
      <div class="no-findings">
        <div class="checkmark">✓</div>
        <div>No exposed credentials detected in the scanned files.</div>
      </div>
    `;
  } else {
    html += `<div class="section-label">Most Affected Files</div>`;
    data.summary.topFiles.forEach(f => {
      html += `
        <div class="file-row">
          <span class="filepath">${escapeHtml(f.file)}</span>
          <span class="filecount">${f.count} finding${f.count > 1 ? "s" : ""}</span>
        </div>
      `;
    });

    html += `<div class="section-label" style="margin-top:1.2rem;">All Findings</div>`;
    data.findings.forEach(f => {
      html += `
        <div class="finding-row sev-${f.severity}">
          <div style="flex:1;min-width:0;">
            <span class="finding-severity sev-${f.severity}">${f.severity}</span>
            <span class="finding-type">${escapeHtml(f.type)}</span>
            <div class="finding-location">${escapeHtml(f.file)}:${f.line}</div>
            <div class="finding-redacted">${escapeHtml(f.redacted)}</div>
          </div>
        </div>
      `;
    });
  }

  resultDiv.innerHTML = html;
}

async function scanRepo() {
  const rawInput = document.getElementById("repo-input").value;
  const resultDiv = document.getElementById("result");
  const repo = parseRepoInput(rawInput);

  if (!repo) {
    resultDiv.classList.remove("hidden");
    resultDiv.innerHTML = '<p style="color:#ff4444;">Enter a valid GitHub repo as owner/repo or a full GitHub URL.</p>';
    return;
  }

  resultDiv.classList.remove("hidden");
  resultDiv.innerHTML = "<p>Scanning " + escapeHtml(repo) + "... this can take 15-30 seconds for larger repos.</p>";

  try {
    const res = await fetch(WORKER_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo: repo })
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.message || ("Scan failed (" + res.status + ")"));
    }

    const data = await res.json();
    renderResults(data);
  } catch (err) {
    resultDiv.innerHTML = `<p style="color:#ff4444;">Request failed: ${err.message}</p>`;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("scan-btn").addEventListener("click", scanRepo);
  document.getElementById("repo-input").addEventListener("keydown", function(e) {
    if (e.key === "Enter") scanRepo();
  });
});
