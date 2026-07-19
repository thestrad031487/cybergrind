---
title: "Prompt Engineering 101: The Four Pillars of Getting Good Output"
date: 2026-07-19
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "prompt engineering", "llm", "productivity", "orange-book"]
description: "Tokens, temperature, and the four pillars of a well-structured prompt — plus real examples of what separates a prompt that gets useful output from one that wastes your time and your token budget."
---

Most people talk to an LLM the way they'd talk to a search engine: type a few words, hope for the best, complain when the answer is generic. That's not a model problem. It's a prompting problem.

An LLM doesn't "know" what you want — it's a probability engine, guessing the most statistically likely next word based on patterns in its training data. Vague input gives it nothing to anchor on, so it fills the gap with the most generic, average answer it can produce. A well-structured prompt narrows that guesswork down to something useful. This post covers the mechanics behind that guesswork and the four-part structure that consistently produces better output.

## What the model actually sees

Text you type gets broken into tokens before the model ever "reads" it — chunks roughly 3-4 characters long, converted into numeric IDs the model actually operates on. Short, common words like "the" are usually a single token; longer or unusual words get split into pieces. Different model families tokenize differently (GPT-family models use byte-pair encoding; BERT-style models use WordPiece), so the same sentence can produce a different token count depending on which model you're talking to.

This matters practically for two reasons: token count drives both your **cost** and your **context window** — the model's total working memory. Exceed the context window and the model doesn't error out; it silently drops earlier content, meaning it can "forget" the start of a long conversation without telling you.

## Why the same prompt gives you a different answer twice

Ask an LLM the same question twice and you'll often get two different answers. That's nondeterminism — the model samples from a probability distribution over possible next tokens rather than always picking the single most likely one. Three parameters control how much that randomness shows up in practice:

| Parameter | What it does | Practical guidance |
|---|---|---|
| **Temperature** | Scales how "adventurous" token selection is | Low (0.0–0.3) for code, data extraction, factual analysis. Higher (0.7+) for brainstorming or creative drafts |
| **Top-p (nucleus sampling)** | Restricts sampling to the smallest set of tokens whose combined probability reaches p, cutting off the unreliable long tail | Alternative to temperature — adjust one or the other, not both |
| **Max tokens** | Caps response length | A ceiling, not a target. Too low truncates mid-thought; too high pads output (and cost) with filler |

Top-p as a decoding strategy comes out of research showing that always picking the highest-probability token (or sampling from the full distribution) produces degenerate, repetitive, or incoherent text — nucleus sampling was proposed specifically to truncate that unreliable tail while preserving useful variety.

## The four pillars of a working prompt

A prompt that reliably produces useful output usually has four components, whether or not the person writing it thinks of it that way:

1. **Instruction** — the actual task, stated with a clear verb: analyze, summarize, compare, classify.
2. **Context** — the background the model needs to interpret the task correctly: who the audience is, what data it's working from, what role it should adopt.
3. **Output format** — the shape of the answer: bullets, a table, JSON, a specific length.
4. **Constraints** — the boundaries: what to exclude, what tone to hold, what not to guess at.

Here's the difference in practice, using a task a lot of security teams actually run through an LLM:

**Bad prompt:**
> "Look at this log and tell me if anything's wrong."

No instruction beyond "look," no context about the environment, no format, no constraints. The model will produce *something* — probably a generic list of "things that could be suspicious in any log ever" — because it has nothing specific to anchor on.

**Good prompt:**
> "You are a SOC analyst reviewing authentication logs for a small business VPN. Identify any entries indicating brute-force attempts or logins from unexpected geographic regions. For each finding, output: timestamp, source IP, reason flagged, and a severity rating (low/medium/high). Do not flag single failed logins from known internal IP ranges — only patterns across multiple attempts."

Same task, four pillars filled in: instruction (identify brute-force/geo anomalies), context (SOC analyst, VPN auth logs), format (structured per-finding output), constraints (ignore isolated internal failures). The model has almost nothing left to guess.

The failure mode to watch for isn't just under-specifying — it's also over-specifying. A prompt that rambles through five loosely related requirements in one paragraph tends to make the model quietly drop or blend parts of the request. Specificity and brevity aren't in tension; the goal is removing ambiguity without burying the actual ask.

## System prompts vs. user prompts — and why the line matters

In any application built on an LLM, there are usually two layers of instruction. The **system prompt** is set by the developer, persists across the whole session, and defines the model's role and hard rules (e.g., "You are a log analysis assistant. Never execute code."). The **user prompt** is whatever the end user types, evaluated within those system-level constraints.

In theory, system instructions always win. In practice, the model doesn't see two separate channels — everything, system and user text alike, gets flattened into one sequence of tokens before the model processes it. The separation exists through formatting conventions and training, not a hard architectural wall, which means it's a probabilistic boundary rather than a guaranteed one. That gap is the foundation of prompt injection, which is worth its own dedicated write-up rather than a paragraph here — for now, the practical takeaway is: don't treat a system prompt as a security control on its own. It reduces the attack surface; it doesn't eliminate it.

## Getting the most out of it

A few habits consistently separate prompts that work from prompts that don't:

- **Give it a role.** "You are a [specific expert]" measurably narrows the model's tone and assumptions compared to no role at all.
- **Show, don't just tell, when format matters.** One or two examples of the exact output shape you want (few-shot prompting) beats a paragraph describing the format in the abstract.
- **Ask for reasoning on anything multi-step.** Adding "explain your reasoning step by step" (chain-of-thought prompting) measurably improves accuracy on tasks that require more than one logical hop — this was formally demonstrated by Google researchers in 2022 and holds up consistently on reasoning-heavy tasks.
- **Save what works.** If you're running the same kind of request repeatedly — log triage, vulnerability write-ups, incident summaries — turn the working version into a template instead of re-deriving it from scratch each time.

None of this is about tricking the model into being smarter. It's about giving a pattern-matching system an actual pattern to match.

---

### References

- Holtzman, A. et al. "The Curious Case of Neural Text Degeneration." ICLR 2020. [openreview.net/forum?id=rygGQyrFvH](https://openreview.net/forum?id=rygGQyrFvH)
- Wei, J. et al. "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." NeurIPS 2022. [arxiv.org/abs/2201.11903](https://arxiv.org/abs/2201.11903)
- OpenAI. "What are tokens and how to count them." [platform.openai.com/docs](https://platform.openai.com/docs/)
- Anthropic. "System Prompts." [docs.claude.com](https://docs.claude.com/)
