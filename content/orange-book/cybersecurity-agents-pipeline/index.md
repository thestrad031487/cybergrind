---
title: "Building Cybersecurity Agents with OpenClaw and Ollama: A Multi-Agent Security Pipeline"
date: 2026-04-15
description: "How to move beyond local AI chat and build a multi-agent security pipeline that generates structured threat reports on demand — with Slack integration and no cloud dependencies."
tags: ["homelab", "AI", "ollama", "agents", "slack", "docker", "cybersecurity", "llm"]
categories: ["orange-book"]
draft: false
---

If you've followed the [Self-Hosted AI Stack walkthrough](/orange-book/self-hosted-ai-stack/), you've got Ollama running locally, OpenClaw as your agent UI, and the whole thing locked down behind Tailscale. That's a solid foundation. But a chat interface, however useful, isn't the ceiling of what this stack can do.

This article is about the next step: building a multi-agent security pipeline that takes a topic — say, "Docker container hardening" or "lateral movement detection" — and returns a structured security report with identified risks, severity ratings, mitigations, and recommendations. The whole thing runs locally, costs nothing per query, and is triggered from Slack.

---

## Part 1 — Why Multi-Agent Instead of a Single Prompt

The obvious approach to "generate a security report" is a single prompt: feed the topic to the model, ask for a report, get output. It works, up to a point. The problem is that you're asking one model pass to do everything simultaneously — understand the topic, identify risks, assess severity, think through mitigations, and write coherently. That's a lot of competing demands on a single context window, and the output tends to be shallow across all dimensions.

Multi-agent pipelines solve this by decomposition. Instead of one model doing everything, you chain specialized agents where each one does a single job well and passes its output to the next. The planner doesn't worry about writing. The writer doesn't have to think about risk severity. Each agent operates in a focused context with a clear objective.

For security work specifically, this matters. A risk analyst agent can be prompted to think like a threat modeler — to ask "what could go wrong and how bad is it" — without simultaneously worrying about how to structure an executive summary. The quality of the risk identification improves when that's all the agent is doing.

The tradeoff is latency. A 5-agent pipeline takes longer than a single prompt. For an on-demand report that someone will read and act on, that's an acceptable tradeoff. For a conversational Slack response, it isn't — which is why the pipeline and the chat interface use different approaches, as we'll get to in Part 4.

---

## Part 2 — Pipeline Architecture

The pipeline runs five agents sequentially. Each agent receives the output of the previous one as part of its context, building toward a complete report.

```
Topic Input
    ↓
[1] Planner       → breaks topic into structured sections
    ↓
[2] Researcher    → summarizes best practices and known vulnerabilities
    ↓
[3] Risk Analyst  → identifies threats with impact/likelihood ratings
    ↓
[4] Mitigation    → converts risks into defensive strategies
    ↓
[5] Writer        → assembles final structured report
    ↓
Report Output (Slack + saved to disk)
```

The pipeline lives in `security-agents/workflows/security_pipeline.py`. Each agent is a class in `security-agents/agents/`, inheriting from a shared `base.py`. All LLM calls go to Ollama via `tools/llm.py`.

Context passing is straightforward — each agent's output becomes part of the next agent's input. The Writer agent receives the full accumulated context from all previous agents and assembles it into the final report structure.

---

## Part 3 — Building the Agents

### The Base Agent

Every agent inherits from a shared base class that handles the Ollama API call. Keeping this in one place means prompt structure, model selection, and error handling are consistent across all agents:

```python
class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")

    def run(self, user_input: str) -> str:
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json={
                "model": "llama3.2:3b",
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False
            }
        )
        return response.json()["message"]["content"]
```

Each agent instantiates this with its own name and system prompt. The `run()` method is what the pipeline calls at each step.

### The Risk Analyst Agent

This is the most interesting agent from a security perspective, so it's worth walking through in detail. The Risk Analyst receives the Researcher's output and is tasked with one thing: identify what can go wrong, how bad it would be, and how likely it is.

The system prompt is where the security context lives:

```python
RISK_ANALYST_PROMPT = """
You are a cybersecurity risk analyst with expertise in threat modeling and
vulnerability assessment. Your job is to analyze security topics and identify
specific risks with the following structure for each:

- Risk name
- Impact: High / Medium / Low
- Likelihood: High / Medium / Low
- Brief description of the threat vector

Focus on realistic, actionable risks. Avoid generic statements.
Prioritize risks by impact first, then likelihood.
You are contributing to a multi-part security report — output only your
risk analysis section, clearly formatted.
"""
```

