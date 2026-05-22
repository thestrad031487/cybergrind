---
title: "ShinyHunters' Salesforce Campaign: Three Rounds, 1.5 Billion Records"
date: 2026-05-22
description: "A threat intelligence breakdown of how ShinyHunters systematically targeted Salesforce environments across three distinct campaigns — vishing and OAuth abuse, the Salesloft/Drift supply chain breach, and the Experience Cloud Aura exploitation."
tags:
  - threat-intelligence
  - shinyhunters
  - salesforce
  - oauth
  - supply-chain
  - data-breach
categories:
  - Daily News
author: "Logan"
draft: false
---

ShinyHunters didn't hack Salesforce. That distinction matters. Across three separate campaigns spanning mid-2025 through early 2026, the group — tracked by security researchers as UNC6040 and UNC6395 — systematically exploited how organizations configure, connect, and authenticate into Salesforce. The platform's infrastructure was never the vulnerability. The integrations, the OAuth flows, and the guest user permissions were.

The result: an estimated 1.5 billion records exfiltrated across more than 1,000 organizations, ransom demands measured in Bitcoin, and confirmed victims including Cloudflare, Zscaler, Palo Alto Networks, Tenable, Proofpoint, and Grubhub.

This is a breakdown of the three rounds.

---

## Background: Who Is ShinyHunters

ShinyHunters is a financially motivated extortion group first observed in 2020. They are tracked under multiple aliases and researcher designations — UNC6040 and UNC6395 are Google Threat Intelligence Group designations for specific campaign clusters, though the relationship between the two (same actors, collaborators, or name-borrowers) has not been publicly confirmed.

The group operates primarily through data theft and extortion rather than ransomware encryption. Their playbook: exfiltrate data, establish proof of access, issue ransom demands with short deadlines, and — if payment is refused — leak or sell the data on BreachForums.

Their 2025-2026 Salesforce campaign represents one of the most sustained and methodical SaaS-focused attack series on record.

---

## Round 1: Vishing and the Malicious Data Loader (Mid-2025)

The first campaign combined voice phishing with OAuth Device Flow abuse — a technique that bypasses MFA entirely without exploiting any authentication vulnerability.

**How it worked:**

The attacker registered a malicious application mimicking Salesforce's legitimate Data Loader tool, configured to request broad OAuth scopes including full API access and refresh token generation. The OAuth Device Flow generates an 8-character authorization code. The attacker's Data Loader instance listens for a successful authentication tied to that code.

From there, the attack is pure social engineering. A vishing call goes out to an English-speaking employee impersonating IT support. The victim is directed to Salesforce's legitimate verification page — `salesforce.com/activate` — and instructed to enter the code. Upon login and approval, an access token is issued directly to the attacker's Data Loader instance.

No malware. No credential theft. No MFA bypass exploit. The victim authorized it.

Once the token was in hand, exfiltration proceeded in small chunks to avoid anomaly detection. Confirmed impacted organizations include Google, Cisco, Adidas, Workday, Qantas, and LVMH subsidiaries. Ransom demands reportedly ranged from 4 to 20 BTC with a 3-4 day deadline.

**MITRE ATT&CK mapping:**
- T1566 — Phishing (Vishing)
- T1528 — Steal Application Access Token
- T1530 — Data from Cloud Storage

---

## Round 2: The Salesloft/Drift Supply Chain Breach (August–September 2025)

This campaign is widely considered one of the largest SaaS supply chain breaches in history. The initial foothold wasn't a Salesforce environment at all — it was Salesloft's GitHub.

**The timeline:**

Between March and June 2025, the threat actors (tracked as UNC6395) accessed Salesloft's GitHub account. They added a guest user, established workflows, and conducted reconnaissance across Salesloft and Drift application environments. Mandiant's investigation confirmed this as ground zero.

In August, the exfiltration phase began. The attackers used TruffleHog — an open-source secret scanning tool designed to find exposed credentials in code repositories — to identify OAuth tokens belonging to Drift, a sales engagement chatbot integrated directly into Salesloft's platform.

Because Drift was connected to hundreds of corporate Salesforce environments as a trusted integration, those stolen tokens were a master key. In a single supply chain operation between August 8–18, 2025, ShinyHunters gained unauthorized access to 760 downstream Salesforce customer environments. Security teams at those organizations had no warning — Drift was a trusted, authorized integration. There was no authentication anomaly to detect.

The confirmed victim list includes cybersecurity companies Zscaler, Palo Alto Networks, Proofpoint, Cloudflare, and Tenable. The attackers focused on support case data — a rich target because cases frequently contain embedded credentials, API keys, AWS tokens, and Snowflake credentials shared during vendor support interactions.

Salesforce refused to pay the ransom. On October 13, the attackers released millions of records after the failed ransom bid.

**MITRE ATT&CK mapping:**
- T1195 — Supply Chain Compromise
- T1528 — Steal Application Access Token
- T1552 — Unsecured Credentials
- T1567 — Exfiltration Over Web Service

---

## Round 3: Experience Cloud / Aura Exploitation (March 2026)

The third campaign targeted public-facing Salesforce Experience Cloud sites running the Aura framework — specifically organizations that had left guest user permissions overly permissive.

ShinyHunters exploited the `/s/sfsites/aura` API endpoint on misconfigured Salesforce Experience Cloud instances using a weaponized version of Mandiant's open-source AuraInspector tool, which had been released in January 2026 to help administrators detect misconfigurations. The campaign had been running since September 2025 but only became public in March 2026 after Salesforce published guidance and ShinyHunters posted about it on their data leak site.

