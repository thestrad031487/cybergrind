---
title: "Internet Connection Types — How the Outside World Gets In"
date: 2026-05-27
author: "Logan"
section: "Orange Book"
tags:
  - networking
  - ISP
  - DSL
  - fiber
  - cable
  - cellular
  - satellite
  - VPN
  - connectivity
  - IT fundamentals
description: "Your network doesn't exist in isolation. Understanding how ISP connections work — DSL, cable, fiber, cellular, satellite, and VPNs — is fundamental for network design, reliability, and security decisions."
suggested_image: "A comparison graphic showing DSL, cable, fiber, and cellular connection types with speed and latency indicators, styled with dark background and orange accents."
---

# Internet Connection Types — How the Outside World Gets In

Your network doesn't exist in isolation. At some point, traffic has to leave your local environment and travel across infrastructure you don't own or control. Understanding how that connection is made — and what the tradeoffs are — is fundamental for anyone responsible for network design, reliability, or security.

## DSL (Digital Subscriber Line)

DSL delivers internet access over existing telephone lines. It doesn't require a separate physical connection — the same copper pair that carries voice calls also carries data, using frequency separation to prevent interference.

ADSL (Asymmetric DSL) offers higher download speeds than upload speeds, which matches typical residential usage patterns. VDSL delivers faster speeds but requires proximity to the telephone exchange. DSL performance degrades with distance — the farther you are from the DSLAM (the ISP's local equipment), the slower and less stable your connection.

## Cable

Cable internet runs over the same coaxial cable infrastructure used for cable television. It generally delivers faster speeds than DSL and is less sensitive to distance from the provider's headend.

The tradeoff is shared bandwidth. Cable is a shared medium — your connection shares capacity with neighboring subscribers. During peak usage hours, congestion can degrade performance noticeably. DOCSIS (Data Over Cable Service Interface Specification) is the standard that defines how cable internet operates, with DOCSIS 3.1 supporting multi-Gbps theoretical speeds.

## Fiber

Fiber optic internet transmits data as light pulses through glass or plastic fibers. It offers the highest speeds, lowest latency, and most symmetrical upload/download performance of any consumer or business ISP technology.

FTTH (Fiber to the Home) runs fiber directly to the premises. FTTC (Fiber to the Curb) or FTTN (Fiber to the Node) runs fiber to a neighborhood distribution point and uses copper for the last segment. The closer the fiber gets to the endpoint, the better the performance.

## Cellular and Mobile Broadband

Cellular networks provide internet access through the same infrastructure that handles mobile phone calls and data. 4G LTE became the standard for mobile broadband, delivering speeds sufficient for most applications. 5G is the current generation, offering dramatically higher theoretical speeds and much lower latency.

Mobile broadband is critical for remote workers, field technicians, and as a backup connection when primary links fail. From an IT perspective, cellular failover is increasingly used in SD-WAN deployments to maintain connectivity when wired ISP links go down.

## Satellite

Satellite internet reaches locations where no terrestrial infrastructure exists — rural areas, maritime environments, remote sites. Traditional geostationary satellite (GEO) has high latency (~600ms round trip) due to the distance signals must travel to orbit and back.

Low-earth orbit (LEO) satellite constellations like Starlink have dramatically reduced latency compared to GEO, making satellite internet viable for a much broader range of applications.

## VPNs

A VPN (Virtual Private Network) doesn't change the underlying connection type but creates an encrypted tunnel through whatever connection you're using. Site-to-site VPNs connect entire networks together over the public internet. Remote access VPNs allow individual users to connect to a corporate network securely from any location.

From a security perspective, VPNs are a critical control for remote access — but they're not a silver bullet. A compromised endpoint on a VPN is a compromised endpoint on your network.

## Thinking About Connection Strategy

For home users, the choice is largely about speed and price. For businesses, the calculus is more complex: uptime SLAs, failover options, bandwidth requirements, and the cost of downtime all factor into connection decisions.

Redundant ISP connections — preferably using different physical paths and different providers — are the baseline for business continuity in network-dependent organizations. A single internet connection is a single point of failure.

---

## References

- CableLabs. *DOCSIS 3.1 Physical Layer Specification*. https://www.cablelabs.com/specifications/CM-SP-PHYv3.1
- ITU-T G.992.1 — *Asymmetric Digital Subscriber Line (ADSL) Transceivers*. International Telecommunication Union. https://www.itu.int/rec/T-REC-G.992.1/en
- ITU-T G.9701 — *Fast Access to Subscriber Terminals (G.fast)*. International Telecommunication Union. https://www.itu.int/rec/T-REC-G.9701
- 3GPP. "5G Standards Overview." https://www.3gpp.org/technologies/5g-system-overview
- SpaceX Starlink. "How Starlink Works." https://www.starlink.com/technology
- IETF RFC 4301 — *Security Architecture for the Internet Protocol (IPsec/VPN)*. https://www.rfc-editor.org/rfc/rfc4301
- FCC. "Broadband Speed Guide." https://www.fcc.gov/consumers/guides/broadband-speed-guide
