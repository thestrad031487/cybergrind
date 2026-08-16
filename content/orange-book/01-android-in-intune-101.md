---
title: "Android in Intune 101: What You're Actually Managing"
date: 2026-08-16
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "android", "mdm", "android-enterprise", "endpoint-management"]
description: "Android Enterprise vs. legacy Device Admin, the four management profile types, and why picking the right one before you enroll a single device saves you months of rework."
---

If you're coming over from the Windows side of Intune, Android feels like a whole different beast on day one — because it is[cite: 1]. Windows management pretty much assumes one device, one main user, and one company owning the hardware[cite: 1]. Android, on the other hand, has to handle personal phones, shared devices, front-desk kiosks, and fully corporate-owned hardware all under the same MDM umbrella — sometimes even within the same tenant[cite: 1]. Before you start enrolling anything, you really need to map out your setup, or you'll be spending the next few months untangling enrollment decisions[cite: 1].

**Device Admin is dead — stop using it**

Google deprecated the legacy Device Administration API way back in 2022, so if you're still running it, it's probably just out of habit at this point[cite: 1]. Device Admin was pretty blunt: full-device control, zero separation between personal and company data, and fewer features with every update[cite: 1]. If you inherit a setup with Device Admin devices, put migrating them to Android Enterprise right at the top of your to-do list[cite: 1]. Both Microsoft and Google have made it crystal clear that this path is being sunset, not maintained[cite: 1].

**Android Enterprise** is the modern replacement[cite: 1]. It’s not just a single setting, but a whole framework with four distinct management profiles depending on who owns the phone and how it's being used[cite: 1]:

* **Personally-Owned Devices with Work Profile (BYOD):** The employee owns the phone[cite: 1]. Intune sets up an isolated, encrypted work container for corporate apps and data that sits alongside their personal stuff without ever touching it[cite: 1]. You can wipe the work profile cleanly without wiping their personal photos or text messages[cite: 1]. This is your go-to whenever the company isn't paying for the hardware[cite: 1].
* **Corporate-Owned, Fully Managed:** The company owns the phone, and it's strictly for work[cite: 1]. No personal profile, no separation — Intune controls the whole device just like a company laptop[cite: 1]. Perfect for corporate phones where personal use isn't allowed[cite: 1].
* **Corporate-Owned, Personally Enabled (COPE):** The hybrid option[cite: 1]. The company owns the device, but a work profile still keeps business and personal data separate[cite: 1]. You get BYOD-style data separation plus full device-level policy controls like full device wipes and extra restrictions[cite: 1]. It's usually the best fit if you give staff company phones but let them use them in their personal lives — avoiding the whole "why can IT see my photos?" awkwardness[cite: 1].
* **Corporate-Owned, Dedicated Devices:** Single-purpose, shared, or userless devices running in kiosk mode[cite: 1]. Think checkout scanners, digital signs, or front-desk check-in tablets[cite: 1]. They're locked down to one or two apps and don't require individual user sign-ins[cite: 1].

**Why this decision comes first**

Every single enrollment method, app deployment plan, and compliance policy relies on knowing which profile a device belongs to — simply because the profile dictates what you can and can't do[cite: 1]. You can't run a full-device wipe on a BYOD phone[cite: 1]. You can't leave a shared kiosk un-enrolled and hope Conditional Access handles it[cite: 1]. Getting this wrong isn't just a matter of tweaking a setting; it usually means wiping and re-enrolling the device from scratch, which turns into a massive headache across a full fleet[cite: 1].

If you're running a lean IT setup, keep it simple: inventory your Android fleet by ownership and daily use *before* jumping into Intune[cite: 1].

* Personal phones with work email → **BYOD Work Profile**[cite: 1]
* Company phones used for work and personal → **COPE**[cite: 1]
* Company phones used strictly for work → **Fully Managed**[cite: 1]
* Shared or kiosk devices → **Dedicated**[cite: 1]

Sorting this out upfront will save you from the massive rework most people learn about the hard way[cite: 1].

In Part 2, we'll dive into the actual enrollment methods — Zero Touch, QR tokens, NFC, Knox Mobile Enrollment, and Play Store setups — and match them up to these profiles[cite: 1].

**References**

- [Android Enterprise management modes overview](https://developers.google.com/android/work/overview)[cite: 1]
- [Microsoft Learn: Android Enterprise enrollment](https://learn.microsoft.com/en-us/mem/intune/enrollment/android-enterprise-overview)[cite: 1]