---
title: "The New Perimeter, Part 4: Building an AI Security Gateway"
date: 2026-07-10
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["firewalls", "AI security", "LiteLLM", "deployment", "homelab", "orange-book"]
description: "Part 4: a working, open-source deployment blueprint for an AI Security Gateway using LiteLLM and Redis, with proper secrets handling."
---

[Part 3]({{< ref "new-perimeter-ai-two-fronts" >}}) covered the AI Security Gateway conceptually — inbound, RAG-context, and outbound protection for GenAI traffic. This part is the actual build: a working deployment using **LiteLLM**, an Apache 2.0 open-source AI gateway, with Redis for state tracking and rate limiting.

One note before the config: every example below uses environment variable references, not literal keys. Never commit real API keys, passwords, or master keys directly into a `docker-compose.yml` or config file that goes into version control — that's exactly the kind of exposure [the supply chain series]({{< ref "ai-supply-chain-baked-in-vulnerabilities" >}}) on this site covers. Use a `.env` file (and make sure it's in `.gitignore`) or a proper secrets manager instead.

## Architecture overview

```
              INBOUND / OUTBOUND DATA PIPELINE

  Enterprise Clients / Internal Apps        DevOps CI/CD Workloads
                    │                                 │
                    └────────────────┬────────────────┘
                                      ▼
                        Application Load Balancer
                              (TLS 1.3 termination)
                                      │
                                      ▼
        ┌─────────────────────────────────────────────────────┐
        │              LITELLM AI SECURITY GATEWAY             │
        │                                                       │
        │   Auth & AuthZ              Synchronous Guardrails    │
        │   • Virtual API keys   ──►  • Prompt injection check  │
        │   • Token rate limits       • PII masking/redaction   │
        │                                       │                │
        │   Egress Router             Semantic Cache             │
        │   • Latency-based LB  ◄──   • Redis vector matching   │
        │   • Region failover                                   │
        └───────────────────────┬───────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                 ▼
        Primary Endpoint   Fallback Pool    Observability Suite
        (Azure OpenAI)     (Anthropic /     • Langfuse auditing
                             AWS Bedrock)    • Prometheus metrics
```

## File 1: `docker-compose.yml`

```yaml
services:
  # Distributed state engine for rate limiting and session tokens
  litellm-redis:
    image: redis:7.2-alpine
    container_name: litellm-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_persistence_layer:/data
    networks:
      - gateway_security_network
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
    restart: always

  # Open-source AI security gateway data plane
  litellm-gateway:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: litellm-gateway
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    env_file:
      - .env
    command: ["--config", "/app/config.yaml", "--port", "4000"]
    depends_on:
      - litellm-redis
    networks:
      - gateway_security_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health/readiness"]
      interval: 10s
      timeout: 5s
      retries: 3
    restart: always

networks:
  gateway_security_network:
    driver: bridge

volumes:
  redis_persistence_layer:
```

Your `.env` file (never committed — add it to `.gitignore`) holds the actual values:

```
AZURE_API_KEY=your-azure-key-here
AZURE_API_BASE=https://your-org-eastus.openai.azure.com/
ANTHROPIC_API_KEY=your-anthropic-key-here
REDIS_PASSWORD=your-redis-password-here
LITELLM_MASTER_KEY=your-master-key-here
```

## File 2: `litellm_config.yaml`

Routing targets, guardrails, and caching behavior. This file is safe to commit — it only references environment variables, never literal secrets.

```yaml
model_list:
  # Primary model group, load balanced across regions
  - model_name: enterprise-gpt-4o
    litellm_params:
      model: azure/gpt-4o-deployment-us-east
      api_base: os.environ/AZURE_API_BASE
      api_key: os.environ/AZURE_API_KEY
      api_version: "2025-01-01-preview"
      rpm: 1200
      tpm: 500000

  # High-availability fallback (triggered during primary cloud disruptions)
  - model_name: enterprise-core-fallback
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY

router_settings:
  routing_strategy: latency-based-routing
  enable_pre_call_checks: true
  backoff_strategy: exponential

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: os.environ/REDIS_URL

litellm_settings:
  default_fallbacks: [["enterprise-gpt-4o", "enterprise-core-fallback"]]
  request_timeout: 45

  # Semantic and exact caching
  cache: true
  cache_params:
    type: redis
    supported_call_types: ["completion", "embedding"]
    ttl: 3600

  # Privacy controls
  turn_off_message_logging: false
  redact_user_api_key_info: true

  success_callback: ["prometheus"]
  failure_callback: ["prometheus"]

guardrails:
  - guardrail_name: inbound-text-moderation
    litellm_params:
      model: openai/moderation-endpoint
      api_key: os.environ/AZURE_API_KEY
    callbacks: ["pre-call"]

  - guardrail_name: automated-pii-masking
    litellm_params:
      mode: redact
    callbacks: ["pre-call"]
```

## Standing it up

```bash
docker-compose up -d --build
```

## Issuing scoped virtual keys

Don't hand internal teams your master key. Issue bounded virtual tokens scoped to a specific model pool, with a hard budget ceiling:

```bash
curl --location 'http://localhost:4000/key/generate' \
  --header "Authorization: Bearer ${LITELLM_MASTER_KEY}" \
  --header 'Content-Type: application/json' \
  --data '{
    "key_alias": "customer-portal-production-app",
    "models": ["enterprise-gpt-4o"],
    "max_budget": 500.00,
    "budget_duration": "30d",
    "tpm_limit": 60000,
    "rpm_limit": 200
  }'
```

## Why this matters for security teams

The gateway pattern here does the actual work described in Part 3 — prompt injection screening, PII redaction, and rate-limited scoped access — but none of it matters if the deployment itself leaks credentials. Treat this config file the same way you'd treat any other infrastructure-as-code: secrets in an environment layer or vault, everything else safe to review in a pull request.

**Next in this series:** where this is all heading — agentic firewalls that write their own rules, and what post-quantum cryptography means for the TLS stack sitting in front of all of this.

---

### References

- LiteLLM. "Open-Source LLM Gateway Documentation." [docs.litellm.ai](https://docs.litellm.ai/)
- OWASP. "Top 10 for Large Language Model Applications."
- Redis. "Redis Security Documentation." [redis.io/docs](https://redis.io/docs/)