A few things worth noting about this prompt design:

- **Single responsibility.** The agent is told explicitly what it's contributing to and told not to go beyond that scope. "Output only your risk analysis section" prevents the model from trying to write conclusions or recommendations — that's the Writer's job.
- **Structured output format.** Specifying impact/likelihood as High/Medium/Low makes the output consistent and parseable. Free-form severity descriptions would make the Writer's job harder.
- **Realistic and actionable.** This instruction nudges the model away from vague outputs like "unauthorized access may occur" toward specific threat vectors.

### The Pipeline Orchestrator

The orchestrator in `security_pipeline.py` is what chains the agents together and manages context passing:

```python
def run_pipeline(topic: str) -> str:
    context = topic

    for agent in [planner, researcher, risk_analyst, mitigation, writer]:
        output = agent.run(context)
        context = f"{context}\n\n{agent.name} output:\n{output}"

    return output  # Writer's final output is the report
```

This is intentionally simple. Each agent appends its output to the running context string, so by the time the Writer runs it has the full chain of reasoning to work from. The Writer's output is the final report.

---

## Part 4 — Slack Integration

### Why Slack as the Interface

The web UI is useful for exploratory work, but Slack is where security workflows actually live for most teams. Being able to trigger a report with `@CyberClaw run report docker volume hardening` from a channel — and get the output back in the same channel — means the tool fits into existing workflows rather than requiring a context switch.

### Socket Mode vs. Event Subscriptions

