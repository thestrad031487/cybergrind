---
title: "Intune in Practice, Part 4: Conditional Access + Intune, the Real Perimeter"
date: 2026-07-23
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "conditional access", "entra id", "zero trust", "microsoft 365", "orange-book"]
description: "A compliance policy defines the bar. Conditional Access is what actually enforces it. The rollout pattern that avoids locking out your own users, and the blind spots worth knowing about. Part 4 of Intune in Practice."
---

Part 3 ended on a deliberately uncomfortable note: a compliance policy by itself doesn't block anything. It grades a device and moves on. This post is the other half of that pairing — Conditional Access is the piece that actually turns "this device is noncompliant" into "this device doesn't get in."

## How the signal actually flows

The mechanics are simpler than the reputation this pairing has: Intune evaluates a device against its compliance policy and reports a status (Compliant / Not Compliant) up to Entra ID. A Conditional Access policy with the "Require device to be marked as compliant" grant control reads that status at sign-in time and decides whether to let the authentication through. Compliance policy defines the bar. Conditional Access enforces it. Split those two apart and you get one of two broken outcomes, both worth knowing by name because they're the two most common misconfigurations: a compliance policy with no Conditional Access behind it produces reports nobody acts on (Part 3's whole point), and a Conditional Access policy requiring compliance with no compliance policies actually assigned means every device is noncompliant by default — including the ones that should legitimately have access.

This is the actual foundation of a Zero Trust posture in an M365 environment: identity gets verified (MFA, sign-in risk), and separately, device health gets verified, and access requires both, not either.

## The blind spot: this only works for enrolled devices

Worth being explicit about a limitation here rather than letting it surface as a surprise later: Conditional Access can only evaluate compliance for devices actually enrolled in Intune. Anything unmanaged — a personal device with no MDM enrollment, a browser session from a kiosk — has no compliance state to check, which is a different scenario than "noncompliant" and needs its own handling (either blocked outright, or routed through an app-protection/MAM fallback instead of a full device check).

There's also a specific, narrower gap worth knowing: the device-code OAuth flow can't provide device state to a Conditional Access compliance check at all, because the device performing authentication isn't the device requesting the code. That's a real gap, not a theoretical one — device code phishing is exactly the kind of technique that exploits gaps like this, and it's worth pairing this policy with a Conditional Access rule that blocks the device-code flow entirely except for a narrow, documented set of justified use cases.

## Don't lock yourself out

Before touching enforcement, exclude a break-glass emergency-access account and the service accounts used for Intune enrollment from any Conditional Access policy requiring compliance. This isn't optional caution — a misconfigured compliance policy or an Entra ID service hiccup combined with zero exclusions is exactly the scenario where an entire admin team ends up locked out of their own tenant with no way back in.

## Rolling it out without breaking things

Same principle as Part 3's enforcement rollout, applied at the Conditional Access layer: never go straight from nothing to enforced.

1. **Build the policy in Report-only mode.** It evaluates every sign-in and logs what would have happened without actually blocking anything.
2. **Run it for two to three weeks.** Long enough to catch a normal business cycle, not just a quiet week.
3. **Review the sign-in logs for legitimate users who would have been blocked.** This is where you catch compliance policy gaps, unenrolled corporate devices, or a group scoping mistake — before it's live.
4. **Fix what the report-only data surfaces, then flip to On.**

For most small-to-mid organizations, two policy patterns cover the bulk of what's needed rather than a sprawling policy set:

- **A core-workload policy** — Exchange Online, SharePoint Online, and Teams specifically — requiring compliant devices. This protects the systems that matter most first.
- **A catch-all policy** — all cloud apps — with the same compliance requirement, plus an OR condition allowing an approved client app or application protection policy as a BYOD-friendly fallback, so personal devices aren't just flatly locked out if MAM-based protection is an acceptable alternative for that use case.

One licensing/config note worth flagging if you're setting this up fresh: the older "Require approved client app" grant control on its own is being retired — Microsoft's guidance is to pair it with, or move fully to, "Require application protection policy" instead. If you're referencing older documentation or a policy built a while back, that's worth double-checking against current guidance rather than assuming it still works as written.

Part 5 moves on to app deployment — Win32 packaging, assignment logic, and the update lifecycle, which is where a lot of the day-to-day Intune workload actually lives once enrollment and access control are settled.

---

### References

- Microsoft Learn. "Require compliant, hybrid joined devices, or MFA." [learn.microsoft.com](https://learn.microsoft.com/en-us/entra/identity/conditional-access/policy-alt-all-users-compliant-hybrid-or-mfa)
- Microsoft Learn. "Conditional Access: Grant." [learn.microsoft.com](https://learn.microsoft.com/en-us/entra/identity/conditional-access/concept-conditional-access-grant)
- Microsoft Learn. "Conditional Access with Intune integration." [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/protect/conditional-access)
- CIAOPS. "Building Conditional Access That Actually Works: Requiring Intune-Compliant Devices." [blog.ciaops.com](https://blog.ciaops.com/2026/05/01/building-conditional-access-that-actually-works-requiring-intune-compliant-devices/)
- Wintive. "Microsoft Intune Compliance Policies Admin Guide (2026)." [wintive.com](https://www.wintive.com/tutorials/intune-mdm/intune-compliance-policies/)
