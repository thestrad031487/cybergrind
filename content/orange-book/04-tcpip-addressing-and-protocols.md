---
title: "TCP/IP Addressing & Protocols — The Language of the Internet"
date: 2026-05-27
author: "Logan"
section: "Orange Book"
tags:
  - networking
  - TCP/IP
  - IPv4
  - IPv6
  - DNS
  - DHCP
  - protocols
  - ports
  - OSI model
  - IT fundamentals
description: "Everything that happens on a network depends on TCP/IP. This article breaks down IP addressing, subnetting, TCP vs UDP, common ports and protocols, DNS, and DHCP — the foundational knowledge that separates users from builders."
suggested_image: "A clean reference table of common ports and protocols on a dark background, with orange header accents and a subtle network diagram in the background."
---

# TCP/IP Addressing & Protocols — The Language of the Internet

Everything that happens on a network — every webpage loaded, every email sent, every video streamed — depends on TCP/IP. It's not just a protocol. It's the foundational language that makes networked communication possible. Understanding it deeply separates people who can use networks from people who can build, secure, and troubleshoot them.

## IP Addressing

Every device on a network needs an IP address to send and receive data. IP addresses exist at Layer 3 of the OSI model and are used by routers to make forwarding decisions.

**IPv4** uses a 32-bit address space, expressed as four octets separated by dots (e.g., 192.168.1.10). This gives us roughly 4.3 billion unique addresses — a number that seemed enormous in the early days of the internet and proved insufficient as connected devices exploded.

The subnet mask defines which portion of the address identifies the network and which identifies the host. A /24 subnet mask (255.255.255.0) means the first three octets are the network and the last octet identifies individual hosts within that network.

**IPv6** uses a 128-bit address space, expressed in hexadecimal notation. This provides an astronomically larger address pool and is increasingly deployed alongside IPv4 in dual-stack configurations.

## TCP vs. UDP

Both TCP (Transmission Control Protocol) and UDP (User Datagram Protocol) operate at Layer 4 and are responsible for how data is delivered between applications.

**TCP** is connection-oriented. Before data transfers, a three-way handshake establishes the connection (SYN, SYN-ACK, ACK). TCP guarantees delivery, handles retransmission of lost packets, and ensures data arrives in order. This reliability comes at a cost — overhead. TCP is used where accuracy matters: web browsing (HTTP/HTTPS), email (SMTP), file transfers (FTP).

**UDP** is connectionless. It fires packets at the destination without establishing a session or confirming delivery. There's no retransmission, no ordering guarantee. This makes it faster and more efficient for applications where speed matters more than perfection: video streaming, VoIP, DNS queries, online gaming.

## Common Ports and Protocols

Ports are the logical endpoints that identify which application should receive incoming traffic. The combination of an IP address and a port number uniquely identifies a communication endpoint.

| Protocol | Port | Use |
|----------|------|-----|
| HTTP | 80 | Web traffic (unencrypted) |
| HTTPS | 443 | Web traffic (encrypted) |
| FTP | 20/21 | File transfer |
| SSH | 22 | Secure remote access |
| DNS | 53 | Domain name resolution |
| DHCP | 67/68 | Automatic IP assignment |
| SMTP | 25 | Email sending |
| POP3 | 110 | Email retrieval |
| IMAP | 143 | Email retrieval (synchronized) |
| SMB | 445 | Windows file sharing |
| RDP | 3389 | Remote desktop |

## DNS and DHCP

**DNS (Domain Name System)** translates human-readable domain names (cybergrind.org) into IP addresses that routers can use. Without DNS, you'd need to memorize the IP address of every website you visit.

**DHCP (Dynamic Host Configuration Protocol)** automatically assigns IP addresses, subnet masks, default gateways, and DNS server addresses to devices when they join a network. Without DHCP, every device would need manual IP configuration — manageable for a handful of devices, impractical for an enterprise.

## Why This Is the Foundation

When something breaks on a network, TCP/IP knowledge is what drives the diagnostic process. Can the host reach its default gateway? Can it resolve DNS? Is traffic being blocked on a specific port? Each question maps directly to a layer of the TCP/IP stack.

For security professionals, this knowledge is equally essential. Port scanning, traffic analysis, firewall rule creation, and intrusion detection all require a solid understanding of how IP addressing and protocols actually work.

You can't secure what you don't understand.

---

## References

- IETF RFC 791 — *Internet Protocol (IPv4)*. https://www.rfc-editor.org/rfc/rfc791
- IETF RFC 8200 — *Internet Protocol, Version 6 (IPv6) Specification*. https://www.rfc-editor.org/rfc/rfc8200
- IETF RFC 793 — *Transmission Control Protocol (TCP)*. https://www.rfc-editor.org/rfc/rfc793
- IETF RFC 768 — *User Datagram Protocol (UDP)*. https://www.rfc-editor.org/rfc/rfc768
- IETF RFC 1035 — *Domain Names — Implementation and Specification (DNS)*. https://www.rfc-editor.org/rfc/rfc1035
- IETF RFC 2131 — *Dynamic Host Configuration Protocol (DHCP)*. https://www.rfc-editor.org/rfc/rfc2131
- IANA. "Service Name and Transport Protocol Port Number Registry." https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml
- Tanenbaum, Andrew S., and David J. Wetherall. *Computer Networks*, 5th ed. Prentice Hall, 2010.
