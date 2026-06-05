---
title: "2026 Verizon DBIR: What the Data Actually Means for Defenders"
date: 2026-06-05
description: "A practitioner's breakdown of the 2026 Verizon Data Breach Investigations Report — covering the year's biggest shifts in vulnerability exploitation, ransomware, third-party risk, GenAI in the attack chain, and what to do about all of it."
tags: ["threat intelligence", "vulnerability management", "ransomware", "social engineering", "GRC", "DBIR"]
categories: ["Orange Book"]
author: "Logan"
showToc: true
TocOpen: false
draft: false
cover:
  hidden: true
---

Every year, Verizon publishes the Data Breach Investigations Report, and every year the security community either over-indexes on a single headline or buries the thing in a drawer. The 2026 edition — the 19th — deserves neither treatment. Based on **31,000+ incidents and 22,000+ confirmed breaches across 145 countries**, this is the largest dataset the DBIR has ever analyzed, and the findings have real operational implications for defenders at every level.

This isn't a summary. It's a breakdown of what changed, why it matters, and what you should actually do about it.

---

## The Big Shift: Vulnerabilities Overtake Credentials as the #1 Entry Point

For years, stolen credentials held the top spot as the most common initial access vector. That era is over.

In the 2026 dataset, **exploitation of vulnerabilities reached 31% of initial access vectors** — a 55% jump from 20% last year. Credential abuse fell to 13%, partly because pretexting was added as a tracked vector (pulling some overlap), but even normalized to prior methodology it sat at 16%. The trend is unambiguous.

### Why Patch Management Is Failing

The report tracked remediation of CISA KEV vulnerabilities across 13,000+ organizations. The results are worse than last year on every metric:

