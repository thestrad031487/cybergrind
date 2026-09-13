---
title: "Dragon Hunter: The Bonus Track That Didn't Finish (And Why That's Okay)"
date: 2026-09-13
author: "Jason Wacker"
section: "ctf"
platform: "Dragon Hunter (securityskills.online)"
difficulty: "hard"
category: "reversing"
tags: ["ctf", "reverse-engineering", "malware-analysis", "network-security", "opsec", "cryptography"]
description: "The story of a two-part bonus CTF track that turned into a full reverse-engineering detour — and the judgment calls, dead ends, and honest stopping point along the way."
draft: true
---

# **The Bonus Track: Lab Builds, Ethical Pauses, and the Flag I Didn't Get**

Part one of this series covered the six base challenges of the **Dragon Hunter** CTF—six web security lessons, each solved cleanly, each with a neat "here’s what I found" ending.

This post is different. It’s about a two-challenge bonus track that turned into hours of building an isolated analysis lab, a moment where I had to stop and decide whether I should even be connecting to a target, and an ending where I didn't actually get the flag.

I think that’s worth writing up anyway. Not every security investigation ends with a clean win, and how you handle the parts that stall out is usually way more interesting to read about than another "and then I popped the shell" post.

*(Quick note on details: Specific IPs, exact binary hashes, and full protocol strings are generalized or left out below. This is partly because the platform may still be live for other students, and partly because one specific detail turned out to belong to an actual person's home network—which definitely doesn't belong in a public write-up!)*

## **When the Format Changes, the Risk Calculus Changes**

The first six challenges all followed the same rhythm: inspect a webpage, spot a vulnerability, get the flag.

Challenge seven, **"Synister the Demonic,"** broke that pattern instantly. Instead of a web interface, it asked me to download and run an executable "client." The flavor text took a sharp turn too—moving away from the lighter "clumsy young dragon" tone into dramatic, urgent language about threat and inevitability.

That combination—a sudden format shift plus high-pressure wording—is worth pausing on no matter the context. It’s the exact shape a lot of real-world malware delivery takes: create a sense of urgency, then get the user to execute an unknown file.

Before touching anything, I treated the download the way I’d treat any unknown executable in the wild: **don't run it, characterize it first.**

## **Building an Isolated Analysis Lab (The Hard Way)**

Setting up a safe sandbox ended up taking more time than the actual challenge, mostly thanks to classic real-world virtualization headaches.

The plan was simple: set up an isolated VirtualBox VM with no network access beyond what was strictly necessary, taking snapshots at every stage so any mistake was one click from undone. Getting there took a few detours:

> * **VirtualBox Host-Only Networking:** VirtualBox threw misleading "invalid settings" errors until I manually created a host network first under Host Network Manager before trying to attach the VM.  
> * **Fighting Windows Defender:** Modern Windows *really* doesn't want you disabling Defender, even with admin rights and Tamper Protection turned off. Registry keys I tweaked kept silently reappearing after reboots—a telltale sign that self-healing mechanisms were actively reverting my changes. (I actually tried Safe Mode too, and even that didn't make the registry change stick. In the end the real fix was pragmatic, not clean: after rebuilding on a properly-versioned Windows image, I just let the FLARE-VM installer run despite the failed Defender pre-check, and it completed fine anyway.)  
> * **Grabbing a Clean Windows ISO:** After Microsoft shifted its evaluation center options, I used **UUP dump** to build an ISO. It pulls installation files live from Microsoft's own CDN, which is infinitely safer than downloading a pre-baked, third-party Windows ISO off a random file-sharing site.  
> * **FLARE-VM Alerts:** Once Mandiant’s FLARE-VM environment finally finished installing, Defender flagged a dozen files. A quick check confirmed these were just standard offensive security tools and teaching binaries (like the samples from *Practical Malware Analysis*). Defender was just doing its job on files built to look suspicious.

> 

## **The File Wasn't Even for Windows**

After spending all that time prepping a Windows environment, I ran a basic header check on the downloaded file: 7F 45 4C 46—ELF magic bytes.

