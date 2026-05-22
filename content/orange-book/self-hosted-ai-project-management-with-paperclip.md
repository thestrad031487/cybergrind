---
title: "Self-Hosted AI Project Management with Paperclip.ai"
date: 2026-05-22
description: "A practitioner's walkthrough of deploying Paperclip.ai on a self-hosted Ubuntu server, configuring an AI agent with local Ollama models, and the real troubleshooting path that got it working."
tags:
  - homelab
  - docker
  - ai
  - ollama
  - paperclip
  - self-hosted
categories:
  - Orange Book
author: "Logan"
draft: false
---

Paperclip.ai is a self-hosted AI project management platform. It gives you a Linear-style issue tracker where AI agents can actually pick up tasks, reason through them, and take action — all running on your own infrastructure. No cloud dependency, no data leaving your environment. For a homelab running a SOC stack, threat intelligence pipelines, and a growing collection of automation projects, having an AI agent that can work through a backlog is genuinely useful.

This article covers the full deployment, including what didn't work and why, because the path to a working setup was not straight.

---

## What Paperclip.ai Is

Paperclip.ai is an open-source platform that combines a project management interface with an AI agent runtime. You create issues, assign them to agents, and the agents execute tasks using whatever AI adapter you configure. The platform supports multiple adapter types — Claude Code, OpenCode, Codex, Gemini, and others — and stores all data locally in PostgreSQL.

The key differentiator from a standard issue tracker is that agents don't just comment on issues. They run code, read files, call tools, and produce real output. Think of it less like Jira and more like a task queue that an AI developer is actively working through.

---

## Infrastructure

**Host machine:** Ubuntu Server 24.04 LTS  
**Access:** Tailscale only (no public exposure)  
**Stack:** Docker Compose with PostgreSQL  
**AI runtime:** Ollama running locally with `llama3.1:8b`  
**Port:** 3100

---

## Deployment

Paperclip runs as a Docker Compose stack with two services: a Node.js server and a PostgreSQL database.

The compose file is straightforward, but there are several environment variables that must be set correctly or the platform will either fail to start or block authentication. More on that shortly.

### Prerequisites

- Docker Engine with Compose
- Ollama running and accessible on your network
- At least one model with 64K+ context pulled in Ollama

### Pulling a Compatible Model

This is worth calling out early. Paperclip's agent runtime requires a model with at least 64,000 tokens of context. Many commonly used models fall short of this:

- `qwen2.5-coder:7b` — 32K context. **Not compatible.**
- `mistral:latest` — 32K context. **Not compatible.**
- `llama3.1:8b` — 128K context. **Compatible.**

Pull a compatible model before starting the stack:

```bash
ollama pull llama3.1:8b
```

If you're running this on a machine with limited VRAM (the Ubuntu server here has an RTX 3060 with 6GB), `llama3.1:8b` at 4-bit quantization fits comfortably and leaves headroom for other services.

---

## Authentication Configuration

This is where most self-hosted deployments will get stuck. Paperclip uses `better-auth` for authentication, and it enforces a trusted origins policy. If the URL you're accessing the dashboard from doesn't match `BETTER_AUTH_TRUSTED_ORIGINS`, authentication will silently fail or refuse to create accounts.

The three environment variables that must be set correctly are:

```yaml
BETTER_AUTH_SECRET: "<your-secret>"
BETTER_AUTH_BASE_URL: "http://<your-server-ip>:3100"
BETTER_AUTH_TRUSTED_ORIGINS: "http://<your-server-ip>:3100,http://<local-ip>:3100"
```

If you're accessing Paperclip over Tailscale (recommended), set `BETTER_AUTH_BASE_URL` to your Tailscale IP. Include both your Tailscale IP and local LAN IP in `BETTER_AUTH_TRUSTED_ORIGINS` as a comma-separated list.

Without these set correctly, the dashboard loads but account creation is blocked.

### The .env File

Create a `.env` file alongside your `docker-compose.yml`:

```bash
BETTER_AUTH_SECRET=<generate-a-strong-secret>
PAPERCLIP_PUBLIC_URL=http://<tailscale-ip>:3100
BETTER_AUTH_BASE_URL=http://<tailscale-ip>:3100
BETTER_AUTH_TRUSTED_ORIGINS=http://<tailscale-ip>:3100,http://<local-ip>:3100
```

And reference these in `docker-compose.yml` under the server service environment:

```yaml
environment:
  BETTER_AUTH_SECRET: "${BETTER_AUTH_SECRET:?BETTER_AUTH_SECRET must be set}"
  BETTER_AUTH_BASE_URL: "${BETTER_AUTH_BASE_URL:-http://localhost:3100}"
  BETTER_AUTH_TRUSTED_ORIGINS: "${BETTER_AUTH_TRUSTED_ORIGINS:-http://localhost:3100}"
  PAPERCLIP_PUBLIC_URL: "${PAPERCLIP_PUBLIC_URL:-http://localhost:3100}"
```

---

## First Boot and Admin Account Creation

On first boot, navigate to `http://<your-server-ip>:3100`. You'll see:

