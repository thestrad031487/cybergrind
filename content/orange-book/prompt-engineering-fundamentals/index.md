---
title: "The Cost of a Bad Prompt: How Prompt Engineering Saves Real Money"
date: 2026-07-19
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["ai", "prompt engineering", "llm", "cost optimization", "governance", "orange-book"]
description: "Tokens cost money on both sides of the conversation. A vague prompt doesn't just waste your time — it inflates the bill. Here's the actual math, and the levers that bring it back down."
---

Every token an LLM API processes has a price tag, on the way in and on the way out. That fact turns "write better prompts" from a productivity tip into a line item. Most organizations treat AI spend as an unavoidable cost of doing business; in practice, a meaningful chunk of it is just badly engineered prompts paying for their own inefficiency.

## The math nobody's watching

API pricing is quoted per million tokens, split between input (what you send) and output (what the model generates), and output almost always costs more than input — commonly 4-5x. As of mid-2026, representative rates look like this:

| Provider / Model | Input ($/1M tokens) | Output ($/1M tokens) |
|---|---|---|
| OpenAI GPT-4o | $2.50 | $10.00 |
| OpenAI GPT-4o mini | $0.15 | $0.60 |
| Anthropic Claude Sonnet | $3.00 | $15.00 |
| Anthropic Claude Haiku | $1.00 | $5.00 |

Rates move often and vary by tier, so treat this as illustrative rather than a quote you can budget against — check the provider's current pricing page before committing numbers to a budget.

Here's where a bad prompt actually costs money, and it's rarely the prompt itself — prompts are usually a few hundred tokens either way. It's what a bad prompt *triggers*:

- **Rambling output.** An unconstrained prompt with no format or length guidance tends to produce a longer, hedgier answer than the task needed — and you're paying the output rate, the expensive side of the ratio, for every extra word.
- **Retries.** A vague prompt that misses the mark gets re-run, sometimes three or four times, with the user tweaking wording each time. That's the full input + output cost, repeated, for work that one well-specified prompt would have done in a single pass.
- **Wrong model for the task.** Sending a simple classification or extraction task to a flagship reasoning model instead of a lightweight one can mean paying 5-15x more per token than the task required.

## A concrete comparison

Take a task a lot of security teams actually run: summarizing a batch of vulnerability scan results for a weekly report.

**Bad prompt:**
> "Summarize these vulnerability scan results."

No length target, no format, no severity threshold. The model has no signal to stop at a reasonable length, so it tends to produce a long, narrative summary — every finding gets a paragraph whether it matters or not. If the summary misses what the analyst actually needed (say, they wanted it grouped by severity), that's a second full round-trip to fix it.

**Good prompt:**
> "Summarize these vulnerability scan results in a table: CVE ID, severity, affected asset, one-line remediation. Include only High and Critical findings. Keep the whole table under 400 tokens."

Same source data, same model, but the output is bounded and structured on the first attempt. Fewer output tokens, no retry, and the result drops straight into a report instead of needing to be reformatted by hand afterward.

Scaled across a team running this kind of summary weekly, the gap between those two prompts compounds fast — not because either prompt is expensive on its own, but because one of them is reliably a single pass and the other reliably isn't.

## Four levers that actually move the bill

**1. Cap output with `max_tokens`, deliberately.** Not as an afterthought — as part of the prompt design. If you know the task needs a paragraph, don't leave the ceiling at the model's default maximum.

**2. Route by task, not by habit.** Classification, extraction, tagging, and short factual lookups don't need a flagship reasoning model. Sending them to a smaller, cheaper model (GPT-4o mini instead of GPT-4o; Haiku instead of Sonnet) can cut cost by an order of magnitude with no meaningful quality loss on tasks that simple.

**3. Use prompt caching for repeated context.** If the same system prompt, reference document, or instruction set gets sent on every call — which is exactly how most security tooling integrations work — both major providers offer a steep discount (up to ~90%) on cached input tokens versus fresh ones. A static system prompt re-sent on every request is close to free money left on the table if caching isn't enabled.

**4. Batch what isn't time-sensitive.** Both OpenAI and Anthropic offer batch processing at roughly half the standard rate for workloads that can tolerate a delay — log analysis pipelines, overnight report generation, and similar non-interactive jobs are usually good candidates.

## Where templates fit into this

The four pillars from the fundamentals write-up (instruction, context, format, constraints) aren't just an accuracy tool — they're the thing that makes a prompt's cost predictable. A one-off prompt gets iterated on live, and every iteration is a billed round-trip. A saved, tested template with the format and constraints already baked in produces the same shape of output every time, from every team member who uses it, with no trial-and-error tax.

That's the actual argument for building a prompt template library rather than letting each person on a team re-derive their own version of "summarize this log": it's not just consistency, it's the difference between paying for the request once and paying for it every time someone reinvents it.

## The takeaway

Token pricing makes something that used to be invisible — how well someone communicates a request — into a direct cost. A prompt engineered with a clear instruction, the right context, a bounded output format, and explicit constraints isn't just more likely to get the right answer. It's the cheaper answer, on the first try, at a rate that holds up whether it's one person running one query or a team running the same request a thousand times a month.

---

### References

- OpenAI. "API Pricing." [openai.com/api/pricing](https://openai.com/api/pricing/)
- Anthropic. "Pricing." [anthropic.com/pricing](https://www.anthropic.com/pricing)
- Anthropic. "Prompt Caching." [docs.claude.com](https://docs.claude.com/)
