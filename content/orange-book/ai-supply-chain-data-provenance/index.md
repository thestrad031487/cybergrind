---
title: "The Invisible Supply Chain, Part 1: Where AI Data Actually Comes From"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "data provenance", "governance", "orange-book", "risk"]
description: "Every AI model is a product of its training data. Part 1 of a 6-part series breaks down where that data actually comes from, and why almost none of it is properly documented."
---

Every AI model is, at its core, a direct product of its training data. Long before a system answers its first prompt or makes its first real-world prediction, decisions about data collection, sourcing, and processing have already permanently shaped its behavior.

For organizations deploying AI, those upstream decisions carry security implications that rarely get examined. The risk doesn't start at deployment. It starts deep inside a data supply chain that's largely invisible, poorly documented, and almost never audited.

This is part 1 of a 6-part series on AI supply chain security. We're starting where every model starts: its data.

## The provenance problem

Training a state-of-the-art model takes a staggering volume of information, and developers pull from a mix of sources, each with a very different trust profile:

| Source | What It Is | Trust Profile & Risks |
|---|---|---|
| **Web Scraping** | Automated crawls of public internet content | **Low** — no curation, no version control, content can change post-collection |
| **Licensed Datasets** | Data purchased from commercial platforms | **Medium** — terms are often vague, original users rarely consented to AI training |
| **Synthetic Data** | AI-generated content used to train later models | **Variable** — growing fast, but risks compounding existing model biases |
| **Internal Corpora** | Company knowledge bases, support transcripts, clinical notes | **Higher** — direct organizational control, but real liability if mishandled |

Foundation models lean heavily on web archives like Common Crawl. Because these datasets are composites of hundreds of upstream sources, true data provenance — knowing exactly where data came from, when it was gathered, and whether it was altered — is basically non-existent.

The numbers back this up. An audit of over 1,800 datasets by the Data Provenance Initiative found that over 70% of licenses were listed as "Unspecified." Of the ones that were labeled, 66% were miscategorized as more permissive than they actually were.

## The AI equivalent of an SBOM

If that "Unspecified license" number sounds familiar, it should. It's the same problem the software industry had before SBOMs became standard practice.

Just as the software world adopted Software Bills of Materials after major supply chain attacks made "what's actually in this build" an unavoidable question, AI needs an equivalent: an **ML-BOM** — a documented inventory of dataset sources, licenses, privacy categories, and filtering decisions.

Adoption of anything like this is still dangerously low. Most organizations deploying AI today cannot tell you, with any confidence, where their model's data actually came from.

## Why this matters for security teams

If you're evaluating or deploying a third-party model, "where did the training data come from" is a legitimate vendor risk question — the same category as asking a SaaS vendor about their subprocessors. The difference is there's rarely a good answer available, and that gap doesn't go away just because it's inconvenient.

**Next in this series:** what actually happens when that unaudited data gets baked directly into a model's weights — including live credentials that don't get patched.

---

### References

- Longpre, S. et al. "The Data Provenance Initiative." [dataprovenance.org](https://www.dataprovenance.org/)
- CISA. "Software Bill of Materials (SBOM)." [cisa.gov/sbom](https://www.cisa.gov/sbom)
- Common Crawl Foundation. [commoncrawl.org](https://commoncrawl.org/)
