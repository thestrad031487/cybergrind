---
title: "Subnetting Explained — What It Is, Why It Matters, and How to Calculate It"
date: 2026-05-27
author: "Logan"
section: "Orange Book"
tags:
  - networking
  - subnetting
  - IPv4
  - CIDR
  - subnet mask
  - IP addressing
  - network design
  - VLSM
  - binary
  - IT fundamentals
description: "Subnetting is one of the most feared topics in networking — and one of the most useful once it clicks. This article breaks down what subnetting is, why we use it, how subnet masks work, and walks through the math step by step so you can calculate subnets with confidence."
suggested_image: "A clean diagram showing a single Class C network divided into four equal subnets, with IP ranges labeled, on a dark background with orange accent lines."
---

# Subnetting Explained — What It Is, Why It Matters, and How to Calculate It

Subnetting is one of those topics that intimidates a lot of people early in their networking journey. The math looks complicated, the terminology is dense, and it's easy to get lost before you understand why any of it matters. But here's the truth — once the logic clicks, subnetting becomes one of the most satisfying and practical skills you'll use in real-world networking.

This article walks you through what subnetting is, why we do it, how subnet masks work, and how to actually calculate subnets from scratch.

## What Is Subnetting?

Subnetting is the process of dividing a single IP network into smaller, more manageable segments called subnets.

Think of a large office building. You could give every single person in the building access to the same floor with no walls, no doors, and no separation. Traffic would be chaotic, security would be nonexistent, and troubleshooting a problem would mean sorting through noise from every device in the building simultaneously.

Or, you could divide the building into departments — floors with controlled access, separate spaces for finance, HR, engineering, and IT. That's subnetting. You take one large address space and break it into logical segments that are easier to manage, more secure, and more efficient.

## Why Do We Subnet?

There are several practical reasons subnetting exists:

**IP Address Conservation** — IPv4 gives us a finite number of addresses. Subnetting allows organizations to use address space efficiently rather than wasting entire blocks on small network segments.

**Traffic Management** — Broadcast traffic is contained within a subnet. Devices only receive broadcasts from other devices in the same subnet. Without subnetting, a broadcast from one device reaches every device on the network — which becomes a significant performance problem at scale.

**Security Segmentation** — Subnets create natural boundaries. You can apply firewall rules, access control lists, and routing policies between subnets. A compromised device in one subnet doesn't automatically have a path to devices in another.

**Organizational Clarity** — Subnets map cleanly to business units, floors, locations, or functions. When you see a device with an IP in the 10.10.20.x range and you know that range is assigned to the finance department, troubleshooting and documentation become much simpler.

## Understanding IP Addresses and Binary

Before subnetting makes sense, you need to understand that IP addresses are fundamentally binary numbers — 32 bits written as four groups of 8 bits (octets), expressed in decimal for human readability.

The IP address **192.168.1.10** in binary is:

```
11000000.10101000.00000001.00001010
```

Each octet is a value from 0 to 255 because 8 binary bits can represent 256 unique values (0–255).

The subnet mask works alongside the IP address to define which portion of the address identifies the **network** and which portion identifies the **host** within that network.

## The Subnet Mask

A subnet mask is also a 32-bit number. It's always a contiguous block of 1s followed by a contiguous block of 0s.

The 1s mark the **network portion** of the address. The 0s mark the **host portion**.

**255.255.255.0** in binary:
```
11111111.11111111.11111111.00000000
```

This is a /24 in CIDR notation — 24 bits set to 1. It means the first three octets identify the network and the last octet identifies hosts within that network.

Applied to the address 192.168.1.10 with a /24 mask:
- **Network address:** 192.168.1.0
- **Usable host range:** 192.168.1.1 – 192.168.1.254
- **Broadcast address:** 192.168.1.255
- **Total usable hosts:** 254

## CIDR Notation

CIDR (Classless Inter-Domain Routing) notation is shorthand for expressing a network and its subnet mask together. Instead of writing 192.168.1.0 with a subnet mask of 255.255.255.0, you write **192.168.1.0/24**.

The number after the slash is the **prefix length** — how many bits are set to 1 in the subnet mask.

Common prefix lengths and their masks:

| CIDR | Subnet Mask | Usable Hosts |
|------|-------------|--------------|
| /8 | 255.0.0.0 | 16,777,214 |
| /16 | 255.255.0.0 | 65,534 |
| /24 | 255.255.255.0 | 254 |
| /25 | 255.255.255.128 | 126 |
| /26 | 255.255.255.192 | 62 |
| /27 | 255.255.255.224 | 30 |
| /28 | 255.255.255.240 | 14 |
| /29 | 255.255.255.248 | 6 |
| /30 | 255.255.255.252 | 2 |

## How to Calculate Subnets

Here's the core formula you need:

**Number of subnets** = 2^(bits borrowed)

**Number of usable hosts per subnet** = 2^(host bits remaining) - 2

