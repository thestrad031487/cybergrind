---
title: "Intune in Practice, Part 1: What Intune Actually Is (and Isn't)"
date: 2026-07-21
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "endpoint management", "microsoft 365", "entra id", "mdm", "orange-book"]
description: "Before deploying anything, it's worth being precise about what Microsoft Intune actually is, where it sits relative to Entra ID and Configuration Manager, and who it's genuinely built for. First in the Intune in Practice series."
---

Kicking off a new series here on Intune — this one's going to run long, because there's a lot of ground worth covering: architecture and enrollment, compliance policy design, conditional access, app deployment, configuration baselines, real lessons from running it as a one-person shop, and the attack surface it introduces once it's live. Part 1 starts with the boring-but-necessary step: being precise about what Intune actually is before deploying anything.

## Unified endpoint management, not just "MDM"

Intune gets called an MDM (mobile device management) tool a lot, which undersells it. It's more accurately described as a cloud-native unified endpoint management (UEM) platform — a single console meant to manage mobile devices, PCs, and applications across a mixed-device environment, consolidating what used to require separate tools for each platform. In practice that means Windows, macOS, iOS/iPadOS, Android, and increasingly Linux and Cloud PCs, all administered from one place rather than bolting together a device-specific tool for each OS.

That distinction matters because "MDM" implies device policy and remote wipe. UEM implies device policy, app deployment, compliance enforcement, and — critically — feeding device state into identity and access decisions elsewhere in the stack. Intune isn't just managing devices in isolation; it's a data source other security controls consume.

## It doesn't stand alone — Entra ID is load-bearing

This is the part that trips people up if they think of Intune as a self-contained product: Intune has an implicit dependency on Microsoft Entra ID (formerly Azure AD), since Intune relies on it for identity and conditional access. You can't meaningfully evaluate Intune's security value without also understanding how it plugs into Entra Conditional Access — a device can be perfectly compliant according to Intune's own policies, and that fact only matters once something downstream (a Conditional Access policy) actually checks it before granting access. We'll dig into that pairing specifically in Part 4.

## A quick history, because the naming has been a mess

If you've been in this ecosystem more than a few years, you've probably noticed Intune has gone by several names, and it's worth knowing why — it explains a lot of confusing legacy documentation still floating around. Microsoft launched the cloud service as Windows Intune in 2010, expanded it to more platforms, and eventually renamed it Microsoft Intune in 2014. In 2019, Microsoft combined the Intune UEM platform with the long-standing on-premises Configuration Manager (ConfigMgr) product, rebranding the combined offering Microsoft Endpoint Manager — the name a lot of people still default to out of habit. That branding was retired in 2022, returning to the Microsoft Intune name alongside the launch of the Intune Suite.

The practical relevance: if you're managing a hybrid environment with a ConfigMgr history, you're going to run into co-management concepts and documentation that assumes the Endpoint Manager branding. It's the same underlying capability, just renamed around it more than once.

## What's actually included vs. what's an add-on

This is genuinely useful to know before you scope a deployment, because licensing shapes what's realistic to plan for. Base Intune (Plan 1) ships with Microsoft 365 E3, E5, F1, F3, and Business Premium subscriptions. The Intune Suite — which layers on features like Remote Help, Endpoint Privilege Management, Advanced Analytics, Enterprise Application Management, and Cloud PKI — has historically been a paid add-on on top of that base license. That's changing: as of July 2026, Microsoft folded premium Intune Suite capabilities directly into M365 E3 and E5 licenses, with E3 subscribers gaining Remote Help, Advanced Analytics, and Plan 2 functions like Tunnel for MAM and specialized device management, while E5 subscribers additionally get Endpoint Privilege Management, Enterprise App Management, and Cloud PKI.

If you're running a lean M365 tenant and haven't looked at licensing in a while, this is worth revisiting — capability you might have written off as "an add-on we can't justify" may already be sitting in the license you're paying for.

## Who this is actually for

Intune makes the most sense for organizations already anchored in the Microsoft ecosystem — Entra ID for identity, M365 for productivity, and a device fleet that's mixed but not wildly exotic. It's not the right tool if your fleet is dominated by platforms Microsoft treats as second-class citizens, and it's overkill if you're managing a handful of devices with no real compliance requirements. For an environment already living in M365 and Entra, though, it's very hard to justify standing up a separate MDM product instead.

Part 2 gets into the architecture decisions that are genuinely painful to walk back later — enrollment method choice, tenant structure, and where co-management fits if you're coming from a ConfigMgr environment.

---

### References

- Microsoft. "Microsoft Intune — Endpoint Management." [microsoft.com/en-us/security/business/microsoft-intune](https://www.microsoft.com/en-us/security/business/microsoft-intune)
- Microsoft. "Microsoft Intune Core Features." [microsoft.com/en-us/security/business/endpoint-management/microsoft-intune](https://www.microsoft.com/en-us/security/business/endpoint-management/microsoft-intune)
- ManageEngine. "What Is Microsoft Intune? A Complete Guide." [manageengine.com](https://www.manageengine.com/products/active-directory-audit/kb/microsoft-intune/what-is-microsoft-intune.html)
- Computerworld. "Microsoft Intune explained: A leader in unified endpoint management." [computerworld.com](https://www.computerworld.com/article/1700964/microsoft-intune-explained-unified-endpoint-management.html)
- Quisitive. "Top 10 Reasons to Deploy Microsoft Intune in 2026." [quisitive.com](https://quisitive.com/top-10-reasons-to-deploy-microsoft-intune-in-2026-unified-endpoint-management-roi/)
