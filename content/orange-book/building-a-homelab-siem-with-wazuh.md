---
title: "Building a Homelab SIEM with Wazuh"
date: 2026-05-13
description: "A practitioner's guide to deploying Wazuh as a self-hosted SIEM, enrolling agents across your environment, and understanding the security visibility it gives you."
tags:
  - siem
  - wazuh
  - homelab
  - cybersecurity
  - blue-team
categories:
  - Orange Book
series: "Security Operations"
author: "Logan"
draft: false
---

A SIEM — Security Information and Event Management system — is the nerve center of a security operations environment. It collects logs and telemetry from across your infrastructure, correlates events into alerts, and gives you a unified view of what's happening on every machine you care about. For years, running your own SIEM meant either paying for enterprise licensing or wrestling with complex open-source deployments. Wazuh changed that calculus significantly.

This article covers what Wazuh is, how to deploy it as a Docker stack, how to enroll agents across different operating systems, and what security visibility you actually get out of the other end.

---

## What Is Wazuh?

Wazuh is an open-source security platform that combines XDR (Extended Detection and Response) and SIEM capabilities into a single deployable stack. It descends from OSSEC, one of the oldest open-source host-based intrusion detection systems, and has evolved into a full-featured platform used by enterprises and homelabbers alike.

The stack has three central components:

**Wazuh Manager** handles agent communication, applies detection rules, processes alerts, and runs active response actions. Every agent in your environment connects back to the manager.

**Wazuh Indexer** is an OpenSearch-based data store that indexes all security events, alerts, and telemetry. This is where your data lives and where queries run.

**Wazuh Dashboard** is the web interface built on OpenSearch Dashboards with Wazuh plugins. This is where you monitor agents, investigate alerts, review compliance reports, and dig into security events.

Each component runs as a separate Docker container. In a single-node deployment — appropriate for a homelab or small environment — all three run on the same host.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           Wazuh Manager                 │
│         (port 1514/1515)                │
└──────────────┬──────────────────────────┘
               │ agent communication
       ┌───────┴────────┐
       │                │
┌──────▼──────┐  ┌──────▼──────┐
│ Linux Agent │  │ Win Agent   │  ... more agents
└─────────────┘  └─────────────┘

┌─────────────────────────────────────────┐
│           Wazuh Indexer                 │
│         OpenSearch (port 9200)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│           Wazuh Dashboard               │
│         Web UI (port 443)               │
└─────────────────────────────────────────┘
```

Agents communicate with the manager over TCP ports 1514 and 1515. The manager forwards processed events to the indexer. The dashboard reads from the indexer and also communicates directly with the manager API on port 55000.

---

## Deploying Wazuh with Docker

Wazuh provides an official Docker Compose repository that handles the entire deployment. The single-node stack is the right starting point for a homelab.

### Prerequisites

- Docker Engine or Docker Desktop
- At least 4 CPU cores and 8GB RAM
- The `vm.max_map_count` kernel parameter set to at least `262144` — the OpenSearch indexer requires this

```bash
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf
```

### Cloning and Deploying

```bash
git clone https://github.com/wazuh/wazuh-docker.git -b v4.14.3
cd wazuh-docker/single-node

# Generate TLS certificates
docker compose -f generate-indexer-certs.yml run --rm generator

# Bring the stack up
docker compose up -d
```

The first boot takes several minutes. The indexer needs to initialize its OpenSearch cluster, load security plugins, build index templates, and reach a GREEN cluster health state before the dashboard becomes responsive. Monitor progress with:

```bash
docker logs single-node-wazuh.indexer-1 --tail 10 -f
```

You're looking for `Cluster health status changed from [YELLOW] to [GREEN]` which signals the indexer is ready.

### Accessing the Dashboard

Once the stack is up, the dashboard is available at `https://<your-host-ip>`. Default credentials are `admin` / `SecretPassword` — change these immediately after first login under **Security → Internal Users**.

---

## Enrolling Agents

Agents are lightweight processes that run on the machines you want to monitor. They collect logs, monitor files, scan configurations, and report everything back to the manager. The manager IP you use during enrollment depends on your network setup — use whatever IP is reachable from the agent machine to the Wazuh server.

### Linux Agent (Ubuntu/Debian)

