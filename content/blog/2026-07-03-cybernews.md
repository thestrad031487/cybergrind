---
title: "CyberNews 2026-07-03"
date: 2026-07-03T08:00:00-05:00
description: "Daily cybersecurity headlines and practitioner commentary for July 03, 2026."
tags: ["news", "daily"]
categories: ["Daily News"]
draft: false
---

## Cybersecurity Headlines — July 03, 2026

- [Visa Lets Banks Access Its In-House Cybersecurity Capabilities](https://www.pymnts.com/cybersecurity/2026/visa-lets-banks-access-cybersecurity-capabilities/) — *pymnts.com*
- [ConsentFix and ClickFix: How Microsoft 365 Accounts are Hijacked in 3 Seconds](https://www.bleepingcomputer.com/news/security/consentfix-and-clickfix-how-microsoft-365-accounts-are-hijacked-in-3-seconds/) — *BleepingComputer*
- [US cyber agency warns over forgotten SharePoint flaw](https://www.computerweekly.com/news/366645307/US-cyber-agency-warns-over-forgotten-SharePoint-flaw) — *ComputerWeekly.com*
- [Cognizant and OpenAI bring frontier AI cyber defense from vulnerability discovery to validated fixes](https://www.prnewswire.co.uk/news-releases/cognizant-and-openai-bring-frontier-ai-cyber-defense-from-vulnerability-discovery-to-validated-fixes-302816442.html) — *PR Newswire UK*
- [Cognizant and OpenAI bring frontier AI cyber defense from vulnerability discovery to validated fixes](https://www.prnewswire.com/news-releases/cognizant-and-openai-bring-frontier-ai-cyber-defense-from-vulnerability-discovery-to-validated-fixes-302816420.html) — *PRNewswire*
- [Cisco finally confirms attackers exploiting Unified CM flaw](https://www.bleepingcomputer.com/news/security/cisco-finally-confirms-attackers-exploiting-unified-cm-flaw/) — *BleepingComputer*
- [Sysdig Details JADEPUFFER, the First Documented Agentic Ransomware Operation](https://hackread.com/sysdig-jadepuffer-first-agentic-ransomware-operation/) — *HackRead*
- [Exploring the SoC as a Service Market: Growth Potential and Key Drivers Through 2031](https://www.globenewswire.com/news-release/2026/07/02/3321169/28124/en/Exploring-the-SoC-as-a-Service-Market-Growth-Potential-and-Key-Drivers-Through-2031.html) — *GlobeNewswire*
- [Missed incidents, persistent threats, and response gaps: Insights from compromise assessment projects](https://securelist.com/compromise-assessment-findings-2025/120542/) — *Securelist.com*
- [SharePoint RCE CVE-2026-45659 Added to CISA KEV After Active Exploitation](https://thehackernews.com/2026/07/sharepoint-rce-cve-2026-45659-added-to.html) — *Internet*

---

## From the Trenches

The ConsentFix/ClickFix story is the one I'd actually sit with today — three seconds to hijack an M365 account is a workflow, not an exploit, and it's built entirely around tricking a user into consenting to something that looks legitimate. No amount of patching stops that; it's an awareness and conditional-access problem before it's a technical one.

Sysdig's JADEPUFFER writeup documenting the first confirmed agentic ransomware operation deserves attention beyond the novelty factor. An LLM-driven agent running the attack chain end to end changes the incident response calculus — the "human operator makes a mistake and tips their hand" assumption a lot of detection tuning relies on doesn't hold the same way.

And SharePoint's CVE-2026-45659 landing on CISA's KEV list after active exploitation is a good reminder that "forgotten" vulnerabilities don't stay forgotten — they just wait for someone to notice they're still unpatched somewhere.

**🔧 Patch Priority:** SharePoint RCE (CVE-2026-45659) — added to CISA's Known Exploited Vulnerabilities catalog, patch immediately if still exposed.

---

*Compiled daily. Stay patched, stay vigilant.*
