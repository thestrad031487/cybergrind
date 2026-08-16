---
title: "Part 4: Android App Management and Managed Google Play"
date: 2026-08-16
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "android", "managed-google-play", "app-management", "mdm"]
description: "How Managed Google Play connects to Intune, the difference between required vs. available deployments, and how app distribution works across personal and corporate profiles."
---

Once your devices are enrolled using the methods from Part 2, the next immediate job is getting the right apps onto them — and locking down the wrong ones. On Windows, you might be used to pushing `.msi` or `.win32` packages through Intune. On Android Enterprise, app management runs through a completely different pipeline: **Managed Google Play**.

**What is Managed Google Play?**

Think of Managed Google Play as your company’s private, curated version of the public Google Play Store. Instead of letting users download whatever they want from millions of apps, Managed Google Play lets you approve, deploy, and pre-configure specific applications directly from the Intune admin portal.

To make this work, you link your Microsoft Intune tenant to an enterprise Google account. Once connected, Intune syncs directly with Managed Google Play, letting you approve public apps, upload internal Line-of-Business (LOB) `.apk` files, or publish web links without ever leaving the Microsoft console.

**How Apps behave across management profiles**

How an app behaves — and whether the user even sees it — depends heavily on the profile types we covered in Part 1:

* **BYOD Work Profile:** Apps pushed through Managed Google Play land strictly inside the encrypted work container. The work store only displays approved corporate apps. The personal side of the phone keeps its normal, unmanaged Play Store, keeping personal and business app activity completely separate.
* **Corporate-Owned, Fully Managed:** The entire phone is bound to Managed Google Play. You can choose to leave the store wide open or restrict it so users can only install apps from your approved corporate catalog.
* **Corporate-Owned, Personally Enabled (COPE):** Works like BYOD for apps — corporate apps land in the work profile, while personal apps stay in the personal profile. However, you still retain top-level policy control over the entire device.
* **Dedicated (Kiosk) Devices:** Usually deployed with silent background installations for single-app or multi-app kiosk setups. Users never see the Play Store interface at all.

**Required vs. Available deployments**

When assigning apps in Intune, you have two primary deployment intents:

1. **Required:** Intune silently installs the app in the background via Managed Google Play as soon as the device checks in — no user interaction or store browsing needed. Essential for core tools like Microsoft Authenticator, Outlook, or security agents.
2. **Available:** The app doesn't install automatically. Instead, it shows up inside the Managed Google Play app store on the user's device, letting them download it on demand if they need it.

**App Configuration policies: Pre-configuring settings**

One of the biggest advantages of Managed Google Play is support for **App Configuration Policies**. Instead of asking users to type in complex server URLs, domain names, or username formats, you can push app configuration keys alongside the app payload. When the employee opens an app like Microsoft Outlook or Edge for the first time, their email address and corporate settings are already filled in.

**The Practical Takeaway**

Don't treat Managed Google Play as an afterthought. Set up your tenant binding early, define your core required apps (like authentication and email apps), and build configuration policies for them before rolling devices out to staff.

Up next in Part 5: Compliance policies, Conditional Access, and how to enforce corporate security baselines without breaking user productivity.

**References**

- [Microsoft Learn: Add Managed Google Play apps to Android Enterprise devices](https://learn.microsoft.com/en-us/intune/app-management/deployment/add-managed-google-play)
- [Microsoft Learn: Connect your Intune account to Managed Google Play](https://learn.microsoft.com/en-us/intune/device-enrollment/android/connect-managed-google-play)