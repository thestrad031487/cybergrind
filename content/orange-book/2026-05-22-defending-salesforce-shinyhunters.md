---
title: "From the Trenches: Defending Salesforce Against ShinyHunters' Playbook"
date: 2026-05-22
description: "A practitioner's guide to hardening Salesforce environments against the three attack patterns ShinyHunters used to breach 1,000+ organizations — OAuth abuse, supply chain token theft, and Experience Cloud misconfiguration."
tags:
  - blue-team
  - salesforce
  - oauth
  - defender
  - hardening
  - shinyhunters
categories:
  - Orange Book
series: "From the Trenches"
author: "Logan"
draft: false
---

If you haven't read the threat intelligence breakdown of the ShinyHunters Salesforce campaign, start there. This article assumes you know what happened and focuses on what to do about it.

The short version: ShinyHunters ran three distinct campaigns against Salesforce environments across 2025 and into 2026. They never exploited a flaw in Salesforce's actual infrastructure. They exploited OAuth flows, integration trust, and misconfigured guest user permissions. More than 1,000 organizations were impacted. The blast radius hit cybersecurity companies — Cloudflare, Zscaler, Palo Alto Networks, Tenable — which is a useful reminder that having a security team doesn't make you immune to this class of attack.

Here's the defender playbook.

---

## Harden OAuth and Connected App Permissions

The Data Loader vishing campaign worked because organizations allow broad OAuth scopes and don't monitor connected app authorizations. Fix this.

**Restrict OAuth scopes on connected apps.** Every connected app in your Salesforce org should have the minimum scopes required to function. Full API access (`api`) is rarely necessary. Audit your connected app list and cut scopes down.

```
Setup → Apps → Connected Apps → Manage Connected Apps
→ Review OAuth Policies for each app
```

**Enable IP restrictions on connected apps.** If a connected app is only ever used from corporate IP ranges, enforce it. This won't stop an attacker who's already inside your network but it raises the bar significantly for external OAuth abuse.

**Disable the OAuth Device Flow where it's not needed.** The Device Authorization Grant (`device`) scope is what made the Data Loader attack possible. If your organization doesn't use devices that require this flow, disable it at the org level.

**Review and revoke stale OAuth tokens.** Tokens that haven't been used in 30+ days are a liability. Build a process to review and revoke them regularly.

```
Setup → Identity → OAuth and OpenID Connect Settings
```

**Monitor connected app activity.** New connected app authorizations should generate alerts. If an employee just approved a "Data Loader" app that your IT team didn't deploy, you want to know within minutes.

---

## Audit Your Third-Party Integrations

The Salesloft/Drift breach hit 760 organizations that never made a mistake in their own environment. They trusted a vendor integration. That integration became the attack vector.

**Inventory every connected app and integration.** You cannot defend what you cannot see. Pull a complete list of authorized OAuth apps and integrations in your Salesforce org. Most organizations are surprised by what they find.

**Apply least privilege to integration service accounts.** The Drift integration had a dedicated Salesforce user with broad permissions. Integration service accounts should be scoped to only the objects and actions the integration actually requires. If your chatbot integration has full read access to Opportunities and Cases, that's a scope problem.

**Monitor for anomalous API activity from integration accounts.** The Salesloft/Drift exfiltration generated high-volume API calls from Tor exit nodes. Behavioral anomaly detection on integration service account activity — sudden volume spikes, unusual SOQL query patterns, off-hours access — would have surfaced this faster.

**Have a vendor breach response plan.** When a vendor you're integrated with announces a breach, you need to be able to revoke their tokens and audit what was accessed within hours, not days. Know where your integration tokens live and how to revoke them before you need to.

**Don't store credentials in support cases.** The attackers specifically targeted Cases because organizations frequently paste API keys, AWS credentials, and Snowflake tokens into support tickets. Train your team. Sanitize credentials out of case content. This is hygiene, not sophistication.

---

## Lock Down Experience Cloud Guest User Permissions

The Aura campaign required no credentials at all. It targeted organizations that had left guest user profiles with excessive permissions on public-facing Experience Cloud sites. Salesforce's own advisory confirmed the attack vector: overly permissive guest user configurations allowing unauthenticated API access via the `/s/sfsites/aura` endpoint.

**Audit guest user profile permissions.** Guest users should have the absolute minimum permissions required for the public-facing functionality you intend to expose. Review every object permission on your guest user profile.

```
Setup → Profiles → Guest User Profile (for each Experience Cloud site)
→ Review Object Settings
```

**Disable API access for guest profiles.** Uncheck "API Enabled" in the guest user profile's system permissions unless there is a specific, documented reason it needs to be on.

**Set org-wide sharing defaults to Private.** This restricts what data is accessible to guest users by default, requiring explicit sharing rules for anything that should be public-facing.

**Disable object access that shouldn't be public.** If your public-facing Experience Cloud site doesn't need to expose Account or Contact records, those objects should not be accessible to guest users. Default deny.

