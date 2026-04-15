---
title: "Self-Hosted AI: Building a Private LLM Stack with OpenClaw, Ollama, and Tailscale"
date: 2026-04-15
description: "A full build walkthrough of a self-hosted AI platform using OpenClaw, Ollama, Docker GPU passthrough, and Tailscale — including the security model behind it."
tags: ["homelab", "AI", "ollama", "docker", "tailscale", "self-hosted", "llm"]
categories: ["orange-book"]
draft: false
---

There's a certain appeal to running your own language model. No API costs, no data leaving your network, no rate limits, no terms of service to worry about when you feed it sensitive context. For anyone who works in security — or just values privacy — the idea of keeping inference local is worth the setup cost.

This is a walkthrough of how I built a fully self-hosted AI platform on my homelab using OpenClaw as the agent layer, Ollama as the LLM runtime, Docker for containerization, an NVIDIA GPU for acceleration, and Tailscale for secure remote access. I'll cover what I built, how I built it, the problems I ran into, and — importantly — the security posture I put in place.

---

## What We're Building

The final architecture looks like this:

```
Browser (any device on my Tailnet)
        ↓
Tailscale HTTPS (Serve)
        ↓
OpenClaw (Docker container)
        ↓
Ollama (Docker container, GPU-enabled)
        ↓
Local LLM Models
```

Each layer has a job. Ollama runs the models and exposes a local API. OpenClaw sits on top of it as the agent UI and workflow layer. Docker keeps both isolated and portable. Tailscale handles remote access without opening a single port to the internet.

**Hardware used:**
- Any modern Linux machine with an NVIDIA GPU (I used an RTX 3060)
- Docker + Docker Compose
- Tailscale account (free tier works)

If you don't have a GPU, Ollama will fall back to CPU inference — it works, just slower. Smaller models like 3B parameters run acceptably on CPU.

---

## Part 1 — GPU Setup

Before Docker even enters the picture, the GPU needs to be accessible to containers. This requires two things: working NVIDIA drivers on the host, and the NVIDIA Container Toolkit.

### Install and Verify Drivers

First, confirm your drivers are functioning:

```bash
nvidia-smi
```

If that returns a table showing your GPU, driver version, and CUDA version, you're good. If it fails, install or reinstall the appropriate driver for your GPU and distro before continuing. This step is worth getting right — a driver mismatch between the host and container will cause silent failures later.

### Install NVIDIA Container Toolkit

The Container Toolkit is what lets Docker containers actually talk to the GPU:

```bash
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify it works by running an NVIDIA container directly:

```bash
docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu22.04 nvidia-smi
```

If you see the same `nvidia-smi` output from inside the container, GPU passthrough is working. This is the single most important verification step before building the stack.

**Common gotcha:** If the CUDA version reported inside the container doesn't match your host driver, the container toolkit wasn't configured correctly, or Docker wasn't restarted after configuration. Restart Docker and try again.

---

## Part 2 — Docker Stack

With GPU passthrough confirmed, the stack itself is straightforward. Two containers — `ollama` and `openclaw` — communicate over an internal Docker network.

### Stop Host Ollama (If Running)

If you have Ollama installed directly on the host, it will be holding port `11434`. Kill it before bringing up the stack:

```bash
sudo systemctl stop ollama
sudo systemctl disable ollama
```

Running both will cause a port conflict that's easy to mistake for a configuration error.

### Fix Docker DNS

On some systems, Docker containers can't resolve external hostnames out of the box. The fix is to give Docker explicit DNS servers in `/etc/docker/daemon.json`:

```json
{
  "dns": ["1.1.1.1", "8.8.8.8"]
}
```

Restart Docker after making this change. Without it, Ollama won't be able to pull model files when you request them.

### Bring Up the Stack

```bash
docker compose up -d
```

Verify both containers are running:

```bash
docker compose ps
```

Check that Ollama can see the GPU:

```bash
watch -n 1 nvidia-smi
```

Then in another terminal, run a quick model test:

```bash
docker exec -it ollama ollama run llama3.2:3b "hello"
```

If you get a coherent response, Ollama is up and GPU-accelerated. The `watch nvidia-smi` output should show GPU memory being consumed during inference.

---

## Part 3 — OpenClaw Configuration

OpenClaw's config lives at `~/ai-stack/openclaw-home/openclaw.json`. The two things that trip people up most often are the schema and the Ollama URL.

### The Ollama URL

This one matters. OpenClaw needs to reach Ollama over the internal Docker network, not localhost:

```json
"url": "http://ollama:11434"
```

Using `localhost` or `127.0.0.1` will fail — those resolve to the OpenClaw container itself, not Ollama. The service name `ollama` is resolved by Docker's internal DNS, which is exactly what you want.

### Models Array

The config schema requires a `models` array. A minimal working example:

```json
{
  "models": [
    {
      "provider": "ollama",
      "model": "llama3.2:3b",
      "url": "http://ollama:11434"
    }
  ]
}
```

Missing or malformed `models` is the most common reason OpenClaw fails to start cleanly.

### Container Permissions

If OpenClaw restarts in a loop, check the permissions on the config directory:

```bash
sudo chown -R 1000:1000 ~/ai-stack/openclaw-home
```

OpenClaw runs as UID 1000 inside the container. If the config directory is owned by root, it can't read its own config.

---

## Part 4 — Secure Remote Access with Tailscale

This is where the setup gets interesting from a security perspective. The problem to solve: OpenClaw's UI requires either `localhost` or HTTPS — it won't load over plain HTTP from a remote address. That means you can't just port-forward and call it done.

Tailscale Serve solves this cleanly.

### Why Tailscale Over a VPN or Open Port

Traditional approaches — opening a port, setting up WireGuard manually, or using a reverse proxy with a public DNS record — all require you to make something reachable from the internet, even if only to a limited audience. Tailscale's model is different: nothing is exposed to the public internet. Devices communicate over an encrypted mesh network, and only devices authenticated to your Tailnet can reach anything.

For a self-hosted LLM this matters. You're potentially feeding this thing sensitive data — incident notes, IOCs, internal documentation. You don't want that service discoverable.

### Setting Up Tailscale Serve

Tailscale Serve proxies a local service and terminates TLS automatically, using Tailscale's own certificate infrastructure:

```bash
sudo tailscale serve --bg http://127.0.0.1:18789
```

That's it. Tailscale provisions a certificate for `<hostname>.ts.net` and proxies HTTPS traffic to OpenClaw on port 18789. You can verify the cert:

```bash
tailscale cert <hostname>.ts.net
```

### Fixing MagicDNS on Clients

On Windows clients, Tailscale's MagicDNS (the thing that resolves `<hostname>.ts.net`) sometimes doesn't activate by default. If `.ts.net` addresses don't resolve on a client device, reset DNS acceptance:

```bash
tailscale up --reset --accept-dns=true
```

Verify resolution:

```bash
nslookup <hostname>.ts.net
```

You should get back a `100.x.x.x` Tailscale IP. Once that works, `https://<hostname>.ts.net` loads OpenClaw from any device on your Tailnet.