It was a Linux binary the whole time.

All the Windows lab setup was technically unnecessary for this specific file (though non-wasted, since tools like IDA Free handle ELF binaries just fine and the lab is ready for the next project). Switching over to a Kali VM, static analysis revealed a statically-linked Go binary with no plain-text flag strings.

It did, however, show a clear behavior: on launch, it attempted to connect out to a hardcoded IP address and port using a 32-byte XOR-keyed handshake. Tracking the disassembler output showed a loop XORing a stack buffer against an embedded 32-byte key string.

## **The Ethical Pause**

Before letting the binary connect to an external server, I ran a quick sanity check on the destination IP.

A reverse DNS lookup resolved to something like [hostname].wireless.static.[isp].net—a residential wireless connection, not standard cloud server infrastructure. A quick port check timed out instead of refusing the connection, which is classic behavior for an unconfigured home router firewall.

That’s a critical line to notice. Legitimate CTF infrastructure almost always runs on dedicated cloud hosting. While home-hosted challenges certainly exist, probing an address that appears to belong to an uninvolved person's residential ISP is an easy way to cross a line.

I stopped right there, paused the challenge, and reached out to my instructor to confirm the target was intentional.

It turned out to be completely sanctioned. The residential endpoint was just the self-hosted setup used by the instructor for the advanced track.

Even knowing that now, pausing was still the right call. Taking a second to verify a target before firing packets at it—especially under the social pressure of "just finish the challenge"—is a muscle worth building.

## **Reading Obfuscated Code Without Executing It**

The eighth challenge, **"Hallow the Empty,"** provided a Python source file that was heavily obfuscated:

> * Identifiers hidden inside integer arrays.  
> * Encrypted string fragments shuffled out of order.  
> * A keyed-hash decryption routine designed to unpack a payload and immediately pass it to an exec() call.

This is structurally identical to how real-world malicious droppers hide payloads from static analysis and antivirus scanners.

Instead of running the script directly, I opened the source file and modified the ending:

```python  
# Swapped out the execution trigger:  
# exec(decrypted_payload)

# Replaced with a safe inspection output:  
print(decrypted_payload)  
with open("unpacked_payload.py", "w") as f:  
    f.write(decrypted_payload)  
```

By letting the data transformation math run (decoding, deriving the key, XORing, and decompressing) while stripping the exec() function, I safely unpacked the code.  
The payload revealed a Flask web application implementing a stored-XSS-to-credential-theft challenge—gated behind Ed25519 signature verification tied to tokens issued by the Synister binary from challenge seven.

## **The Puzzle I Didn't Crack**

The Synister binary turned out to be a client for an interactive cryptographic protocol. Connecting to it dropped me into a menu to create, bind, temper, seal, and "ascend" custom access tokens.

I started testing the protocol mechanics systematically:

> 1. **Binding:** I could cleanly bind a token to a specific resource and capability, generating a validly signed token.  
> 2. **Authority Caps:** The authority level on that token capped out at a hard ceiling, regardless of how many times I ran it through the seal/ascend loop.  
> 3. **Bloodlines:** Looking through the error strings showed higher-privilege capability names existed in the system, but attempting to request them returned errors stating they belonged to a different "bloodline."  
> 4. **The Gate:** The Flask app from challenge eight explicitly required a much higher authority level than anything my token could generate.

I spotted a promising lead late in the game—a piece of platform text referenced "the Warden's Seal" as the true authority marker, which tied back suspiciously well to the Gravelock challenge from the main track. But before I could test token forgery against that specific claim, the 48-hour hosting window expired and the lab infrastructure went offline.

## **Final Thoughts**

> * **Base Track:** 6 / 6 challenges completed.  
> * **Bonus Track:** 0 / 2 flags recovered.

Even without the final flags, I consider this bonus track a win. The real takeaway from an exercise like this isn't just accumulating points—it's building out a clean analysis environment, recognizing when to stop and verify a target, and safely unpacking obfuscated code without giving it execution rights.

If the infrastructure opens back up, I’ve got my next hypothesis ready to test. Until then, the hunt is paused!