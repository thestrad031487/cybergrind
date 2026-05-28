---
title: "Networked Host Services — What Lives on Your Network and Why It Matters"
date: 2026-05-27
author: "Logan"
section: "Orange Book"
tags:
  - networking
  - services
  - SMB
  - HTTP
  - HTTPS
  - email
  - SMTP
  - IMAP
  - POP3
  - SSH
  - RDP
  - SNMP
  - FTP
  - security
  - IT fundamentals
description: "A network is infrastructure. Services are what make it useful — and what make it a target. This article covers file/print services, web servers, email protocols, remote access tools, and why service awareness is a security imperative."
suggested_image: "A server rack illustration with labeled service icons (web, email, file, remote access) connected by lines, on a dark background with orange accent lighting."
---

# Networked Host Services — What Lives on Your Network and Why It Matters

A network is infrastructure. Services are what make that infrastructure useful. Understanding the services running in your environment — what they do, what protocols they use, and how they're configured — is essential for both operations and security.

## File and Print Services

Centralized file sharing is one of the oldest and most fundamental network services. Rather than copying files to USB drives or emailing attachments, file servers provide shared storage that multiple users can access simultaneously with appropriate permissions.

**SMB (Server Message Block)** is the protocol that underpins Windows file and print sharing. Modern environments run SMB3, which includes encryption, improved performance, and better resilience. SMB1 has severe, well-documented vulnerabilities (most infamously exploited by EternalBlue/WannaCry) and should be disabled in every environment.

Print servers centralize printer management, allowing multiple users to submit print jobs to shared printers without requiring point-to-point printer connections.

## Web Servers

Web servers deliver content over HTTP and HTTPS. Apache, Nginx, and Microsoft IIS are the dominant platforms. A web server listens for incoming requests on port 80 (HTTP) or port 443 (HTTPS), processes the request, and returns the appropriate content.

In enterprise environments, web servers don't just serve public-facing websites. Internal web applications, management consoles, and API endpoints all run on web server infrastructure.

## Email Services

Email is built on a stack of protocols that handle different parts of the message lifecycle.

**SMTP (Simple Mail Transfer Protocol)** handles outbound mail — sending messages from client to server and relaying between servers. Port 25 for server-to-server relay, port 587 for authenticated client submission.

**POP3 (Post Office Protocol)** allows clients to download messages from a server, typically removing them from the server after download. Port 110 (unencrypted), 995 (SSL).

**IMAP (Internet Message Access Protocol)** keeps messages on the server and synchronizes state across multiple clients. Changes made on one device are reflected everywhere. Port 143 (unencrypted), 993 (SSL). IMAP is the standard for modern email clients.

## Remote Access and Management

Remote access services allow administrators and users to connect to systems without physical access.

**SSH (Secure Shell)** provides encrypted command-line access to remote systems. Port 22. The standard for managing Linux/Unix systems and network equipment.

**RDP (Remote Desktop Protocol)** provides graphical remote desktop access to Windows systems. Port 3389. Widely used but also widely targeted by attackers — exposed RDP is consistently one of the top attack vectors in ransomware campaigns.

**SNMP (Simple Network Management Protocol)** allows monitoring systems to query network devices and servers for status information. Older SNMP versions (v1, v2c) transmit community strings in plaintext. SNMPv3 adds authentication and encryption.

## Why Service Awareness Is a Security Imperative

Every service running in your environment is an attack surface. Services with known vulnerabilities, default credentials, or excessive network exposure are the entry points attackers look for first.

Knowing what's running — and what should be running — is the starting point for hardening. If you can't enumerate the services in your environment, you can't protect them.

Run a scan. Know your inventory. Understand the protocols. That's the foundation of defensible infrastructure.

---

## References

- IETF RFC 5321 — *Simple Mail Transfer Protocol (SMTP)*. https://www.rfc-editor.org/rfc/rfc5321
- IETF RFC 1939 — *Post Office Protocol — Version 3 (POP3)*. https://www.rfc-editor.org/rfc/rfc1939
- IETF RFC 9051 — *Internet Message Access Protocol (IMAP) — Version 4rev2*. https://www.rfc-editor.org/rfc/rfc9051
- IETF RFC 4251 — *The Secure Shell (SSH) Protocol Architecture*. https://www.rfc-editor.org/rfc/rfc4251
- Microsoft. "MS-SMB2: Server Message Block (SMB) Protocol Versions 2 and 3." *Microsoft Open Specifications*. https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-smb2
- Microsoft Security Response Center. "Microsoft Security Bulletin MS17-010 — EternalBlue." https://msrc.microsoft.com/update-guide/vulnerability/CVE-2017-0144
- IETF RFC 3411 — *An Architecture for Describing Simple Network Management Protocol (SNMP) Management Frameworks*. https://www.rfc-editor.org/rfc/rfc3411
- Microsoft. "Remote Desktop Protocol." *Microsoft Documentation*. https://docs.microsoft.com/en-us/windows-server/remote/remote-desktop-services/clients/remote-desktop-protocol
