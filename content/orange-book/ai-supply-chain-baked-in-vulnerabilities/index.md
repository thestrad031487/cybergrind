---
title: "The Invisible Supply Chain, Part 2: Vulnerabilities You Can't Patch Out"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "data leakage", "credentials", "governance", "orange-book", "risk"]
description: "Part 2: when web-scraped training data includes live credentials and PII, there's no patch cycle that fixes it. The data is already baked into the weights."
---

In [Part 1]({{< ref "part1-data-provenance" >}}) we looked at how little organizations actually know about where their AI training data comes from. This time, we look at what happens once that unverified data gets baked directly into a model.

## Permanently baked-in vulnerabilities

When web scraping happens at multi-terabyte scale, sensitive information inevitably slips through. PII, medical histories, private forum posts, and even active credentials routinely end up embedded directly into a model's weights.

The scale here is worth sitting with: security researchers scanning a single monthly archive of Common Crawl discovered nearly **12,000 live, verified API keys and passwords**. Not expired test keys. Live, working credentials.

## The patching dilemma

This is where AI security breaks from the traditional vulnerability management playbook. Once a model is trained on this data, it can't be easily patched. There's no CVE, no version bump, no clean remediation path — the information is distributed across billions of parameters, not sitting in a file you can delete.

Worse, with targeted prompt engineering, attackers can sometimes coax a model into reproducing training data verbatim, surfacing exactly the kind of live credentials or private user data that got scraped in the first place.

## Regulatory tension

This "more data is better" training philosophy sits in direct conflict with data protection mandates like the EU's GDPR, which requires data minimization as a core principle. You end up with a structural mismatch: the incentives that produce a good model and the incentives that produce a compliant one are pulling in opposite directions.

## Why this matters for security teams

Traditional vulnerability management assumes remediation is possible — patch, redeploy, verify. AI models break that assumption. If your organization is fine-tuning or deploying a base model, the leakage risk in the base weights isn't something your team introduced and it isn't something your team can fix. It's inherited risk, and it needs to be treated as a permanent characteristic of the model rather than a bug to file.

**Next in this series:** how the technical choices made during training and optimization — overfitting, quantization, federated learning — introduce their own distinct security trade-offs.

---

### References

- Meli, M. et al. "How Bad Can It Git? Characterizing Secret Leakage in Public GitHub Repositories." NDSS Symposium.
- European Parliament. "General Data Protection Regulation (GDPR)." [gdpr.eu](https://gdpr.eu/)
- Carlini, N. et al. "Extracting Training Data from Large Language Models." USENIX Security Symposium.
