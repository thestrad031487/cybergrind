---
title: "Intune in Practice, Part 2: Enrollment & Architecture 101"
date: 2026-07-21
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "endpoint management", "windows autopilot", "entra id", "tenant architecture", "orange-book"]
description: "The enrollment method and tenant structure decisions that are genuinely painful to walk back later — Autopilot, Company Portal, co-management, and how group strategy actually scales. Part 2 of Intune in Practice."
---

Part 1 covered what Intune is. This one covers the decisions that are expensive to unwind once devices are already enrolled and policies are already assigned — because unlike a compliance policy you can just edit, ownership model and tenant structure tend to get baked into a fleet from day one.

## The decision is about ownership, not platform

It's tempting to think about enrollment method by platform — "how do I enroll a Windows PC" vs. "how do I enroll an iPhone." The more useful lens is ownership: is this device company-owned or personal? That single distinction drives almost everything else about which method fits.

| Method | Ownership model | Best fit |
|---|---|---|
| **Windows Autopilot** | Corporate-owned only — cannot be used for personal/BYOD devices | Zero-touch provisioning; device ships to the user and configures itself on first boot |
| **Company Portal (user-driven)** | Personal (BYOD) or corporate | User opts in and enrolls themselves; the standard BYOD path |
| **Device Enrollment Manager (DEM)** | Corporate-owned, shared | Bulk enrollment of shared/kiosk devices under one service account, up to 1,000 devices per account |
| **Provisioning package** | Corporate-owned | Offline/bulk setup for labs or isolated environments with no network dependency during setup |
| **Co-management** | Corporate-owned | Transitional bridge for organizations still running Configuration Manager, gradually shifting workloads to Intune |

The practical read for most small-to-mid IT shops: Autopilot user-driven realistically covers the large majority of corporate Windows devices, Company Portal covers BYOD, and DEM/provisioning packages are worth reaching for only if you actually have shared or kiosk-style devices. Co-management is a transitional state on the road to fully cloud-native management, not a permanent architecture — worth knowing going in so it doesn't quietly become permanent by default.

## The Autopilot licensing myth

Worth killing early because it causes real budget confusion: Autopilot itself isn't a separately licensed product. It's a provisioning capability built into Windows and the Intune management plane. Standard Autopilot scenarios — user-driven Entra join, self-deploying mode, pre-provisioning — run on Intune Plan 1 plus Entra ID P1, both of which are already included in Microsoft 365 E3 and E5. If a licensing conversation somewhere has assumed Autopilot needs Intune Plan 2 or the full Suite, that's not accurate for the common deployment scenarios — worth double-checking before anyone budgets for an add-on that isn't actually required here.

## The Enrollment Status Page gotcha

The Enrollment Status Page (ESP) is what a user sees during Autopilot setup — a progress screen that can also block the user from using the device until required apps and policies finish installing. This is genuinely useful, but it has a well-known failure mode: the "block device use" setting has separate device-setup and user-setup phases, and blocking both is a common cause of help desk tickets when an app install stalls during the user phase. The safer default is blocking only the device-setup phase, so a slow app install during the user phase doesn't strand someone at a frozen screen with no way to get to their desktop.

## Tenant structure: resist the urge to split

If you're standing this up on a single M365 tenant already, don't overthink this part: Microsoft's own guidance is to use a single tenant if your needs can be met with that architecture, reserving multiple tenants for organizations at genuinely large scale (Microsoft's education architecture guidance draws the line around the one-million-user mark) or where a separate tenant is needed to validate tenant-wide changes without touching production. Multi-tenant setups add real management overhead — decoupled Conditional Access policies, decoupled directory roles, decoupled everything — that most organizations don't need and don't want to maintain.

## Group strategy: this is where scale actually gets decided

Once devices are enrolled, how you group them determines whether policy assignment stays manageable or turns into a mess six months in. A few things worth getting right from the start:

- **Use dynamic groups**, not manual membership, for anything that should scale on its own — "all Windows 11 devices," "all devices in a given department" — so new enrollments pick up the right policies automatically instead of requiring someone to remember to add them.
- **Don't recreate "All Users" or "All Devices."** Intune already provides these as built-in virtual groups with no management overhead; a custom equivalent is just extra maintenance for no benefit.
- **Prefer assignment filters over mixed exclusion groups.** Rather than manually excluding specific devices from a broad assignment, assign to the group and use a filter to refine scope dynamically — it's more maintainable as the fleet changes.
- **Watch group-membership timing.** Dynamic group membership updates aren't instant — a newly registered Autopilot device showing "Unassigned" against its deployment profile is often just membership catching up, not a misconfiguration.

For BYOD-vs-corporate scoping specifically, the practical pattern is a general restriction blocking personal-device enrollment, with a narrower, higher-priority exception scoped to an approved group — the ordering matters, since the more permissive rule has to sit above the general block or it never takes effect.

Part 3 moves into compliance policy design — the difference between a policy that's actually enforcing something and one that's just checkbox theater.

---

### References

- Microsoft Learn. "Step 5 – Enroll devices in Microsoft Intune." [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/device-enrollment/enroll-devices)
- Microsoft Learn. "Windows Autopilot requirements." [learn.microsoft.com](https://learn.microsoft.com/en-us/autopilot/requirements)
- Microsoft Learn. "Windows Autopilot user-driven Microsoft Entra join — Configure and assign the Enrollment Status Page." [learn.microsoft.com](https://learn.microsoft.com/en-us/autopilot/tutorial/user-driven/azure-ad-join-esp)
- Microsoft Learn. "Resource isolation with multiple tenants to secure with Microsoft Entra ID." [learn.microsoft.com](https://learn.microsoft.com/en-us/entra/architecture/secure-multiple-tenants)
- Microsoft Learn. "Assignment filter performance tips for Intune." [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/fundamentals/filters-performance-recommendations)
- ManageEngine. "Intune Enrollment Methods Compared." [manageengine.com](https://www.manageengine.com/products/active-directory-audit/kb/intune-enrollment-methods.html)
- Microsoft Negotiations. "Windows Autopilot Licensing: What Your M365 Covers (2026)." [microsoftnegotiations.com](https://microsoftnegotiations.com/blog/windows-autopilot-licensing)
