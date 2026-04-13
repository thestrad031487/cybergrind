---
title: "Prompt Engineering Basics"
date: 2026-04-13T08:00:00-05:00
description: "How to write effective prompts — role prompting, chain of thought, few-shot examples, and specificity techniques that get better results from any LLM."
tags: ["AI", "prompting", "fundamentals"]
weight: 2
---

## Why Prompt Engineering Matters

The same model will give you dramatically different results depending on how you phrase your request. Prompt engineering is the practice of structuring your input to get consistently useful output.

## Be Specific

Vague prompts get vague answers. Instead of "summarize this log," try "summarize this Apache access log and identify any requests that look like directory traversal attempts."

## Role Prompting

Tell the model what role to play. This sets the tone, vocabulary, and focus of the response.

**Example:**
> "You are a senior SOC analyst. Review the following alert and determine if it warrants escalation."

## Chain of Thought

Ask the model to think step by step before giving a final answer. This improves accuracy on complex tasks.

**Example:**
> "Think through this step by step before giving your final recommendation."

## Few-Shot Examples

Show the model what good output looks like by providing examples before your actual request.

**Example:**
> "Here are two examples of how I want IOCs formatted: [example 1], [example 2]. Now format these IOCs the same way: [your data]"

## Negative Constraints

Tell the model what NOT to do.

**Example:**
> "Do not include any CVEs older than 2023. Do not speculate — only include confirmed findings."

## Specify Output Format

If you need JSON, a table, or bullet points — ask for it explicitly.

**Example:**
> "Return your findings as a JSON array with fields: indicator, type, confidence, and notes."

## Iterate

Your first prompt is rarely your best. Treat prompting like debugging — refine based on the output you get.
