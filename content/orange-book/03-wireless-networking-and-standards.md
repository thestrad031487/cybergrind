---
title: "Wireless Networking & Standards — What's Actually Happening When You Connect to Wi-Fi"
date: 2026-05-27
author: "Logan"
section: "Orange Book"
tags:
  - networking
  - wireless
  - Wi-Fi
  - 802.11
  - WPA2
  - WPA3
  - WEP
  - SSID
  - security
  - IT fundamentals
description: "Wireless networking feels effortless from the user side — but underneath is a carefully engineered stack of standards, authentication mechanisms, and encryption protocols. This article breaks down 802.11, WEP/WPA/WPA2/WPA3, SSIDs, and wireless configuration in Windows."
suggested_image: "A stylized illustration of radio waves emanating from a wireless access point, with a padlock icon indicating encryption, on a dark background with orange accents."
---

# Wireless Networking & Standards — What's Actually Happening When You Connect to Wi-Fi

Wireless networking feels effortless from the user side. You click a network name, type a password, and you're online. But underneath that simplicity is a carefully engineered stack of standards, authentication mechanisms, and encryption protocols that determine whether your connection is fast, reliable, and secure.

## The 802.11 Standard Family

802.11 is the IEEE standard that defines how wireless local area networks operate. It's not a single standard but a family of amendments, each improving on the last.

**802.11b** — Released in 1999, operating in the 2.4 GHz band with speeds up to 11 Mbps. Largely historical at this point.

**802.11g** — Also 2.4 GHz, improved speeds up to 54 Mbps. Backward compatible with 802.11b.

**802.11n (Wi-Fi 4)** — Introduced MIMO (Multiple Input, Multiple Output) antenna technology and dual-band operation (2.4 GHz and 5 GHz). Speeds up to 600 Mbps.

**802.11ac (Wi-Fi 5)** — 5 GHz only, MU-MIMO, speeds up to several Gbps. The dominant standard in most enterprise and home deployments today.

**802.11ax (Wi-Fi 6)** — Improved efficiency in dense environments, OFDMA technology, better performance in high-device-count scenarios like stadiums, offices, and apartment buildings.

## Wireless Security Protocols

Security is where wireless networking has had the most painful evolution.

**WEP (Wired Equivalent Privacy)** — The original wireless security protocol. Fundamentally broken. WEP can be cracked in minutes using readily available tools. It should never be used.

**WPA (Wi-Fi Protected Access)** — Introduced as a temporary fix for WEP's vulnerabilities while a more complete solution was developed. Better, but still compromised.

**WPA2** — The current baseline standard. Uses AES encryption and is significantly more secure than its predecessors. WPA2-Personal uses a pre-shared key. WPA2-Enterprise uses 802.1X authentication against a RADIUS server, providing per-user credentials and better auditability.

**WPA3** — The newest standard, addressing weaknesses in WPA2's handshake process with Simultaneous Authentication of Equals (SAE). Adoption is growing but not yet universal.

## SSIDs and Network Discovery

The SSID (Service Set Identifier) is the name of the wireless network. By default, access points broadcast their SSID so devices can discover and connect to them. Suppressing SSID broadcast is a minor security measure — it doesn't prevent determined attackers from finding the network, but it does reduce casual exposure.

When SSID broadcast is disabled, users must manually configure the connection by entering the network name, security type, and password through their operating system's network settings.

## Configuring Wireless in Windows

In Windows, wireless connections are managed through Network & Internet Settings. When an SSID is broadcasting, it appears in the list of available networks. Selecting it and providing credentials establishes the connection.

For hidden networks, the process involves navigating to Wi-Fi > Manage Known Networks > Add a New Network and entering the SSID and security settings manually.

Device Manager is where adapter-level settings live — including the 802.11 standard support, which must match the capabilities of the access point for a connection to be established.

## Why Wireless Security Is a Frontline Issue

Wireless is often the most exposed part of a network perimeter. An attacker within radio range can attempt to authenticate without ever setting foot in your building. Understanding the standards, knowing which security protocols are acceptable, and correctly configuring your access points is basic hygiene for any IT or security professional.

If you're still seeing WPA or WEP in your environment, that's a finding — not a footnote.

---

## References

- IEEE 802.11 Working Group. *IEEE 802.11-2020: IEEE Standard for Information Technology — Wireless LAN Medium Access Control (MAC) and Physical Layer (PHY) Specifications*. IEEE, 2020. https://standards.ieee.org/ieee/802.11/7028/
- Wi-Fi Alliance. "Wi-Fi Security." https://www.wi-fi.org/discover-wi-fi/security
- Wi-Fi Alliance. "WPA3 Specification." https://www.wi-fi.org/file/wpa3-specification
- NIST Special Publication 800-97 — *Establishing Wireless Robust Security Networks: A Guide to IEEE 802.11i*. https://csrc.nist.gov/publications/detail/sp/800-97/final
- Fluhrer, Scott, Itsik Mantin, and Adi Shamir. "Weaknesses in the Key Scheduling Algorithm of RC4." *Selected Areas in Cryptography*, 2001. (Foundational WEP vulnerability research.)
- Microsoft. "Connect to a Wi-Fi network in Windows." *Microsoft Support*. https://support.microsoft.com/en-us/windows/connect-to-a-wi-fi-network-in-windows-1aad4ccb-c57b-4e40-8a0e-4c3d5432a2f9