The attack required no authentication. Guest user profiles in Experience Cloud, when misconfigured, can expose object data through the Aura API. The weaponized AuraInspector automated scanning at scale — finding vulnerable endpoints across the internet and manipulating API parameters to scrape data without any credentials. Salesforce's GraphQL API initially limited queries to 2,000 records at a time, but ShinyHunters found that abusing the `sortBy` parameter bypassed this restriction. Salesforce subsequently closed that bypass.

The campaign affected an estimated 300–400 organizations. Confirmed victims include 7-Eleven and Instructure (Canvas), which confirmed ShinyHunters exploited a Salesforce Experience Cloud misconfiguration as part of the broader Canvas breach activity.

**MITRE ATT&CK mapping:**
- T1190 — Exploit Public-Facing Application
- T1078 — Valid Accounts (Guest)
- T1530 — Data from Cloud Storage

---

## Campaign Summary

| Campaign | Timeline | Method | Estimated Impact |
|---|---|---|---|
| Vishing / Data Loader | Mid-2025 | OAuth Device Flow phishing | 1,000+ orgs |
| Salesloft / Drift | Aug–Sep 2025 | Supply chain, OAuth token theft | 760 orgs |
| Experience Cloud / Aura | Sep 2025–Mar 2026 | Misconfigured guest user API | 300–400 orgs |

Total claimed exfiltration: approximately 1.5 billion records.

---

## Key Observations

**Salesforce's infrastructure was not compromised.** Every campaign exploited configuration, integration trust, or user behavior. This is not a caveat — it is the point. The attack surface for a modern SaaS platform extends far beyond the vendor's control.

**OAuth tokens are high-value targets.** In both the Data Loader campaign and the Salesloft/Drift breach, OAuth tokens were the primary objective. A valid OAuth token with broad scopes is functionally equivalent to a password — and often harder to detect in use because it generates legitimate-looking API activity.

**Supply chain integrations extend your blast radius.** The Salesloft/Drift breach didn't require compromising 760 organizations individually. One integration with one vendor was enough. Every connected app in your Salesforce org is a potential pivot point.

**Speed of exfiltration is increasing.** Unit 42 documented ShinyHunters moving from initial compromise to complete data exfiltration in under an hour across multiple incidents — faster than most organizations can begin incident response.

**Defensive tools become offensive weapons.** AuraInspector was released by Mandiant in January 2026 to help defenders find misconfigurations. ShinyHunters weaponized it within weeks. This is not unique to this campaign — it is a recurring pattern in the threat landscape.

---

## Sources

- Mitiga — *ShinyHunters and UNC6395: Inside the Salesforce and Salesloft Breaches* — https://www.mitiga.io/blog/shinyhunters-and-unc6395-inside-the-salesforce-and-salesloft-breaches
- DoControl — *Who Is ShinyHunters? Tactics, Top Attacks & How to Protect Your Organization* — https://www.docontrol.io/blog/shinyhunters
- Push Security — *How three techniques are behind ShinyHunters' 2026 campaigns* — https://pushsecurity.com/blog/analyzing-the-instructure-breach
- Salesforce Ben — *FBI Issues Salesforce Instance Warning Over 'ShinyHunters' Data Theft* — https://www.salesforceben.com/fbi-issues-salesforce-instance-warning-over-shinyhunters-data-theft/
- Salesforce Ben — *Salesforce Data Theft Roundup 2025: Everything You Need to Know* — https://www.salesforceben.com/salesforce-data-theft-roundup-everything-you-need-to-know/
- Illumio — *The Master Key Problem: Inside the Salesloft Breach and Ongoing Threat* — https://www.illumio.com/blog/the-master-key-problem-what-the-salesloft-breach-reveals-about-an-ongoing-threat
- NetSecurity — *A Full Recap of Salesforce Supply-Chain Nightmare* — https://www.netsecurity.com/a-full-recap-of-salesforce-supply-chain-nightmare-how-one-breach-impacted-700-organizations/
- Infosecurity Magazine — *Salesloft: GitHub Account Breach Was Ground Zero in Drift Campaign* — https://www.infosecurity-magazine.com/news/salesloft-github-breach-drift/
- BleepingComputer — *ShinyHunters claims ongoing Salesforce Aura data theft attacks* — https://www.bleepingcomputer.com/news/security/shinyhunters-claims-ongoing-salesforce-aura-data-theft-attacks/
- Help Net Security — *ShinyHunters claims new campaign targeting Salesforce Experience Cloud sites* — https://www.helpnetsecurity.com/2026/03/11/shinyhunters-salesforce-aura-data-breach/
- SecurityWeek — *Hundreds of Salesforce Customers Allegedly Targeted in New Data Theft Campaign* — https://www.securityweek.com/hundreds-of-salesforce-customers-allegedly-targeted-in-new-data-theft-campaign/
- Black Kite — *ShinyHunters and the Salesforce Experience Cloud Campaign* — https://blackkite.com/blog/shinyhunters-and-the-salesforce-experience-cloud-campaign-how-misconfigured-portals-create-supply-chain-risk
- Reco — *Inside the ShinyHunters Experience Cloud Campaign: IOCs, Detection Logic, and What's at Risk* — https://www.reco.ai/blog/inside-the-shinyhunters-experience-cloud-campaign-iocs-detection-logic-and-whats-at-risk
- SOFX — *ShinyHunters Breaches Canvas LMS in Second Instructure Security Incident in Eight Months* — https://www.sofx.com/shinyhunters-breaches-canvas-lms-in-second-instructure-security-incident-in-eight-months/
- Wikipedia — *Aura data breach* — https://en.wikipedia.org/wiki/Aura_data_breach

---

*CyberGrind covers the ShinyHunters Salesforce defender playbook in a separate Orange Book article. If you're a security practitioner asking what to actually do about this, that's the one to read.*