```bash
wget https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/wazuh-agent_4.14.3-1_amd64.deb
sudo WAZUH_MANAGER='<manager-ip>' dpkg -i wazuh-agent_4.14.3-1_amd64.deb
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

### Linux Agent (RHEL/CentOS/Fedora)

```bash
sudo WAZUH_MANAGER='<manager-ip>' rpm -ihv wazuh-agent-4.14.3-1.x86_64.rpm
sudo systemctl daemon-reload
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent
```

### Windows Agent

```powershell
Invoke-WebRequest -Uri https://packages.wazuh.com/4.x/windows/wazuh-agent-4.14.3-1.msi -OutFile wazuh-agent.msi
Start-Process msiexec.exe -Wait -ArgumentList '/i wazuh-agent.msi /q WAZUH_MANAGER="<manager-ip>"'
Start-Service WazuhSvc
```

### macOS Agent

```bash
curl -so wazuh-agent.pkg https://packages.wazuh.com/4.x/macos/wazuh-agent-4.14.3-1.arm64.pkg
sudo WAZUH_MANAGER='<manager-ip>' installer -pkg wazuh-agent.pkg -target /
sudo /Library/Ossec/bin/wazuh-control start
```

After enrollment, agents appear in the Wazuh dashboard under **Agents**. New agents may show as **Pending** until the manager accepts the enrollment — this happens automatically by default.

### Verifying Agent Connectivity

On the agent machine, check the agent log for successful connection:

```bash
# Linux
sudo tail -f /var/ossec/logs/ossec.log | grep -i "connected\|error"
```

A successful connection looks like:
```
wazuh-agentd: INFO: Connected to the server (192.168.x.x:1514).
```

---

## What Wazuh Actually Monitors

Once agents are enrolled, here's what you get out of the box without any additional configuration.

### File Integrity Monitoring (FIM)

Wazuh watches critical system directories for unauthorized changes. On Linux this includes `/etc`, `/usr/bin`, `/usr/sbin`, and other sensitive paths. On Windows it monitors the registry and system directories. Any modification — creation, deletion, permission change, content change — generates an alert with the before and after state, the user who made the change, and a timestamp.

This is particularly valuable for detecting persistence mechanisms. Malware that modifies `/etc/passwd`, drops a cron job, or installs a service will be caught immediately.

### Log Collection and Analysis

Wazuh collects and parses logs from hundreds of sources out of the box: syslog, auth.log, Windows Event Log, application logs, web server logs, and more. It applies a ruleset of thousands of detection rules to identify suspicious patterns — brute force attempts, privilege escalation, suspicious process execution, and known attack signatures.

### Security Configuration Assessment (SCA)

On enrollment, agents immediately run a CIS benchmark scan against the host. For Ubuntu 24.04 it runs the CIS Ubuntu 24.04 policy, checking hundreds of configuration items and scoring the system's compliance posture. Results appear in the dashboard under **Security Configuration Assessment** for each agent.

### Vulnerability Detection

Wazuh inventories installed packages on each agent and cross-references them against the NVD (National Vulnerability Database) and other sources. It surfaces CVEs affecting your specific package versions with CVSS scores, so you know exactly which machines need patching and how urgently.

### Rootkit Detection

The rootcheck module scans for signs of rootkits, hidden processes, hidden files, and anomalous kernel modules. It runs periodically and alerts on anything that looks like tampering at the OS level.

### Active Response

Wazuh can take automated action when certain rules fire. The most common example is blocking an IP address that triggers a brute force detection rule — Wazuh will automatically add a firewall rule to drop traffic from that IP for a configurable period. Active response can be customized with your own scripts for any action you want to automate.

---

## MITRE ATT&CK Integration

Every Wazuh alert is tagged with the relevant MITRE ATT&CK technique and tactic where applicable. This means you're not just seeing raw alerts — you're seeing them mapped to an adversary behavior framework that tells you what phase of an attack they represent. An alert tagged T1078 (Valid Accounts) means someone is using legitimate credentials in a suspicious way. T1059 (Command and Scripting Interpreter) means a script or shell is running in a context that warrants attention.

The dashboard includes an ATT&CK heatmap view that shows which techniques have fired across your environment, giving you a visual sense of your threat exposure.

---

## Compliance Reporting

Wazuh ships with built-in dashboards for PCI-DSS, HIPAA, GDPR, NIST 800-53, and TSC compliance. These aren't just checkboxes — they map actual alert data and configuration assessment results to specific control requirements. If you're building toward any of these frameworks, Wazuh gives you a head start on audit evidence.

---

## Security Benefits at a Glance

Running Wazuh across your environment gives you visibility you simply don't have without it. Here's what changes:

**Before Wazuh:** Someone SSH brute-forces your server for three days before succeeding. You find out when you notice unusual processes running weeks later — if you notice at all.

**After Wazuh:** The brute force triggers a rule after 10 failed attempts. Active response blocks the source IP automatically. You get an alert within seconds. If they somehow succeed, the login from an unusual IP triggers another alert, and any files they touch are logged via FIM.

The same pattern holds for privilege escalation, lateral movement, persistence mechanisms, and data exfiltration attempts. Wazuh doesn't prevent attacks — your firewall, patch management, and access controls do that. What Wazuh does is collapse the detection gap: the time between an attacker gaining access and you knowing about it.

For a homelab running production services, personal data, or anything you actually care about, that visibility is the difference between a contained incident and a complete compromise.

---

## Operational Notes

A few things worth knowing from running this in practice:

**The indexer is resource-hungry on first boot.** OpenSearch initializes a large number of plugins and index templates. Allow 5-10 minutes before expecting the dashboard to be responsive. Monitor `docker logs` on the indexer and wait for GREEN cluster health.

**The JVM security policy matters on newer Java versions.** Wazuh's indexer uses OpenSearch which includes a performance analyzer plugin that references a Java security policy file. On Ubuntu 26.04 with Java 21, this causes a startup crash. The fix is to remove the security policy line from `jvm.options` and mount the modified file into the container.

**Agent IPs need to be reachable from the manager.** The Wazuh manager needs to be able to communicate back to agents for active response and configuration updates. If your agents are behind NAT or on different network segments, ensure bidirectional connectivity on ports 1514 and 1515.

**Change default credentials immediately.** The default `admin` / `SecretPassword` credentials are publicly documented. Change them before exposing the dashboard to any network.

---

## What's Next

A single-node Wazuh deployment monitoring a handful of agents is a solid starting point. From here, natural expansions include integrating external threat intelligence feeds, building custom detection rules for your specific environment, setting up email or Slack alerting for high-severity events, and eventually exploring the multi-node stack for redundancy and scale.

The Orange Book will cover each of these in dedicated articles as this series continues.
