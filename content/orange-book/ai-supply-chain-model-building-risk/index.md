---
title: "The Invisible Supply Chain, Part 3: How Model-Building Choices Introduce Risk"
date: 2026-07-09
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "supply chain", "quantization", "federated learning", "overfitting", "orange-book", "risk"]
description: "Part 3: overfitting, quantization, and federated learning all introduce security trade-offs that most teams never evaluate before deployment."
---

Parts 1 and 2 of this series covered the data going into a model. This time we look at the technical choices made while training and optimizing it — decisions that introduce their own, separate set of security trade-offs.

## Overfitting and validation

During training, a model processes data over multiple epochs, or complete passes. Train it too long and it stops learning general concepts and starts memorizing the training data outright. That's overfitting, and it makes a model significantly more likely to leak sensitive details when prompted.

A held-out validation set is supposed to act as a quality gate that catches this. Skip or rush that step and you get unpredictable, volatile behavior once the model is in the real world.

## Pruning and quantization

To run efficiently on standard hardware, trained models get compressed after the fact:

- **Pruning** removes minor parameters that contribute little to predictions
- **Quantization** reduces numerical precision (e.g., 32-bit floats down to 8-bit integers)

Both save real memory and compute. But research shows quantization can silently erode safety-aligned behavior. Backdoor defenses that successfully block malicious inputs in a full-precision model often fail completely once that same model is compressed. The safety testing your team ran on the full model may simply not hold after it's quantized for production.

## Federated learning

Federated learning trains models across decentralized devices, sending only weight updates back to a central server instead of raw data. It's a genuinely good answer to privacy concerns — but it trades privacy for integrity.

In a decentralized architecture, it's very hard to detect if a rogue participant is submitting poisoned updates designed to skew the global model's behavior. There's no central dataset to audit, which is the entire point of the architecture, and also exactly what makes poisoning hard to catch.

## Why this matters for security teams

None of these are exotic edge cases — they're standard, widely-used techniques. If a vendor tells you their model has been red-teamed and safety-tested, the follow-up question is: tested before or after quantization? Before or after any federated training rounds? The answer changes what that testing actually proves.

**Next in this series:** the "inheritance tax" of fine-tuning — why building on someone else's base model means inheriting all of the above, whether you know it or not.

---

### References

- Kumar, A. et al. "Quantization and Safety Alignment in Large Language Models." arXiv preprint.
- McMahan, B. et al. "Communication-Efficient Learning of Deep Networks from Decentralized Data." AISTATS.
- Bagdasaryan, E. et al. "How To Backdoor Federated Learning." AISTATS.