---

## Part 5 — Security Considerations

This section is worth reading carefully, even if you skipped the build steps. Self-hosted LLMs have a different threat model than most homelab services, and it's easy to underestimate the attack surface.

### What's Actually Exposed

Let's be precise about what this setup does and doesn't expose:

- **Ollama (port 11434):** Bound to the internal Docker network only. Not reachable from the host network, not reachable from the internet.
- **OpenClaw (port 18789):** Reachable only via Tailscale. Not bound to any public interface.
- **Tailscale endpoint:** Reachable only by devices authenticated to your Tailnet. In my case, that's just my own devices.

There is no public-facing attack surface in this setup. A port scan of the host from outside the Tailnet returns nothing relevant.

### Network Segmentation

The AI stack runs on a segmented network, isolated from other homelab services and from general home network traffic. This matters for a few reasons:

1. **Blast radius containment.** If something in the stack were compromised, it can't trivially pivot to other services on the network.
2. **Traffic isolation.** Model inference generates a lot of internal traffic. Keeping it segmented avoids interference with other services and makes anomalous traffic easier to spot.
3. **Principle of least privilege.** The containers don't need access to anything outside their own network. They don't have it.

### Authentication

OpenClaw requires a gateway token for UI access. Without it, the UI loads but is non-functional. This isn't a substitute for network-level controls — it's a second factor. The threat model here is: even if someone got onto the Tailnet unexpectedly, they'd still need the token to use OpenClaw.

The token is generated by OpenClaw on first run and entered through the Control UI settings. Treat it like an API key — don't share it, don't commit it anywhere.

### Tailscale as a Zero Trust Control Plane

Tailscale's security model is worth understanding, not just using. Each device on a Tailnet has a node key and authenticates to the Tailscale control plane via your identity provider (Google, GitHub, etc.). Access control is managed via ACLs in the Tailscale admin console.

In practice, this means:
- A new device can't join your Tailnet without authenticating through your IdP
- You can see every device on your Tailnet and revoke access instantly
- All Tailnet traffic is encrypted end-to-end (WireGuard under the hood)

For a homelab this is significantly stronger than a traditional VPN setup, and dramatically stronger than port-forwarding.

### What's Left to Harden

No setup is complete. Honest gaps in this one:

- **No WAF or rate limiting in front of OpenClaw.** Tailscale + token auth is the only layer. Adding Nginx with rate limiting in front would improve the posture.
- **Model integrity.** Ollama pulls models from the Ollama registry. There's no signature verification happening. For high-trust environments, consider pre-pulling and caching models locally rather than pulling on demand.
- **Secrets management.** The gateway token is stored in config on disk. For a more hardened setup, a secrets manager or at minimum encrypted storage would be appropriate.
- **Logging.** There's currently no centralized logging for queries sent to the model. For compliance-sensitive use cases, that's a gap worth closing.

These aren't showstoppers for a personal homelab — but they're worth knowing about.

---

## Current Status and What's Next

The stack is fully operational. Ollama is running GPU-accelerated inference on a 3B model, OpenClaw is accessible over HTTPS via Tailscale, and the whole thing is isolated behind segmented networking and Zero Trust access controls.

Next steps from here:

- Adding additional models (Qwen, Gemma) for different task profiles
- Building cybersecurity-specific agent workflows in OpenClaw
- Documenting those agents as they get built — expect follow-up posts in this section

If you build something similar, the two things most likely to bite you are the Docker DNS issue and the `localhost` vs. service-name distinction for the Ollama URL. Everything else is straightforward once the GPU passthrough is confirmed working.

---

*This article is part of the CyberGrind Orange Book — hands-on technical build documentation from the homelab.*
