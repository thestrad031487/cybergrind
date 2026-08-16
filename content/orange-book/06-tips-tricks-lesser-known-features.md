---
title: "Android in Intune: Tips, Tricks, and Lesser-Known Features"
date: 2026-08-16
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "android", "tips", "troubleshooting", "mdm"]
description: "The gotchas, power-user features, and workarounds for Android device management in Intune that don't show up clearly in Microsoft's documentation — learned the hard way so you don't have to."
---

Five parts down, and we're wrapping up the series with the stuff that rarely makes it into official docs — the actual quirks and gotchas you only learn by running into them firsthand[cite: 5]. If you've been following along from Part 1, this final piece will save you a ton of headaches down the road[cite: 5].

**Factory Reset Protection can lock you out of your own fleet**

Google's Factory Reset Protection (FRP) is fantastic anti-theft tech: if someone wipes a device without signing into the original Google account, the phone locks down hard[cite: 5]. Great for keeping thieves out, but a massive headache if you manually reset a corporate phone without realizing it's still tied to an employee's personal Google account[cite: 5]. For company-owned hardware, always trigger a remote wipe via Intune instead of doing a physical factory reset — Intune bypasses FRP properly[cite: 5]. If you *have* to reset a phone manually, make sure you manually remove that Google account from the settings *before* wiping[cite: 5].

**"Corporate-owned" isn't always as clean as it looks**

If you're picking up refurbished, secondhand, or transferred hardware, watch out: those devices might still be registered to a former owner's Zero Touch portal if the original reseller link wasn't unlinked[cite: 5]. If a supposedly fresh phone tries to enroll into a completely random tenant on its first boot, that's usually why[cite: 5]. Always double-check device history before rolling out refurbished hardware[cite: 5].

**Work profile apps can't always talk to each other — by design**

The wall between a BYOD work profile and personal profile is rock-solid[cite: 5]. That means apps expecting to cross that line (like a personal gallery app trying to attach a photo to a work email) will often fail, or require explicit user permissions[cite: 5]. This isn't a bug; it's the security boundary doing its actual job[cite: 5]. Pre-empting this in user guides helps avoid a flood of "my phone is broken" tickets[cite: 5].

**Dedicated and kiosk devices need separate screen timeout rules**

A kiosk device running a single app will still follow standard Android battery saver and display sleep timers unless you specifically override them[cite: 5]. If you don't push a device restriction policy for display timeout alongside your kiosk configuration, your check-in scanner or lobby tablet will randomly go to sleep mid-day[cite: 5]. It's an easy setting to overlook because it lives in a separate policy[cite: 5].

**The Intune Company Portal app version matters**

When Android enrollment fails mysteriously, it's often just an outdated Company Portal app rather than a bad Intune policy[cite: 5]. While Google Play usually handles background updates, restricted or sideloaded devices can end up stuck on outdated builds that break newer enrollment flows[cite: 5]. Checking the Company Portal app version is a super quick troubleshooting step before you start picking apart Conditional Access logs[cite: 5].

**Managed Google Play approval isn't instantaneous**

When you approve a new app inside Managed Google Play, there's a noticeable delay before it syncs to Intune as an assignable app, and even longer before it reaches enrolled devices[cite: 5]. That's normal background sync behavior between Microsoft and Google[cite: 5]. Don't assume your deployment broke five minutes after hitting approve — give it a little breathing room to propagate[cite: 5].

**Bulk enrollment tokens expire — keep track of them**

If you're deploying via QR codes or enrollment tokens, remember that those tokens come with an expiration date[cite: 5]. Regenerating a token midway through a rollout without updating your setup guide is a classic source of "why won't this batch enroll?" confusion[cite: 5]. Add a simple reminder line to your deployment runbook with the token's expiration date[cite: 5].

**That's a wrap!**

Across all six parts, we covered[cite: 5]:

*   Understanding management profiles and picking the right one first[cite: 5]
*   Navigating the five enrollment methods[cite: 5]
*   What the Zero Touch Portal is actually doing behind the scenes[cite: 5]
*   Deploying apps with Managed Google Play[cite: 5]
*   Designing compliance and Conditional Access rules that enforce real security[cite: 5]
*   The real-world gotchas that tie it all together[cite: 5]

If you're building out Android management in a lean IT environment, following these steps in order should save you from learning these lessons the hard way[cite: 5].

**References**

- [Google: Factory Reset Protection](https://source.android.com/docs/security/features/reset-protection)[cite: 5]
- [Microsoft Learn: Troubleshoot Android enrollment](https://learn.microsoft.com/en-us/troubleshoot/mem/intune/enroll/troubleshoot-android-enrollment-failures)[cite: 5]