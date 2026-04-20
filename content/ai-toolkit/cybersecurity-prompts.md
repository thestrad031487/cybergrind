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

> "You are hunting for living-off-the-land (LOTL) activity. Review this process execution log and identify any suspicious use of built-in Windows tools such as PowerShell, WMI, certutil, or mshta that could indicate attacker abuse."

> "Given this list of user logon events, identify any accounts showing anomalous behavior — off-hours access, impossible travel, or access to resources outside their normal baseline."

## Phishing Triage

> "Analyze this email header and body. Identify indicators of phishing including spoofed sender, suspicious links, urgency language, and mismatched display names vs actual addresses."

> "You are a phishing analyst. Score this email from 1-10 for likelihood of being malicious and explain your reasoning. Flag specific indicators."

> "Extract all URLs from this email and evaluate each one for suspicious characteristics: lookalike domains, recently registered domains, URL shorteners, or redirects to credential harvesting pages."

> "A user reported this email as suspicious but it passed our spam filter. Explain in plain language what makes this a phishing attempt so I can use it in a security awareness training example."

## Log Analysis

> "Review this Windows Event Log excerpt and identify any events consistent with credential dumping, privilege escalation, or persistence mechanisms. Reference MITRE ATT&CK techniques where applicable."

> "Analyze this firewall log and identify the top 5 most suspicious outbound connections. For each, explain why it stands out."

> "You are a SOC analyst. Review this Sysmon log and identify any process injection attempts, hollowing, or unusual parent-child process relationships."

> "Given this Okta audit log, identify any authentication events that suggest account compromise — failed MFA, new device enrollments, session anomalies, or admin privilege changes."

> "Parse this web server access log and identify potential reconnaissance activity, including directory traversal attempts, scanner signatures, and unusually high request rates from single IPs."

## Vulnerability Assessment

> "Given this Nessus scan output, prioritize the findings by exploitability and potential business impact. Focus on critical and high findings first."

> "Explain CVE-[number] in plain English. What is the attack vector, what systems are affected, and what is the recommended remediation?"

> "You are a vulnerability analyst. Given this list of CVEs from our last scan, identify which have public exploits available, which are in CISA's KEV catalog, and which should be prioritized for emergency patching."

> "Review this patch management report. Identify systems that are most overdue and most exposed based on network segment and installed software. Suggest a prioritized remediation order."

## Incident Response

> "You are an incident responder. Based on this timeline of events, construct a likely attack narrative and identify gaps in the forensic record that need investigation."

> "Draft an incident report executive summary for the following breach. Keep it under 200 words, avoid technical jargon, and focus on business impact and remediation steps taken."

> "You are leading a tabletop exercise on a ransomware scenario. Generate 5 escalating injects for a 90-minute exercise targeting a mid-sized nonprofit with limited IT staff."

> "Given this list of compromised hosts and the attacker's observed TTPs, draft a containment checklist in priority order. Include network isolation steps, credential reset requirements, and forensic preservation tasks."

> "Review this post-incident timeline and identify any detection or response failures. For each gap, suggest a specific control or process improvement that would have reduced dwell time or blast radius."

## Malware Analysis

> "You are a malware analyst. Given this behavioral sandbox report, summarize what this sample does in plain English. Identify persistence mechanisms, C2 communication patterns, and any evasion techniques observed."

> "Review these strings extracted from a suspicious binary and identify any indicators of malicious intent — hardcoded IPs, suspicious API calls, encoded payloads, or references to system paths commonly abused by malware."

> "Map the following observed malware behaviors to MITRE ATT&CK techniques and subtechniques. For each technique, suggest a detection opportunity."

> "Given this YARA rule, explain what it is designed to detect and identify any weaknesses that could allow a variant to evade it."

## Detection Engineering

> "Write a Sigma rule to detect the following suspicious behavior: [describe behavior]. Include the title, status, logsource, detection logic, and falsepositives fields."

> "Review this Sigma rule and identify any logic errors, overly broad conditions that would generate high false positive rates, or missing field normalizations."

> "You are a detection engineer. Given this threat actor TTP summary, propose three high-fidelity detection hypotheses with the log sources required to implement each one."

> "Convert this alert description into a structured detection use case with the following fields: hypothesis, log source, detection logic, tuning guidance, and response playbook stub."

## Report Writing

> "Convert these raw technical findings into a professional penetration test finding. Include: title, severity, description, business impact, and remediation recommendation."

> "You are a security report writer. Rewrite this finding to be appropriate for a non-technical executive audience. Remove jargon and focus on risk and business impact."

> "Draft a monthly SOC metrics summary for leadership based on the following data. Include: total alerts, escalations, MTTD, MTTR, top attack categories, and one key trend to watch."

> "Write a risk acceptance memo for the following vulnerability that our team has assessed as low priority for now. Include the risk description, compensating controls in place, and a review date."

## Threat Intelligence

> "Analyze this IOC list and group the indicators by type. For each group, suggest hunting queries and detection logic."

> "Given this malware sample behavior report, map the observed behaviors to MITRE ATT&CK techniques and suggest relevant detections."

> "You are a threat intelligence analyst. Summarize this threat actor profile in a structured format: aliases, motivation, target sectors, commonly used TTPs, and known malware families."

> "Given these recent IOCs from a threat feed, assess which are most likely to be relevant to our environment based on the following context: [describe your org/sector/stack]. Prioritize accordingly."

## Risk & Compliance

> "You are a GRC analyst. Given this NIST CSF 2.0 assessment output, identify the top three control gaps by business impact and draft a remediation recommendation for each."

> "Draft a control gap analysis summary for an organization that needs to achieve SOC 2 Type II readiness within 12 months. Assume a 50-person SaaS company with no formal security program currently in place."

> "Review this security policy draft and identify any gaps, ambiguous language, or missing sections relative to NIST SP 800-53 Rev. 5 requirements for a moderate-impact system."

> "Translate this technical security finding into a risk register entry. Include: risk description, likelihood, impact, inherent risk rating, current controls, residual risk rating, and recommended treatment."

## Security Awareness

> "Write a security awareness tip of the week for a non-technical employee audience on the topic of [topic]. Keep it under 150 words, use plain language, and end with one concrete action they can take today."

> "Create a phishing simulation debrief message for employees who clicked a test phishing link. The tone should be educational and non-punitive. Explain what they missed and what to look for next time."

> "Draft five multiple-choice quiz questions for a security awareness training module on password hygiene. Include one clearly correct answer and three plausible distractors for each question."

> "You are writing onboarding security training for new employees at a nonprofit. Summarize the top five security behaviors you want every employee to adopt, with a one-sentence explanation of why each matters."
