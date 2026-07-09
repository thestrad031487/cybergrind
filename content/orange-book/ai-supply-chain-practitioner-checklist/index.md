---
title: "The Invisible Supply Chain, Part 6: A Practitioner's Checklist"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "checklist", "governance", "risk management", "orange-book"]
description: "Wrapping up the AI supply chain security series with a practical checklist for evaluating data provenance, training risk, fine-tuning inheritance, and model card quality before deployment."
---

This series started with a simple idea: every AI model is a direct product of its training data, and most organizations deploying AI have no real visibility into what that data actually was. Over five parts, we traced that problem from raw data collection all the way through to the documentation that's supposed to make it transparent.

Here's the full arc, and a checklist you can actually use.

## The series so far

1. **[Data Provenance]({{< ref "part1-data-provenance" >}})** — Most training data has unspecified or misclassified licensing. There's no AI equivalent of an SBOM in widespread use yet.
2. **[Baked-In Vulnerabilities]({{< ref "part2-baked-in-vulnerabilities" >}})** — Live credentials and PII get scraped into training data and can't be patched out once the model is trained.
3. **[Model-Building Risk]({{< ref "part3-model-building-risk" >}})** — Overfitting, quantization, and federated learning each introduce distinct, under-evaluated security trade-offs.
4. **[The Fine-Tuning Inheritance Tax]({{< ref "part4-fine-tuning-inheritance-tax" >}})** — Fine-tuning doesn't sanitize a base model. You inherit everything underneath it, including undiscovered backdoors.
5. **[Black Box & Model Cards]({{< ref "part5-black-box-model-cards" >}})** — You can't read model weights the way you'd read source code, and model cards are voluntary, uneven, and often thin.

## A practical evaluation checklist

Before adopting or deploying a third-party model, it's worth walking through:

- [ ] **Provenance** — Does the vendor document dataset sources and licensing, or is it "proprietary training data" with no further detail?
- [ ] **Leakage exposure** — Has the model been tested for verbatim memorization of sensitive or licensed content?
- [ ] **Compression testing** — Was safety evaluation done before or after quantization/pruning? Ask specifically.
- [ ] **Fine-tuning lineage** — If this is a fine-tuned model, what base model and checkpoint is it built on, and is that checkpoint's history documented?
- [ ] **Model card completeness** — Does it cover training data, intended use, evaluation metrics, known limitations, and licensing? Or is it a paragraph and a disclaimer?
- [ ] **Update path** — If a vulnerability is found in the base model post-deployment, what's the actual remediation path? (Often: none. Plan accordingly.)

## The core takeaway

None of this is about refusing to use AI. It's about recognizing that AI supply chain risk doesn't behave like traditional software supply chain risk — there's no patch Tuesday for a model's training data, and "we'll fix it in the next release" doesn't apply to something baked into billions of parameters.

Treat vendor AI evaluation the way you'd treat any other third-party risk assessment: ask the uncomfortable questions up front, document what you don't get answers to, and build your deployment decisions around the gaps rather than assuming they don't exist.

---

### References

- NIST. "AI Risk Management Framework (AI RMF 1.0)." [nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework)
- Data Provenance Initiative. [dataprovenance.org](https://www.dataprovenance.org/)
- Mitchell, M. et al. "Model Cards for Model Reporting." FAT* Conference (ACM).
