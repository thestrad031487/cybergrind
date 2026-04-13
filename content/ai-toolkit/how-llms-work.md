---
title: "How Large Language Models Work"
date: 2026-04-13T08:00:00-05:00
description: "A plain-English breakdown of tokenization, context windows, temperature, and hallucination — what every practitioner should know before using AI tools."
tags: ["AI", "LLM", "fundamentals"]
weight: 1
---

## What Is a Large Language Model?

A Large Language Model (LLM) is a type of AI trained on massive amounts of text data to predict the next most likely token in a sequence. That simple mechanic — predict the next token — is the foundation of everything from ChatGPT to Claude to Llama.

## Tokenization

LLMs don't read words — they read tokens. A token is roughly 3-4 characters on average. The word "cybersecurity" might be split into two or three tokens. This matters because:

- Model limits are measured in tokens, not words
- Unusual words, code, and non-English text use more tokens
- Billing on API calls is per token

## Context Windows

The context window is how much text the model can "see" at once — both your input and its output combined. Once you exceed the context window, earlier content gets dropped. For security work this matters when feeding in large log files, lengthy reports, or long conversations.

## Temperature

Temperature controls how "creative" or "random" the model's output is. A temperature of 0 means the model always picks the most likely next token — deterministic and consistent. Higher temperatures introduce more variation. For structured tasks like parsing IOCs or writing scripts, use low temperature. For brainstorming or writing, higher is fine.

## Hallucination

LLMs generate plausible-sounding text — they don't look things up. When a model states a CVE number, a tool flag, or a statistic confidently, it may be fabricating it. This is called hallucination. In security contexts, always verify:

- CVE details against NVD
- Tool syntax against official docs
- Statistics against primary sources

## What This Means for Security Practitioners

Understanding these fundamentals helps you use AI tools more effectively and spot their failure modes before they cause problems in your workflow.
