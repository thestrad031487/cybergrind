---
title: "Intune in Practice, Part 8: Intune Attack Surface & Hardening"
date: 2026-07-27
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "endpoint management", "cybersecurity", "rbac", "cisa", "orange-book"]
description: "Whoever controls Intune controls the fleet. A March 2026 CISA advisory made that concrete after a destructive attack on Stryker's Microsoft environment. Least privilege, phishing-resistant MFA, and Multi Admin Approval — closing out the Intune in Practice series."
---

Every part of this series so far has been about building capability into Intune — enrollment, compliance, access control, apps, baselines. This last one is about the flip side: everything that makes Intune powerful for administration makes it equally powerful for whoever manages to compromise the administrative layer. Whoever controls Intune can push scripts, alter configurations, and remotely wipe devices across an entire fleet in one coordinated action — and in March 2026, that stopped being a theoretical concern.

## What actually happened

On March 11, 2026, a cyberattack disrupted medical technology firm Stryker's Microsoft environment badly enough to affect surgical operations at hospitals nationwide. According to reporting on the incident, the attackers — attributed to the Handala threat actor — compromised an administrator account and used it to create a new Global Administrator account, which was then used to wipe data across managed devices. No exotic exploit was involved. The attackers used Intune's own legitimate administrative functions, weaponized through a compromised credential, which is precisely what makes this kind of attack hard to catch — the actions blend into normal administrative activity instead of tripping a malware signature.

CISA issued a formal advisory on March 18, developed in coordination with the FBI and Microsoft, urging U.S. organizations broadly — not just Stryker's industry — to harden their endpoint management platforms against the same pattern. The advisory's framing is worth sitting with: it treats endpoint management systems like Intune as critical infrastructure deserving the same governance rigor as domain controllers and identity providers, not as a secondary admin tool.

## Three controls CISA specifically called out

The advisory's recommendations line up closely with Zero Trust practice already covered earlier in this series, applied specifically to the administrative layer rather than the end-user layer:

**Least privilege via RBAC and scope tags.** Use Intune's role-based access control to give each administrator only the permissions their actual responsibilities require, scoped as narrowly as practical — not broad, standing Global Administrator access as a default convenience. Scope tags let you segment which devices and users a given admin role can actually touch, so a compromised help-desk-tier account can't reach the entire fleet even if the credential itself is compromised.

**Phishing-resistant MFA and privileged access hygiene.** Standard MFA (an app push, a text code) has known bypass techniques; phishing-resistant methods (FIDO2 security keys, certificate-based authentication) close that gap specifically for accounts capable of administrative action. Pairing this with Privileged Identity Management — where elevated roles require just-in-time activation with justification rather than sitting active permanently — means a compromised standing credential doesn't automatically carry standing privilege.

**Multi Admin Approval for destructive actions.** This is the control that most directly addresses what happened at Stryker: configuring Intune so that high-impact actions — device wipe, RBAC changes, script deployment, policy changes to compliance or settings catalog profiles — require a second administrator's approval before they execute. A single compromised account, even one with legitimate elevated access, can't unilaterally push a destructive action through. Microsoft expanded this protection's coverage in 2026 specifically in response to this incident category.

## Why this matters even for a small tenant

It's tempting to read "nation-state-linked attacker, medical device manufacturer, hospitals affected" and conclude this is an enterprise-scale problem. It isn't, structurally. The attack technique doesn't require a large target — it requires an administrative account with more standing privilege than it needs and no second-approval gate on destructive actions. That combination exists in plenty of small tenants where a single administrator (sometimes the only IT person in the building) holds Global Administrator by default because there's never been a reason to scope it down. The size of the organization affects the blast radius of a compromise, not whether the underlying misconfiguration exists.

## A practical starting checklist

For a tenant that hasn't specifically hardened its Intune administrative layer yet, in rough priority order:

1. **Audit who currently holds Global Administrator or broad Intune admin roles**, and move anyone who doesn't need standing access to a narrower, scoped role instead.
2. **Enable Multi Admin Approval** for at minimum device wipe and RBAC changes — the two actions with the most irreversible blast radius.
3. **Require phishing-resistant MFA** for any account with administrative Intune access, not just a general MFA policy applied tenant-wide.
4. **Set up alerting on new administrative role assignments and new Global Administrator accounts specifically** — the Stryker incident's escalation path was creating a new Global Admin account, which is exactly the kind of event that should generate an immediate alert rather than being discovered later in a routine audit.

None of this requires additional licensing beyond what's already covered in this series — it's entirely a configuration and governance exercise, which makes it one of the highest-value places to spend hardening effort regardless of budget.

That closes out this series. Eight parts covering what Intune actually is, how to structure enrollment and tenant architecture, compliance policies with teeth, the Conditional Access pairing that enforces them, app deployment without losing your mind, configuration baselines, running it lean in a resource-constrained org, and finally, protecting the administrative layer itself. The common thread through all of it: Intune is only as good as the decisions made around it — licensing, scoping, sequencing, and governance matter at least as much as the platform's own feature set.

---

### References

- CISA. "CISA Urges Endpoint Management System Hardening After Cyberattack Against US Organization." March 18, 2026. [cisa.gov](https://www.cisa.gov/news-events/alerts/2026/03/18/cisa-urges-endpoint-management-system-hardening-after-cyberattack-against-us-organization)
- BleepingComputer. "CISA warns businesses to secure Microsoft Intune systems after Stryker breach." [bleepingcomputer.com](https://www.bleepingcomputer.com/news/security/cisa-warns-businesses-to-secure-microsoft-intune-systems-after-stryker-breach/)
- Redmondmag. "CISA, Microsoft Outline Intune Safeguards After Stryker Cyber Attack." [redmondmag.com](https://redmondmag.com/articles/2026/03/19/cisa-microsoft-outline-intune-safeguards.aspx)
- HIPAA Journal. "CISA Advises U.S. Organizations to Harden Microsoft Intune Following Stryker Data Wiping Attack." [hipaajournal.com](https://www.hipaajournal.com/cisa-harden-microsoft-intune/)
