---
title: "Best Practices & Policy Design for Android in Intune"
date: 2026-08-16
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "android", "compliance-policy", "conditional-access", "mam"]
description: "Compliance policy design for Android, when MAM beats full MDM, and the Conditional Access quirks specific to Android that Windows admins never have to think about."
---

Four parts in, you've got devices enrolled (Parts 1–3) and apps deployed (Part 4)[cite: 4]. This is where everything turns into a solid security posture rather than just a collection of working settings[cite: 4] — covering compliance policy design, how to actually choose between MAM and MDM, and the Android-specific Conditional Access quirks that love to trip up Windows admins[cite: 4].

**Compliance policy: the floor, not the ceiling**

An Android compliance policy in Intune checks core baseline conditions: minimum OS version, encryption status, root detection, PIN complexity, and threat detection[cite: 4]. But here's the thing: flagging a device as non-compliant *does absolutely nothing on its own*[cite: 4]. A compliance policy only gets teeth when you pair it with a Conditional Access policy that actively blocks non-compliant devices from company resources[cite: 4]. Unenforced compliance policies are just expensive reporting tools[cite: 4].

A few settings carry way more weight on Android than on Windows:

*   **Rooted device detection:** Rooting bypasses system controls and can compromise work profile isolation entirely[cite: 4]. Never leave this check off[cite: 4].
*   **Minimum OS version:** Android's patch landscape is notorious for vendor delays[cite: 4]. Enforcing a minimum OS version does serious heavy lifting compared to Windows, where update delivery is far more centralized[cite: 4].
*   **Google Play Protect status:** Standard baseline malware protection and a no-brainer compliance requirement[cite: 4].

**MAM vs. Full MDM — making the choice**

We know what MAM is from Part 4, but here is the rule of thumb for deciding which route to take[cite: 4]:

*   **Go with full MDM (Android Enterprise enrollment) when:** The company owns the hardware, or you need total device-level control (full wipes, strict OS updates, or kiosk locks)[cite: 4].
*   **Go with MAM alone when:** The device belongs to the employee, or you're managing temporary users like contractors, volunteers, or board members[cite: 4]. It avoids the support burden and privacy headache of managing personal hardware[cite: 4].

Defaulting to full MDM for every device just because it's familiar is a trap[cite: 4]. If you enroll a personal device when MAM would have done the job, you've taken on the burden of supporting that hardware while giving users a reason to ask, "Why does IT have so much control over my personal phone?"[cite: 4]

**Android-specific Conditional Access quirks**

A few Android behaviors operate differently from Windows and will absolutely land in your support queue if you aren't prepared[cite: 4]:

*   **App-based Conditional Access checks the app, not just device status:** You can require an "Approved client app" as a grant control[cite: 4]. Even on a fully compliant device, a user opening a non-approved mail app instead of Microsoft Outlook will get blocked[cite: 4]. It works as intended by enforcing MAM policies, but it can confuse users who assume device compliance is a blanket pass[cite: 4].
*   **Device-based and app-based policies don't automatically inherit from each other:** If you're supporting both MDM-enrolled and MAM-only users, you need distinct Conditional Access rules for both[cite: 4]. Configuring only one leaves a massive loophole for the other[cite: 4].
*   **Cellular network signals are less predictable:** Mobile data routing behaves differently than corporate Wi-Fi or standard wired connections[cite: 4]. Always test your location- or network-based Conditional Access rules on cellular connection before rolling them out[cite: 4].

**The practical takeaway**

Compliance policies without Conditional Access enforcement are pure security theater[cite: 4]. Pick MAM or MDM intentionally for each group of users, and treat Android Conditional Access testing as its own project phase instead of assuming it will act like Windows[cite: 4].

Part 6 wraps up the series with real-world tips, gotchas, and lesser-known features that you won't find in standard vendor docs[cite: 4].

**References**

- [Microsoft Learn: Android compliance policy settings](https://learn.microsoft.com/en-us/mem/intune/protect/compliance-policy-create-android)[cite: 4]
- [Microsoft Learn: Conditional Access and app protection policies](https://learn.microsoft.com/en-us/mem/intune/protect/app-based-conditional-access-intune)[cite: 4]