| Metric | 2025 (last year's DBIR) | 2026 (this year) |
|---|---|---|
| Full remediation rate | 38% | 26% |
| Median days to full patch | 32 days | 43 days |
| Median KEV CVEs per org | 11 | 16 |

The volume problem is real. The number of KEV vulnerabilities organizations had to patch rose ~50% year over year, and there appears to be a structural ceiling — even top-performing organizations can only remediate 30–40% of KEV instances in the first week after detection, regardless of process maturity or tooling investment.

### Recency Matters More Than Age

One of the more actionable findings comes from a four-year survival analysis of exploitation activity. The data shows a consistent decay curve: **the longer it's been since a vulnerability was last exploited in the wild, the less likely it is to be exploited again soon.** The probability roughly halves at 30 days, halves again at 90 days, and by a year is approximately the same as a vulnerability that was never actively exploited.

The practical implication: when you're forced to triage, a recently-exploited vulnerability not yet on the KEV is often a better patch target than an old KEV entry with no recent wild exploitation. Prioritize based on current exploitation activity, not just catalog membership.

### What to Do

- Treat the CISA KEV as a floor, not a ceiling. Enrich your patching queue with active exploitation intelligence.
- Minimize your internet-facing footprint. AI-assisted vulnerability discovery is accelerating — expect coordinated disclosure of bulk vulnerabilities to become more common.
- Track KEV remediation rates as an operational metric, not just a compliance checkbox.
- Inventory and aggressively patch internet-facing network edge devices. EOL cellular routers in OT/utilities environments are being repurposed as operational relay boxes for threat actor campaigns at scale.

---

## Ransomware: Bigger, But Getting Cheaper to Resist

**Ransomware appeared in 48% of all breaches**, up from 44%. It was present in 77% of System Intrusion pattern breaches, and System Intrusion itself now accounts for 60% of all breaches. The Ransoming Twenties are fully in effect.

But there's meaningful signal in the payment data:

- **69% of ransomware victims did not pay** (up from 65% the prior year)
- Median ransom paid: **$139,875**, down from $150,000
- The decline persisted even with a much larger, more representative data sample this year — which strengthens confidence that it's a real trend

The DBIR's analysis frames this as a market under margin compression. Ransomware-as-a-Service commoditization, combined with improved defensive posture and greater victim resilience, is squeezing threat actor revenue. That said, threat actors are responding by maximizing business disruption rather than just encrypting data — the goal being to create time pressure that forces payment. The Marks & Spencer ransomware incident in April 2025, which disrupted online sales, stock tracking, and refrigeration monitoring for weeks at an estimated £300 million in losses, is cited as an example of what operational disruption looks like at scale.

### The Infostealer-to-Ransomware Pipeline

**50% of ransomware victims had a credential or infostealer leak event within 95 days** before falling victim. This is not coincidence — it's pipeline. Ransomware operators increasingly outsource initial access to Initial Access Brokers (IABs) who buy compromised credentials from infostealer campaigns and sell access.

IAB pricing from the dataset:
- Standard user account: ~$700 median
- Administrative account: ~$1,300 median

VPN credentials accounted for 44% of IAB-listed access types, followed by RDP and web application access. ProxyShell/ProxyLogon access was still being actively sold 2–3 years after disclosure — a direct reflection of incomplete patching.

### The RMM Shift

Threat actors are swapping traditional C2 frameworks (Cobalt Strike, custom backdoors) for **legitimate Remote Monitoring and Management (RMM) software**. Usage of RMM tools in System Intrusion breaches increased 240% year over year, while Backdoor/C2 actions dropped 27%. The reason is simple: RMM tools are already in the organization's application whitelist, they don't require additional infrastructure, and they blend into normal administrative activity.

This is particularly relevant for defenders because detection logic built around known C2 tooling won't catch it. Behavioral detection on RMM usage anomalies — unusual hours, unusual endpoints, unusual privilege scope — is the right countermeasure.

### What to Do

- Monitor your organization's infostealer exposure. Services that track credential leaks tied to your domain provide meaningful early warning of the pipeline in action.
- Enforce MFA everywhere, especially for VPN and remote access. IABs sell VPN credentials more than anything else.
- Harden your RMM posture: restrict which endpoints can run RMM agents, alert on new RMM software installations, and audit the scope of existing RMM deployments.
- Maintain offline, immutable backups. The CIS Controls framework's Data Recovery section (CIS Control 11) covers the essentials: documented recovery process, automated backups, isolated recovery data.

---

## Third-Party Risk: 48% of Breaches, Up 60% in One Year

Third-party involvement in breaches has **doubled two years in a row**. It went from roughly 15% to 30% last year, and now sits at 48%. At this trajectory, it's approaching parity with direct-to-organization breaches.

The DBIR categorizes third-party breach archetypes into three types:

1. **Vendor in your software supply chain** — vulnerability in vendor product or backdoored software (SolarWinds-style)
2. **Vendor hosting your data** — attacker breaches the vendor environment where your data lives (Snowflake-style credential campaigns)
3. **Vendor with network/credential access to your environment** — attacker moves laterally from compromised vendor into your org (Target 2013-style)

The 2025 Salesforce/Salesloft Drift campaign is cited as an example of archetypes 2 and 3 chaining: OAuth tokens from a Salesforce plugin were compromised, then used to exfiltrate customer data from the Salesforce platform. Victim organizations had limited ability to prevent it — the exposure was in the vendor layer.

### The Cloud Configuration Problem

A new dataset this year provided visibility *inside* third-party cloud environments (not just external scans). The findings:

- **31%** full remediation rate for weak password and excessive permission exposures — and the median time to fix 50% of these findings was **nearly 8 months**
- **23%** of third parties fully remediated missing or improperly configured MFA on cloud accounts
- **37%** of organizations had an admin account with MFA disabled on an IaaS offering
- Only **14%** of organizations had a Snowflake admin account with MFA disabled — evidence that high-profile breach campaigns do change behavior

Excessive privileges in cloud environments — IaaS, PaaS, SaaS — remain pervasive. The report is direct: authentication and authorization fundamentals that have been understood for decades still aren't consistently applied. This is especially important for **service and machine accounts**, which are often over-permissioned and under-monitored, and will become increasingly critical as agentic AI workflows grow.

### What to Do

- Build third-party risk questions around authentication posture: Is MFA enforced on all externally-exposed admin accounts? What is the credential rotation policy for service accounts?
- Add supply chain review to your vendor onboarding: ask how vendors handle CVE patching in products you run, and what their SLA is for KEV-level vulnerabilities.
- Implement least-privilege enforcement for third-party integrations, especially OAuth tokens and API keys. Scope them to the minimum required permissions and rotate them on a defined schedule.
- In cloud environments, treat your slice of the shared responsibility model seriously. If your IaaS provider doesn't mandate MFA for admin accounts, you need to.

---

## GenAI in the Attack Chain: Operational Acceleration, Not Novel Techniques

The DBIR collaborated with Anthropic to analyze 793 threat actors who violated Claude's acceptable use policy between March 2025 and February 2026. Their activity was classified against the MITRE ATT&CK framework.

Key findings:

- The **median actor researched AI assistance across 15 distinct ATT&CK techniques**; extreme cases covered 40–50 techniques across multi-session attack chains
- **44% of AI-assisted initial access techniques** were phishing-related, followed by exploitation of vulnerabilities at 32%
- **Less than 2.5%** of AI-assisted malware observations involved rare techniques with one or fewer known examples — the vast majority involve well-documented, already-detectable methods
- The median existing malware example count for AI-assisted techniques was **55** — meaning actors are mostly automating techniques defenders already have detection logic for

The headline conclusion: **AI is currently an operational accelerant, not a novel attack surface creator.** It's lowering the barrier for less-sophisticated actors to execute known techniques more efficiently. Your detection posture doesn't need to be rebuilt — but it needs to keep pace with faster, more adaptive execution.

The exception worth watching: AI-assisted vulnerability discovery. Early 2026 indicators suggest this is advancing rapidly. Expect coordinated disclosure of larger-than-usual CVE batches as AI-assisted static analysis scales.

### Shadow AI as an Insider Threat

Separate from attacker use of AI, the DBIR's DLP dataset surfaces a growing insider risk:

- **67%** of users access AI services via non-corporate accounts on corporate devices
- **45%** of employees are now regular AI users on corporate devices (up from 15% the prior year)
- Shadow AI is the **third most common non-malicious insider action** in DLP data, a fourfold increase in percentage
- The most common data type submitted to unauthorized AI: **source code**, followed by images and structured data
- **3.2%** of DLP violations involved research and technical documentation — direct intellectual property exposure risk

### What to Do

- Your existing detection coverage for known ATT&CK techniques is likely still valid. Focus on ensuring it's current and well-tuned, not on building entirely new categories.
- Develop a GenAI acceptable use policy that distinguishes between authorized AI tools and personal accounts. The data shows the "personal account on corporate device" behavior is dominant.
- Deploy DLP controls that can identify source code, technical documentation, and proprietary data being submitted to external AI endpoints.
- Monitor for AI-assisted phishing indicators: well-crafted English from threat actors historically limited by language proficiency is an emerging signal worth tracking.

---

## Social Engineering: The Phone Is Now More Dangerous Than Email

Social Engineering was the third most common breach pattern at 16% of breaches. The human element appeared in **62%** of all breaches (up from 60%).

The most significant finding is about attack vector effectiveness. In phishing simulation data:

- Email phishing: **1.4% median click rate**
- Phone-centric vectors (voice, SMS): **~2% median click rate** — a **40% higher success rate**

41% of Social Engineering breaches involved social vectors beyond email. About a quarter of social action vectors came from social media or phones.

**Pretexting** — synchronous social manipulation via voice or text, where the attacker builds a trusted relationship in real time — is growing as an initial access vector to ransomware and extortion attacks. It's fundamentally different from phishing in that it requires a human on the other end actively deceiving the victim. Security awareness training built around "check if the email looks suspicious" doesn't address it.

The **ClickFix** attack pattern is also worth flagging: malicious webpages presenting themselves as CAPTCHA challenges or software fix prompts that instruct users to run PowerShell or terminal commands to "resolve an issue." No malicious attachment, no suspicious link — just a social prompt that results in the user executing attacker-controlled code themselves.

### What to Do

- Expand your security awareness training to explicitly cover voice and SMS-based attacks. Phishing simulations are well-established; vishing and smishing simulations are not — and the data says they should be.
- Train help desk and IT support staff specifically on pretexting scenarios. The attacker impersonating a user who needs a password reset, or impersonating IT who needs to "troubleshoot" by accessing a desktop, are the exact scenarios appearing in the breach data.
- Establish out-of-band verification procedures for any request that involves credential changes, access grants, or wire transfers — especially when initiated via phone or messaging platforms like Microsoft Teams.
- Ensure mobile devices used for work (personal or corporate) are enrolled in MDM. The report notes that SMS phishing detections were only visible on managed devices — unmanaged personal phones are a blind spot.

---

## Industry Snapshot

| Industry | Top Risk | Notable |
|---|---|---|
| **Education** | System Intrusion (52% of breaches) | Exploit vuln is top initial access vector (34%); ransomware in 65% of malware cases |
| **Healthcare** | System Intrusion + Social Engineering | Human element and credential abuse prominent |
| **Financial** | Credential abuse, BEC, web app attacks | High incident volume; 14% Snowflake MFA fix rate post-breach shows accountability |
| **Manufacturing** | System Intrusion dominant | Ransomware-heavy; supply chain exposure growing |
| **Public Administration** | System Intrusion | State-affiliated actors more prominent; Espionage motivation higher than most sectors |
| **Utilities** | Espionage is top motive (71%) | Secrets data most commonly compromised; EOL OT/IoT device exposure significant |
| **Retail** | System Intrusion + Social Engineering | Financial motivation dominant; personal data frequently targeted |

---

## North Korean IT Workers: A Hiring Problem, Not Just a Hacking Problem

The 2026 DBIR includes a dedicated deep-dive on DPRK-affiliated IT Workers (ITWs) — operatives who infiltrate organizations as remote employees using stolen identities.

The scale is larger than most organizations realize. The analysis estimates approximately **15,000 stolen identities** in active use, with each ITW operating 3–5 identities simultaneously. Historically concentrated in blockchain/Web3 and frontend engineering roles, ITWs are expanding into HR, marketing, and AI-focused job categories — following the market for high-paying remote positions.

The risk isn't just that you've hired someone with falsified credentials. It's that these employees, once inside, have legitimate access to internal systems and may be exfiltrating data, conducting reconnaissance, or setting up persistence for future operations — all while appearing to be a normally performing employee.

Mitigation is fundamentally a hiring process and insider threat problem:

- Enhanced identity verification at multiple stages of hiring, not just background check providers
- HR and recruitment staff need awareness of this threat category specifically
- Insider threat programs should include this scenario in scope
- Be alert to employees who resist video calls, refuse to appear on camera, have unusual working hours relative to their stated location, or consistently route work through remote desktop tools on their assigned systems

---

## The Underlying Message: Fundamentals at Scale

The 2026 DBIR's overarching theme is deliberate: the threat landscape is accelerating, but the mitigations aren't new. The organizations getting breached aren't failing at cutting-edge defensive techniques — they're failing at patching, MFA, credential hygiene, and third-party visibility.

The vulnerability exploitation surge doesn't call for new tools. It calls for better execution of vulnerability management. The third-party breach explosion doesn't require a new framework. It requires actually enforcing authentication standards on vendor accounts. GenAI in the attack chain isn't breaking detection — it's accelerating execution of known techniques that existing detection logic should already cover.

The security poverty line is real. But the data says even organizations with significant resources are falling short on basics. The gap between knowing what to do and consistently doing it at scale is where most breaches live.

---

## Quick Reference: Defensive Priorities by Finding

| Finding | Priority Action |
|---|---|
| Vulns #1 initial access vector | Enrich KEV patching with active exploitation intel; minimize internet-facing footprint |
| 43-day median patch time | Track KEV remediation rate as an operational KPI |
| Ransomware in 48% of breaches | MFA on all remote access; offline immutable backups; RMM behavioral monitoring |
| Infostealer pipeline | Monitor credential leak exposure on your domain; enforce MFA on VPN |
| Third-party breaches up 60% | Vendor auth audits; scope and rotate OAuth tokens/API keys; cloud admin MFA |
| 8-month permission fix time | Least-privilege reviews; service account auditing |
| GenAI-assisted attacks | Tune existing ATT&CK coverage; deploy DLP for AI endpoints; update AUP |
| Shadow AI | DLP controls for source code/docs; authorized AI tools with corporate accounts |
| Mobile social engineering | Vishing/smishing simulation; MDM for work-use devices; out-of-band verification |
| RMM abuse up 240% | Inventory RMM tools; alert on new installs; behavioral anomaly detection |
| North Korean ITWs | Multi-stage identity verification; insider threat program scope update |

---

*Source: Verizon 2026 Data Breach Investigations Report. Dataset covers November 2024 through October 2025.*
