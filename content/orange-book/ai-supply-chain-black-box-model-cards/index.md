---
title: "The Invisible Supply Chain, Part 5: Navigating the Black Box with Model Cards"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "model cards", "transparency", "governance", "orange-book", "risk"]
description: "Part 5: model weights are billions of opaque numbers with no human-readable record of why decisions get made. Model cards are the industry's answer, and they're mostly voluntary."
---

The first four parts of this series covered where AI training data comes from, what gets permanently baked into a model, how training and optimization choices introduce risk, and how fine-tuning inherits all of it. This part covers a harder problem: you often can't check any of it yourself.

## Unlike software, you can't just read it

Traditional software binaries can be disassembled and reverse-engineered. A trained model's weights are just billions of opaque floating-point numbers. There's no human-readable record of why the model makes the decisions it makes.

Red-teaming a model can sample its behaviors under specific conditions, but sampling isn't auditing. You can find that a model does something concerning under certain prompts; you can't use red-teaming alone to prove it won't do something concerning under prompts nobody thought to try.

## The nutritional label approach

To bridge that gap, the industry leans on **model cards** — voluntary, structured documentation meant to work like a nutritional label for AI:

```
       ┌────────────────────────────────────────┐
       │               MODEL CARD               │
       ├────────────────────────────────────────┤
       │ 1. Training Data & Filtering Gaps       │
       │ 2. Intended Use Cases                   │
       │ 3. Evaluation & Performance Metrics     │
       │ 4. Known Limitations & Biases           │
       │ 5. Legal Licensing & Permissions        │
       └────────────────────────────────────────┘
```

## Where this breaks down

Model cards are frequently incomplete, vague, or missing entirely. They aren't legally mandated in most jurisdictions, so developers have little incentive to thoroughly document limitations that might discourage adoption. The document that's supposed to be your primary transparency mechanism is written by the same organization that benefits from you not looking too closely.

## Why this matters for security teams

When you're evaluating a model for deployment, the model card is often the only artifact you'll get that even attempts to answer the questions this whole series has raised — data provenance, known limitations, evaluation methodology. Treat a thin or absent model card the same way you'd treat a vendor that won't answer a security questionnaire: as a data point, not an oversight to politely work around.

**Next in this series:** pulling all five parts together into a practical checklist for evaluating AI supply chain risk.

---

### References

- Mitchell, M. et al. "Model Cards for Model Reporting." FAT* Conference (ACM).
- Hugging Face. "Model Cards Documentation." [huggingface.co/docs/hub/model-cards](https://huggingface.co/docs/hub/model-cards)
- NIST. "AI Risk Management Framework (AI RMF 1.0)." [nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework)
