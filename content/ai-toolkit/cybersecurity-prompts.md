---
title: "Cybersecurity Prompt Library"
date: 2026-04-13T08:00:00-05:00
description: "A practical library of AI prompts organized by SOC use case — threat hunting, phishing triage, log analysis, report writing, and more."
tags: ["AI", "prompting", "SOC", "cybersecurity"]
weight: 3
---

## Threat Hunting

> "You are a threat hunter. Given the following network logs, identify any patterns consistent with lateral movement, beaconing, or data exfiltration. Think step by step before giving your findings."

> "Review these DNS query logs and flag any domains that look algorithmically generated (DGA), have unusual query frequency, or resolve to known threat infrastructure."

## Phishing Triage

> "Analyze this email header and body. Identify indicators of phishing including spoofed sender, suspicious links, urgency language, and mismatched display names vs actual addresses."

> "You are a phishing analyst. Score this email from 1-10 for likelihood of being malicious and explain your reasoning. Flag specific indicators."

## Log Analysis

> "Review this Windows Event Log excerpt and identify any events consistent with credential dumping, privilege escalation, or persistence mechanisms. Reference MITRE ATT&CK techniques where applicable."

> "Analyze this firewall log and identify the top 5 most suspicious outbound connections. For each, explain why it stands out."

## Vulnerability Assessment

> "Given this Nessus scan output, prioritize the findings by exploitability and potential business impact. Focus on critical and high findings first."

> "Explain CVE-[number] in plain English. What is the attack vector, what systems are affected, and what is the recommended remediation?"

## Incident Response

> "You are an incident responder. Based on this timeline of events, construct a likely attack narrative and identify gaps in the forensic record that need investigation."

> "Draft an incident report executive summary for the following breach. Keep it under 200 words, avoid technical jargon, and focus on business impact and remediation steps taken."

## Report Writing

> "Convert these raw technical findings into a professional penetration test finding. Include: title, severity, description, business impact, and remediation recommendation."

> "You are a security report writer. Rewrite this finding to be appropriate for a non-technical executive audience. Remove jargon and focus on risk and business impact."

## Threat Intelligence

> "Analyze this IOC list and group the indicators by type. For each group, suggest hunting queries and detection logic."

> "Given this malware sample behavior report, map the observed behaviors to MITRE ATT&CK techniques and suggest relevant detections."