**Enable Salesforce Shield or Event Monitoring for API activity.** The Aura exploitation generated API calls to the `/s/sfsites/aura` endpoint. Event Monitoring gives you visibility into these calls. If you're running public Experience Cloud sites, this visibility is non-negotiable.

**Run AuraInspector against your own sites.** Mandiant released AuraInspector in January 2026 specifically to help administrators detect misconfigured Experience Cloud instances. ShinyHunters weaponized it — you should use the legitimate version to find your own exposure before they do.

---

## Detection: What to Look For

Across all three campaigns, there are detectable signals if you know what to log.

**Connected app authorizations from unexpected users or locations.** Any OAuth authorization from an IP that doesn't match your corporate ranges or a user who doesn't typically use that app.

**SOQL queries hitting multiple high-value objects in sequence.** Attackers exfiltrating from Salesforce run queries against Accounts, Contacts, Cases, and Opportunities in rapid succession. Legitimate users don't do this at scale.

**Bulk data export events.** Salesforce logs data export activity. If someone is exporting thousands of records, that should trigger an alert.

**New connected app authorizations.** Any new OAuth authorization event should be reviewed. In the Data Loader campaign, the attack required the victim to authorize a new app. That authorization event is a detection opportunity.

**API calls from Tor exit nodes.** The Salesloft/Drift exfiltration was partially detected because of high-volume API calls from Tor infrastructure. If your SIEM is ingesting Salesforce Event Monitoring logs, feed them through threat intelligence enrichment.

**Aura endpoint scanning.** Unusual GET request volume against `/s/sfsites/aura` or `/s/sfsites/` endpoints from external IPs is a signal that someone is running reconnaissance or active exploitation against your Experience Cloud sites.

---

## The Uncomfortable Reality

These attacks worked because organizations treat SaaS platforms as someone else's security problem. Salesforce's infrastructure wasn't compromised. Your Salesforce configuration was.

Every integration you add extends your attack surface. Every OAuth token you issue is a credential. Every guest user profile you misconfigure is a potential unauthenticated API endpoint. The vendor provides the platform. The security posture is yours.

The organizations that fared best during these campaigns were the ones with OAuth activity monitoring, least-privilege integration policies, and incident response playbooks that included "vendor breach" scenarios. That's not a sophisticated security program. That's foundational hygiene applied to a SaaS environment.

If you're a security practitioner at an organization running Salesforce — especially one with Experience Cloud deployments or a rich integration ecosystem — run the AuraInspector scan, pull your connected app inventory, and review your guest user profile permissions this week. Not next quarter.

ShinyHunters moved from initial compromise to complete data exfiltration in under an hour. Your detection and response window is shorter than you think.

---

## Sources

- Mitiga — *ShinyHunters and UNC6395: Inside the Salesforce and Salesloft Breaches* — https://www.mitiga.io/blog/shinyhunters-and-unc6395-inside-the-salesforce-and-salesloft-breaches
- DoControl — *Who Is ShinyHunters? Tactics, Top Attacks & How to Protect Your Organization* — https://www.docontrol.io/blog/shinyhunters
- Push Security — *How three techniques are behind ShinyHunters' 2026 campaigns* — https://pushsecurity.com/blog/analyzing-the-instructure-breach
- Illumio — *The Master Key Problem: Inside the Salesloft Breach and Ongoing Threat* — https://www.illumio.com/blog/the-master-key-problem-what-the-salesloft-breach-reveals-about-an-ongoing-threat
- BleepingComputer — *ShinyHunters claims ongoing Salesforce Aura data theft attacks* — https://www.bleepingcomputer.com/news/security/shinyhunters-claims-ongoing-salesforce-aura-data-theft-attacks/
- Help Net Security — *ShinyHunters claims new campaign targeting Salesforce Experience Cloud sites* — https://www.helpnetsecurity.com/2026/03/11/shinyhunters-salesforce-aura-data-breach/
- SecurityWeek — *Hundreds of Salesforce Customers Allegedly Targeted in New Data Theft Campaign* — https://www.securityweek.com/hundreds-of-salesforce-customers-allegedly-targeted-in-new-data-theft-campaign/
- Reco — *Inside the ShinyHunters Experience Cloud Campaign: IOCs, Detection Logic, and What's at Risk* — https://www.reco.ai/blog/inside-the-shinyhunters-experience-cloud-campaign-iocs-detection-logic-and-whats-at-risk
- SafeState — *ShinyHunters Behind Salesforce Aura Data Theft Campaign* — https://www.safestate.com/post/shinyhunters-behind-salesforce-aura-data-theft-campaign
- Salesforce Ben — *FBI Issues Salesforce Instance Warning Over 'ShinyHunters' Data Theft* — https://www.salesforceben.com/fbi-issues-salesforce-instance-warning-over-shinyhunters-data-theft/

---

*Indicators of Compromise and MITRE ATT&CK mappings for all three campaigns are covered in the companion threat intelligence article.*
