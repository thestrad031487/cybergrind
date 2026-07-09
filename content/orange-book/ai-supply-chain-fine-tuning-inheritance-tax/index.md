---
title: "The Invisible Supply Chain, Part 4: The Fine-Tuning Inheritance Tax"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "fine-tuning", "prompt injection", "governance", "orange-book", "risk"]
description: "Part 4: fine-tuning doesn't sanitize a base model. It inherits everything underneath it, plus a few new problems of its own."
---

So far this series has covered the data going into a model and the technical choices made while training it. Now: what happens when your organization doesn't build a model at all, but fine-tunes someone else's.

## Why everyone fine-tunes

Building a foundation model from scratch costs millions of dollars, so the dominant industry pattern is to take a pre-trained base model and fine-tune it on smaller, task-specific data. This is efficient, and it's also how the vast majority of deployed AI actually gets built.

The catch: fine-tuning only modifies task-specific behaviors. It does not sanitize or erase the base weights. When an organization adopts a fine-tuned model, they inherit the entire unverified baseline underneath it — everything covered in Parts 1 through 3 of this series, whether they know it or not.

That inheritance shows up as three distinct risks.

## 1. Safety alignment erosion

Studies show a model's safety guardrails can be systematically compromised by fine-tuning on as few as **10 adversarially crafted examples**. Ten. Even entirely benign, legitimate fine-tuning can gradually obscure the model's original safe pathways as a side effect, with no adversarial intent required at all.

## 2. Expanded attack surface

Fine-tuned models narrow their focus, and that narrowing makes them measurably more susceptible to prompt injection. A model specialized for financial reasoning becomes intensely responsive to an attacker who frames a malicious prompt in financial terms — the specialization that makes it useful also makes it more exploitable within that domain.

## 3. Untracked checkpoints

Fine-tuning targets a specific snapshot of a base model. If that snapshot is later found to contain a backdoor, every downstream derivative inherits the vulnerability — often without the deploying organization ever knowing which checkpoint they built on.

## Why this matters for security teams

"We fine-tuned it ourselves" is not the same claim as "we built it securely." If your team's threat model for an AI deployment stops at the fine-tuning data, it's missing the majority of the attack surface. The base model — its training data, its optimization history, its checkpoint lineage — is still your risk, even though your team never touched it directly.

**Next in this series:** why you can't just read a model's weights to check any of this, and what model cards do (and mostly don't) do about it.

---

### References

- Qi, X. et al. "Fine-tuning Aligned Language Models Compromises Safety, Even When Users Do Not Intend To." ICLR.
- Greshake, K. et al. "Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection." AISec.
- Hugging Face. "Model Versioning and Checkpoints." [huggingface.co/docs](https://huggingface.co/docs)
