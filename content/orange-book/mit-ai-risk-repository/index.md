---
title: "MIT AI Risk Repository: Mapping 1,700+ AI Risks"
date: 2026-03-31
tags: ["ai", "frameworks", "governance", "risk", "orange-book"]
description: "A deep dive into the MIT AI Risk Repository — its Causal and Domain taxonomies, who it's built for, and its acknowledged limitations."
---

# The MIT AI Risk Repository: Mapping the Full Landscape of AI Risks

*A deep dive into the most comprehensive academic catalog of AI risks ever assembled*

---

## What Is It?

The **MIT AI Risk Repository** is a living research database developed by MIT FutureTech. It is not a governance framework, a regulation, or a standard — it is a research tool: a comprehensive, publicly accessible catalog of over **1,700 distinct AI risks**, extracted from 74 existing frameworks, taxonomies, and academic classifications.

It was published in 2024 and is part of the broader **MIT AI Risk Initiative**, which aims to increase awareness and adoption of best practice AI risk management across the AI ecosystem.

**Citation:** Slattery, P., Saeri, A. K., Grundy, E. A. C., Graham, J., Noetel, M., Uuk, R., Dao, J., Pour, S., Casper, S., & Thompson, N. (2024). *The AI Risk Repository: A Comprehensive Meta-Review, Database, and Taxonomy of Risks from Artificial Intelligence*. https://doi.org/10.48550/arXiv.2408.12622
**Website:** [airisk.mit.edu](https://airisk.mit.edu)

---

## Why Was It Created?

Before the Repository, there was no single place to go to understand the full breadth of risks that AI poses. Dozens of individual frameworks, whitepapers, and academic papers each addressed pieces of the problem — but they used different terminology, different categories, and different levels of specificity.

The Repository was created to solve that fragmentation problem. According to the MIT team, to the best of their knowledge, it is the **first comprehensive review of AI risk frameworks and taxonomies** that extracts their risks and releases that data for further adaptation and use.

---

## How It Works

The Repository has three components:

### 1. The AI Risk Database
Links each of the 1,700+ risks to its source document (paper title, authors), supporting evidence (quotes, page numbers), and to the taxonomies below. Available freely on Google Sheets and OneDrive.

### 2. The Causal Taxonomy of AI Risks
Classifies **how, when, and why** an AI risk occurs, across three axes:

- **Entity** — Was the risk caused by an AI system, a human, or something else?
- **Intent** — Was the outcome intentional or unintentional?
- **Timing** — Did the risk occur pre-deployment (before the AI is released) or post-deployment (after it's in the wild)?

### 3. The Domain Taxonomy of AI Risks
Classifies risks into **7 domains and 24 subdomains**. These are the seven domains:

| # | Domain | Summary |
|---|---|---|
| 1 | Discrimination & Toxicity | Unfair treatment, harmful content, unequal AI performance across groups |
| 2 | Privacy & Security | Data leakage, identity exposure, AI system vulnerabilities and attacks |
| 3 | Misinformation | False outputs, filter bubbles, erosion of shared reality |
| 4 | Malicious Actors | Disinformation at scale, fraud, cyberweapons, mass harm |
| 5 | Human-Computer Interaction | Overreliance, loss of human agency and autonomy |
| 6 | Socioeconomic & Environmental | Job loss, power centralization, governance failure, environmental harm |
| 7 | AI System Safety, Failures & Limitations | Misaligned goals, dangerous capabilities, lack of transparency, multi-agent risks |

---

## Key Risks Highlighted

A few risk subdomains worth calling out specifically:

**AI pursuing its own goals in conflict with human goals or values (Domain 7.1)**
AI systems acting in conflict with human goals or values — potentially through reward hacking, goal misgeneralization, or the development of dangerous capabilities such as manipulation, deception, situational awareness, or self-proliferation.

**Lack of transparency or interpretability (Domain 7.4)**
Challenges in understanding or explaining AI decision-making processes, which can lead to mistrust, difficulty in holding actors accountable, and the inability to identify and correct errors.

**Governance failure (Domain 6.5)**
Inadequate regulatory frameworks and oversight mechanisms failing to keep pace with AI development — a meta-risk that undermines the ability to manage all other risks.

**Pollution of information ecosystem (Domain 3.2)**
Highly personalized AI-generated misinformation creating filter bubbles where individuals only see what matches their existing beliefs, undermining shared reality and weakening democratic processes.

---

## Who Should Use It?

The Repository is designed to serve multiple audiences:

- **Policymakers** — for risk assessments, shared frameworks for discussion, and monitoring emergent risks
- **Risk evaluators and auditors** — to identify previously undocumented risks and develop audit criteria
- **Academics** — as a foundation for new research, finding underexplored areas, and developing educational material
- **Industry** — to conduct internal risk assessments and develop risk mitigation strategies

---

## Honest Limitations

The MIT researchers are admirably transparent about what the Repository does *not* do well:

- It is limited to risks drawn from 65 documents (though over 17,000 records were screened)
- It may be missing emerging, domain-specific, or unpublished risks
- A single expert reviewer was used for extraction and coding, introducing potential for subjective bias
- The taxonomies prioritize clarity and simplicity over nuance
- Risks are not categorized by impact, likelihood, or interaction effects

These are not reasons to dismiss the work — they are reasons to treat it as a living document, which is exactly how the MIT team presents it.

---

## How to Access It

- **Website:** [airisk.mit.edu](https://airisk.mit.edu)
- **Full database (Google Sheets):** https://docs.google.com/spreadsheets/d/15LeHcpeuZC9txkvcaMoh3sUhkMvdMMry69xxXL46DT0/copy
- **Research paper:** https://arxiv.org/pdf/2408.12622
- **Licensed under:** CC BY 4.0

---

*Next in this series: [The NIST AI Risk Management Framework](./02_NIST_AI_RMF.md)*