```
Instance setup required
No instance admin exists yet. Run this command in your Paperclip environment
to generate the first admin invite URL:

pnpm paperclipai auth bootstrap-ceo
```

Run this inside the container:

```bash
docker exec -it <container-name> pnpm paperclipai onboard
```

Follow the onboarding wizard. When it asks about agent setup, you can configure it here or skip and configure later from the dashboard.

---

## Configuring the AI Agent — What Didn't Work

### Attempt 1: Hermes Agent

The Paperclip dashboard lists Hermes Agent as an adapter option. The natural instinct is to try it — especially after seeing the NetworkChuck video making the rounds about switching from OpenClaw to Hermes.

Hermes was installed on the host machine and the binary was mounted into the Paperclip container. After resolving several path issues (Hermes uses a uv-managed Python venv with hardcoded paths, requiring three separate volume mounts), it appeared to work — `hermes --version` returned successfully from inside the container.

The adapter test still failed. Paperclip's Hermes integration uses `hermes --print -` as its invocation pattern, which is not valid syntax in Hermes v0.14.0. The CLI interface changed and Paperclip's adapter hasn't caught up.

Digging further: there is no Hermes adapter code in the Paperclip server codebase at all. The available adapters are:

```
claude-local
codex-local
cursor-local
gemini-local
openclaw-gateway
opencode-local
pi-local
```

Hermes shows in the UI as a detected option based on the binary being in PATH, but there's no actual adapter implementation backing it. Dead end.

### Attempt 2: OpenCode with Ollama

OpenCode (`opencode-local`) is a fully supported adapter with actual implementation code in the Paperclip codebase. The challenge is configuring it to use a local Ollama instance rather than the cloud providers it defaults to.

OpenCode's config schema uses a `provider` key (not `providers`) and expects model definitions in a specific format. The config lives at `/paperclip/.config/opencode/config.json` inside the container — which maps to the persistent `paperclip-data` Docker volume.

Create the config:

```bash
docker exec <container-name> mkdir -p /paperclip/.config/opencode
docker exec <container-name> bash -c "cat > /paperclip/.config/opencode/config.json << 'EOF'
{
  \"$schema\": \"https://opencode.ai/config.json\",
  \"provider\": {
    \"ollama\": {
      \"api\": \"openai\",
      \"name\": \"Ollama\",
      \"models\": {
        \"llama3.1:8b\": {
          \"name\": \"Llama 3.1 8B\",
          \"contextLength\": 131072,
          \"reasoning\": false
        }
      }
    }
  },
  \"model\": \"ollama/llama3.1:8b\"
}
EOF"
```

**Important:** The `baseURL` and `apiKey` fields are stripped by OpenCode's schema validation. The Ollama endpoint URL needs to be configured separately. If your Ollama instance is running on the same host as Paperclip but outside Docker, use your Tailscale or LAN IP rather than `localhost` — `localhost` inside the container refers to the container itself, not the host.

Verify OpenCode can see the model:

```bash
docker exec <container-name> opencode models 2>&1 | grep ollama
# Expected output: ollama/llama3.1:8b
```

---

## Creating the Agent

In the Paperclip dashboard:

1. Navigate to **Agents**
2. Click **New Agent**
3. Name: `Einstein` (or whatever fits your environment)
4. Adapter type: **OpenCode**
5. Model: `ollama/llama3.1:8b`
6. Click **Test** — the adapter probe runs a live check

A successful test returns a response within 2-3 seconds and shows the run as succeeded in the activity log.

---

## Operational Notes

**The HOME variable matters.** The Paperclip container sets `HOME=/paperclip`. Any tool that resolves config paths relative to `$HOME` (like Hermes does with `~/.hermes/`) will look in `/paperclip/` instead of the expected host path. This caused repeated permission errors during the Hermes troubleshooting. If you mount external tool configs, either set `HOME` explicitly in the container environment or mount to the path the tool actually resolves.

**Port conflicts.** If you previously ran Paperclip as a standalone container (not via Compose), the old container will hold port 3100 and prevent the Compose stack from starting. Stop and remove the old container before bringing up the Compose stack.

**PostgreSQL volume persistence.** The `paperclip-data` volume persists all instance data including agent config, issue history, and backups. The `pgdata` volume persists the PostgreSQL database. Both survive container restarts and rebuilds. Don't delete them.

**Context length enforcement.** Hermes enforces a hard 64K context minimum. OpenCode does not enforce this at the adapter level but models with insufficient context will produce degraded output on complex tasks. Use a model with at least 64K context regardless of which adapter you're running.

**Automatic backups.** Paperclip runs automatic database backups every 60 minutes by default, stored in `/paperclip/instances/default/data/backups/` inside the container. The retention policy keeps 7 daily, 4 weekly, and 1 monthly backup. No additional configuration required.

---

## What's Next

A working Paperclip instance with a local Ollama agent is a useful foundation. From here, natural expansions include connecting the agent to your actual project repositories, wiring Slack notifications for issue updates, and building out a backlog of well-defined tasks the agent can actually execute.

The Orange Book will cover agent task design — how to write issues that an AI agent can actually work through versus ones that require too much implicit context to be actionable.
