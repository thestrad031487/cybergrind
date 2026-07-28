---
title: "Intune in Practice, Part 3: Compliance Policies That Actually Do Something"
date: 2026-07-22
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "endpoint management", "compliance policy", "conditional access", "microsoft 365", "orange-book"]
description: "A compliance policy that isn't wired into anything downstream doesn't enforce a single thing. Grace periods, the Not Evaluated trap, and how to roll enforcement out without locking out your own users. Part 3 of Intune in Practice."
---

Here's an uncomfortable fact about compliance policies that a lot of tenants learn the hard way: a compliance policy, on its own, doesn't block anything. It evaluates a device against a set of rules and labels it Compliant or Not Compliant — that's it. Nothing downstream actually happens unless something else is watching that label and acting on it. Get this wrong and you can have a fully built-out compliance policy that's pure checkbox theater, catching real problems and doing absolutely nothing about them.

## Two different jobs: compliance policies vs. configuration profiles

Worth being precise about this distinction, because the names get used interchangeably and they're not the same thing. Configuration profiles are what actually set a device up — enforce a setting, push a config, turn a feature on or off. Compliance policies check whether a device's current state meets your bar — encryption enabled, OS version current, a passcode set. One configures, the other grades. You generally need both: a configuration profile to make sure BitLocker gets turned on, and a compliance policy to catch the device where it somehow isn't.

## The policy that blocks nobody

This is the trap: build a well-designed compliance policy, assign it to a group, watch devices get correctly flagged Not Compliant — and nothing happens to them. No block, no warning, nothing. The policy is doing its job (evaluating), but the piece that turns "noncompliant" into an actual consequence is Conditional Access, and it's a separate, deliberate configuration step. A compliance policy without a Conditional Access policy behind it is a very well-organized list of problems nobody's acting on.

We'll get into the Conditional Access pairing itself in Part 4. The point for this post: don't treat "I built the compliance policy" as "I enforced anything." Those are two different projects.

## Grace periods: staged consequences, not instant blocks

The default noncompliance action — "mark device noncompliant" — fires immediately, zero days, unless you explicitly configure a schedule. Setting that schedule is what creates a grace period: the device sits in an "In Grace Period" state rather than flipping straight to Not Compliant, giving the user time to fix whatever's wrong (usually a pending OS update, the single most common failure) before anything blocks them.

Good practice is staging multiple actions on a gentle-to-firm curve rather than one blunt cutoff:

- Day 0 — mark noncompliant (starts the clock, no user-facing action yet)
- Day 1–3 — email notification explaining what needs fixing, in plain language rather than a policy-code dump
- Day 7 — second reminder
- Day 30 — retire the device if it's still noncompliant

For general guidance, a 3–7 day grace period is reasonable for most organizations — long enough to avoid punishing someone for a pending update or a transient sync issue, short enough that it isn't meaningless. Environments with a genuinely higher risk tolerance requirement tighten that considerably — sub-24-hour windows for corporate devices, sub-8-hour for BYOD — but that's a real tradeoff against help desk load from users hitting transient compliance blips, not a default to reach for without thinking about who's going to be fielding the tickets.

## The "Not Evaluated" trap

This one causes real confusion during troubleshooting. When you drill into a device's per-setting compliance detail, each setting shows one of: Compliant, Not Compliant, Error, or Not Evaluated. That last one gets misread constantly — it does not mean the setting passed. It means Intune couldn't check it at all: a required management extension isn't installed or isn't syncing, the device lacks a hardware capability the check depends on (TPM-backed health attestation being a common one), or the setting simply doesn't apply to that platform. A device full of "Not Evaluated" results isn't a clean device. It's an unverified one, and those aren't the same thing.

## Rolling out enforcement without locking out your own users

If you're moving from no enforcement to active blocking, don't flip the switch straight to production. Deploy the Conditional Access side in report-only mode first — this shows you exactly who would get blocked without actually blocking anyone, which is the only reliable way to catch a misconfigured policy or a batch of devices with stale compliance status before it turns into a flood of locked-out users. Move to enforcement only after the report-only data looks clean, and keep a grace period in place through that transition rather than going straight to a hard cutover.

Part 4 picks up exactly where this leaves off — the Conditional Access side of this pairing, and why device compliance is really only half the access-control picture.

---

### References

- Microsoft Learn. "Device compliance policy monitoring and reports for Intune." [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/protect/compliance-policy-monitor)
- Microsoft Learn. "Get started with device compliance policies in Intune." [learn.microsoft.com](https://learn.microsoft.com/en-us/intune/intune-service/protect/device-compliance-get-started)
- ManageEngine. "Intune Compliance Policy: The Complete Guide." [manageengine.com](https://www.manageengine.com/products/active-directory-audit/kb/microsoft-intune/microsoft-intune-compliance-policy.html)
- NinjaOne. "How to Use Intune Compliance Grace Period Effectively." [ninjaone.com](https://www.ninjaone.com/blog/use-intune-compliance-grace-period-effectively/)
- Wintive. "Intune Compliance Policies: 2026 Admin Guide." [wintive.com](https://www.wintive.com/microsoft-365-best-practices/intune-mdm/intune-compliance-policies/)
