---
title: "CyberNews 2026-03-28"
date: 2026-03-28T08:00:00-05:00
tags: ["news", "daily"]
categories: ["Daily News"]
draft: false
---

## Cybersecurity Headlines — March 28, 2026

- [2.7M Employee Records Stolen, 100GB of Anime Fan Data Lost, and Millions of Crime Tips Leaked](https://me.pcmag.com/en/security/36218/27m-employee-records-stolen-100gb-of-anime-fan-data-lost-and-millions-of-crime-tips-leaked) — *PCMag.com*
- [2.7M Employee Records Stolen, 100GB of Anime Fan Data Lost, and Millions of Crime Tips Leaked](https://uk.pcmag.com/security/164053/27m-employee-records-stolen-100gb-of-anime-fan-data-lost-and-millions-of-crime-tips-leaked) — *PCMag.com*
- [We Are At War](https://thehackernews.com/2026/03/we-are-at-war.html) — *Internet*
- [CISA sounds alarm on Langflow RCE, Trivy supply chain compromise after rapid exploitation](https://www.helpnetsecurity.com/2026/03/27/cve-2026-33017-cve-2026-33634-exploited/) — *Help Net Security*
- [Iran Built Vast Camera Network to Control Dissent. Israel Turned it Into Targeting Tool](https://www.insurancejournal.com/news/international/2026/03/27/863731.htm) — *Insurance Journal*
- [LangChain, LangGraph Flaws Expose Files, Secrets, Databases in Widely Used AI Frameworks](https://thehackernews.com/2026/03/langchain-langgraph-flaws-expose-files.html) — *Internet*
- [Surfshark vs NordVPN: Which VPN service is better?](https://www.salon.com/2026/03/27/surfshark-vs-nordvpn-which-vpn-service-is-better/) — *Salon*
- [WEAPONS OF MASS DISTRACTION: How Cognitive and Influence Warfare Is Being Waged Against You](https://www.activistpost.com/weapons-of-mass-distraction-how-cognitive-and-influence-warfare-is-being-waged-against-you/) — *Activistpost.com*
- [With AI and quantum threats closing in on enterprises, IBM says don’t panic — but start moving](https://siliconangle.com/2026/03/26/enterprise-security-demands-dont-panic-discipline-rsac26/) — *SiliconANGLE News*
- [CISA: New Langflow flaw actively exploited to hijack AI workflows](https://www.bleepingcomputer.com/news/security/cisa-new-langflow-flaw-actively-exploited-to-hijack-ai-workflows/) — *BleepingComputer*

## From the Trenches

The CISA alert on the Langflow RCE is the story of the week. AI workflow tooling is getting adopted faster than security teams can assess it, and Langflow is widely deployed in enterprise environments that probably don't have it on their asset inventory yet. An actively exploited RCE in an AI orchestration framework is exactly the kind of blind spot that leads to a bad quarter. Hunt for it in your environment today.

The LangChain and LangGraph flaws exposing files, secrets, and databases in the same news cycle as the Langflow RCE should be a forcing function for every org that has greenlit AI framework adoption without a security review. These tools touch sensitive data by design — credentials, database connections, API keys. The attack surface is real and it's growing faster than the vendor patch cycle.

**🔧 Patch Priority:** Langflow (CVE-2026-33017) — actively exploited RCE with CISA confirmation; if it's in your environment it needs to be patched or isolated immediately.

---

*Compiled daily. Stay patched, stay vigilant.*