The minus 2 accounts for the **network address** (all host bits = 0) and the **broadcast address** (all host bits = 1), which cannot be assigned to devices.

### Worked Example: Dividing a /24 into Four Equal Subnets

**Starting network:** 192.168.1.0/24

You need 4 subnets. How many bits do you need to borrow?

2^2 = 4 — so you need to borrow **2 bits** from the host portion.

New prefix length: /24 + 2 = **/26**

New subnet mask: 255.255.255.**192**

Why 192? Because the two borrowed bits add 128 + 64 = 192 to the last octet.

**Host bits remaining:** 32 - 26 = 6 bits
**Usable hosts per subnet:** 2^6 - 2 = **62 hosts**

**The four subnets:**

| Subnet | Network Address | Usable Range | Broadcast |
|--------|----------------|--------------|-----------|
| 1 | 192.168.1.0/26 | 192.168.1.1 – .62 | 192.168.1.63 |
| 2 | 192.168.1.64/26 | 192.168.1.65 – .126 | 192.168.1.127 |
| 3 | 192.168.1.128/26 | 192.168.1.129 – .190 | 192.168.1.191 |
| 4 | 192.168.1.192/26 | 192.168.1.193 – .254 | 192.168.1.255 |

The **block size** — the increment between subnets — is always **256 minus the subnet mask value** in the relevant octet. Here: 256 - 192 = **64**. So subnets start at 0, 64, 128, and 192.

### Worked Example: How Many Subnets Can You Create?

**Starting network:** 10.0.0.0/16
**Requirement:** Create subnets with at least 500 usable hosts each.

How many host bits do you need for 500 hosts?

2^9 = 512, minus 2 = **510 usable hosts** — that works.

So you need **9 host bits**, meaning your prefix length is:

32 - 9 = **/23**

How many /23 subnets can you carve from a /16?

Bits borrowed: 23 - 16 = **7 bits**
Number of subnets: 2^7 = **128 subnets**

Each subnet has 510 usable hosts, and you get 128 of them from the original /16.

## The Block Size Shortcut

Once you know the subnet mask, calculating subnet boundaries becomes mechanical:

**Block size = 256 - subnet mask value in the interesting octet**

For a /26 (mask 255.255.255.192): 256 - 192 = **64**
Subnets: .0, .64, .128, .192

For a /27 (mask 255.255.255.224): 256 - 224 = **32**
Subnets: .0, .32, .64, .96, .128, .160, .192, .224

For a /28 (mask 255.255.255.240): 256 - 240 = **16**
Subnets: .0, .16, .32, .48, .64, .80, .96, .112, .128, .144, .160, .176, .192, .208, .224, .240

This shortcut makes it fast to identify which subnet an IP address belongs to and what its valid host range is.

## VLSM — Variable Length Subnet Masking

Real networks don't always need equal-sized subnets. A point-to-point link between two routers only needs 2 hosts (/30). A server VLAN might need 30 hosts (/27). A large office subnet might need 200 hosts (/24).

VLSM lets you allocate subnets of different sizes from the same address space — assigning exactly as much space as each segment needs rather than forcing everything into the same bucket. This is how modern networks are designed, and it's why understanding the math matters more than memorizing fixed tables.

## Putting It Together

Subnetting isn't about memorizing formulas — it's about understanding the relationship between the network bits, the host bits, and the address space you're working with. Once that relationship is clear, the calculations are just arithmetic.

Practice with a starting network, a requirement, and work through it:

1. How many subnets do you need? → Bits to borrow → New prefix length
2. How many hosts per subnet? → Host bits remaining → Usable hosts per subnet
3. What's the block size? → 256 minus the mask → Subnet boundaries

Do it enough times and it becomes second nature. That's when subnetting stops being a test topic and starts being a design tool.

---

## References

- IETF RFC 791 — *Internet Protocol (IPv4)*. https://www.rfc-editor.org/rfc/rfc791
- IETF RFC 950 — *Internet Standard Subnetting Procedure*. https://www.rfc-editor.org/rfc/rfc950 (The foundational RFC defining subnetting.)
- IETF RFC 1519 — *Classless Inter-Domain Routing (CIDR): An Address Assignment and Aggregation Strategy*. https://www.rfc-editor.org/rfc/rfc1519
- IETF RFC 1878 — *Variable Length Subnet Table For IPv4*. https://www.rfc-editor.org/rfc/rfc1878 (VLSM reference.)
- IETF RFC 4632 — *Classless Inter-Domain Routing (CIDR): The Internet Address Assignment and Aggregation Plan*. https://www.rfc-editor.org/rfc/rfc4632
- IANA. "IPv4 Address Space Registry." https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xhtml
- Cisco Systems. "IP Addressing and Subnetting for New Users." *Cisco Documentation*. https://www.cisco.com/c/en/us/support/docs/ip/routing-information-protocol-rip/13788-3.html
- Lammle, Todd. *CCNA Routing and Switching Complete Study Guide*. Sybex, 2016.