Slack offers two ways to receive events: a webhook-based Event Subscriptions model (Slack POSTs to a public URL you provide) and Socket Mode (your bot maintains a persistent WebSocket connection to Slack's servers). For a homelab behind Tailscale with no public-facing URL, Socket Mode is the only practical option — there's no URL to give Slack for webhooks.

Socket Mode also has a secondary advantage: no need to manage incoming webhook security, TLS termination, or ingress rules. The bot initiates the connection outbound, which fits cleanly with the Zero Trust networking model.

### Bot Command Structure

The bot listens for `@CyberClaw` mentions and routes based on the message content:

```python
if "run report" in message or "run security report" in message:
    topic = extract_topic(message)
    subprocess.Popen(["python3", "main.py", topic])
    slack_client.chat_postMessage(
        channel=channel_id,
        text=f"Running security report on: *{topic}*. This may take a minute..."
    )
else:
    # Direct chat — bypass OpenClaw, talk straight to Ollama
    response = ollama_chat(message)
    slack_client.chat_postMessage(channel=channel_id, text=response)
```

The pipeline is spawned as a subprocess so the bot can immediately acknowledge the request without blocking. The report gets posted back to the channel when it completes.

### The OpenClaw Bypass Decision

This is worth explaining because it's not obvious from the outside. OpenClaw ships with a substantial built-in system prompt — workspace files, agent definitions, heartbeat config — that totals roughly 15,000–17,000 tokens before your message even arrives. On a 3B model with a limited context window, that overhead is significant. Response times for Slack messages routed through OpenClaw were unacceptably slow, and the model was frequently hitting context limits.

The fix was to bypass OpenClaw entirely for Slack interactions. The Slack bot talks directly to Ollama's `/api/chat` endpoint, with a minimal system prompt scoped to the task. OpenClaw remains useful for the web UI — where the richer agent context is a feature — but it's not in the critical path for Slack responses.

This is a good example of the kind of architectural decision that only becomes clear once you're running the system under real conditions. The initial assumption was that all LLM interaction would go through OpenClaw. The reality was that OpenClaw's design is optimized for something different than low-latency chat.

---

## Part 5 — Lessons Learned

### Context Window Management

The context window is the binding constraint on everything in this stack. A 3B model running on consumer hardware has a finite context budget, and it fills up faster than you'd expect. The multi-agent pipeline is actually a context management strategy as much as it is an agent strategy — by giving each agent a focused context, you avoid loading the entire problem into a single pass.

Watch for silent degradation. When a model hits its context limit it doesn't always error — it starts ignoring earlier parts of the input. If your pipeline output starts looking shallow or repetitive, context overflow is the first thing to check.

### System Prompt Bloat

OpenClaw's built-in workspace files (`AGENTS.md`, `SOUL.md`, `HEARTBEAT.md`, `TOOLS.md`) are loaded into every request. Trimming these files reduced token overhead meaningfully, but the bundled system prompts OpenClaw injects are harder to control. For use cases where you need lean, fast inference — like Slack responses — design your integration to bypass the agent layer and talk directly to Ollama.

### Model Selection Per Use Case

Not every task needs the same model. In this setup:

- **llama3.2:3b** — fast, low overhead, good for direct Slack chat and pipeline agents
- **mistral** — better reasoning, higher quality output, used for the OpenClaw web UI where latency is more acceptable

Matching model to use case matters more than always using the biggest available model. A fast, accurate 3B response beats a slow, slightly better mistral response for conversational interactions.

### Report Persistence

Reports were initially being written inside the container filesystem and lost on every rebuild. The fix is a host volume mount in `docker-compose.yml`:

```yaml
volumes:
  - ~/ai-stack/reports:/app/outputs/reports
```

Reports now persist at `~/ai-stack/reports/` on the host, survive container rebuilds, and are accessible outside Docker without any additional steps. This should be set up before the first report runs — not after.

---

## Part 6 — What's Next

The pipeline works, but it's operating without external data. Every report is generated from what the model knows from training — which is useful but has a ceiling. The most impactful near-term improvements:

- **MISP/OpenCTI integration** — wire live IOC and threat intel data into the Risk Analyst agent. Instead of reasoning from training data alone, the agent gets current indicators from the homelab threat intel stack.
- **Memory system** — agents that can reference past reports. If you've already generated a report on container hardening, a follow-up report on a related topic should be able to build on it rather than starting from scratch.
- **Real-time web research** — an initial research agent that pulls current threat advisories before the pipeline runs, feeding fresh context to the Researcher and Risk Analyst.
- **Report browsing UI** — reports currently accumulate as markdown files in `~/ai-stack/reports/`. A lightweight web interface for browsing, searching, and comparing reports would make the output significantly more useful.
- **Debate mode** — two Risk Analyst agents with different threat modeling perspectives (attacker-focused vs. defender-focused) whose outputs get reconciled by the Writer. Likely to improve risk coverage on complex topics.

---

## Closing

What this pipeline demonstrates is that useful security tooling doesn't require cloud APIs, SaaS subscriptions, or sending your data to someone else's infrastructure. A consumer GPU, a local LLM, and a few hundred lines of Python produce structured security reports that are genuinely useful for homelab hardening, threat modeling exercises, and building institutional knowledge.

The Slack integration closes the loop — the tool fits into the workflow rather than requiring a dedicated interface. The Zero Trust networking model from the [Tailscale article](/orange-book/zero-trust-homelab-tailscale/) means the bot and the pipeline run entirely within a private, authenticated environment.

The current version is a starting point. Wiring in live threat intel data from MISP and OpenCTI is the next unlock — at that point the pipeline stops reasoning from static training data and starts reasoning from current intelligence. That article is coming.

---

### Sample Report Output

To make this concrete, here's a sanitized example of pipeline output for the topic *Docker volume mount hardening*:

---

**Executive Summary**

This report outlines the security risks associated with volume mounts, provides mitigations and recommendations for securing these storage mechanisms within containers. It highlights common vulnerabilities and offers a checklist to ensure secure configuration of volume mounts.

**Risks**

1. **Insufficient Access Controls** — High impact, medium likelihood.
   Mitigation: Implement Least Privilege Principle, Role-Based Access Control (RBAC), and regularly review access permissions.

2. **Insecure File Permissions** — High impact, low likelihood.
   Mitigation: Set file ownership and permissions accordingly (e.g., `chown user:group`; `0444` for public files; `0440` for group files).

3. **Weak Passwords / Insecure Connections** — Medium impact, medium likelihood.
   Mitigation: Enforce strong password policies, implement MFA, and regularly update secure connections using TLS.

4. **Lack of Encryption** — High impact, low likelihood.
   Mitigation: Use full disk encryption with a trusted algorithm (e.g., AES-256).

**Recommendations**

1. Conduct regular security audits to identify vulnerabilities and address them promptly.
2. Implement incident response plans for security events involving volume mounts.
3. Use tools like `last` and `ausearch` to monitor volume mounts for suspicious activity.

**Best Practices**

1. Regularly review and update access permissions.
2. Enforce strong password policies and implement MFA.
3. Use full disk encryption with a trusted algorithm.
4. Implement RBAC for secure storage access.

---

*Report generated locally by the CyberClaw security pipeline. No data left the network.*

---

*This article is part of the CyberGrind Orange Book — hands-on technical build documentation from the homelab.*
