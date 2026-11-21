---
title: "Security Skills CTF: an operator's recap with AI in the loop"
date: 2026-11-21
draft: false
featured: true
featured_label: "CTF Write-up"
author: "Jason Wacker"
section: "ctf"
tags: ["ctf", "security-skills", "writeup", "ai-assisted", "school"]
description: "Recap of the Security Skills school CTF: six categories, 30 challenges, how I ran it as the operator with an AI analyst doing the heavy parsing, and where human judgment still decided the answer."
platform: "Security Skills"
difficulty: "easy"
category: "mixed"
---

My school runs a CTF on a CTFd instance called Security Skills. There are 30 challenges across six categories, five per category, worth 25 to 125 points each, for 2,250 points total. Every flag uses the format `Professor{...}`.

I worked through 29 of them on a Saturday morning and finished at 2,125 points. The 30th, DF05, couldn't be solved. More on that below.

## How the board is built

Each category follows the same pattern. The first three challenges are warmups that teach one tool or idea: decode base64, read robots.txt, run `strings`. The last two are small investigations. You get several files, usually a log, an inventory and some evidence, and the answer comes from correlating them rather than finding a string. Those two also include deliberate decoys: a lookalike username, an approved USB drive on the same host, a second workstation pulling the same package name.

That split works well for teaching. The warmups get you comfortable with the tool, and the harder ones punish you for grabbing the first thing that looks right.

## How I ran it

I worked the board from my Windows PC, not a Kali box. The browser stayed on CTFd for reading challenges and submitting flags. Anything that needed real tooling (pcaps, ELF binaries, an encrypted backup, CSV exports of Windows logs) went to Claude, running in a Linux sandbox where it could use tshark, openssl, objdump, exiftool and Python. I gave it the challenge text and the files, it ran the analysis and reported what it found, and I decided what to submit.

I think of that as an operator and analyst split. I owned the board: which challenge to take next, what the question was really asking, which answer went in the flag box, and what to do when something didn't add up. The AI did the analyst work, and it did it much faster than I could have on a Windows machine without a Linux toolchain installed.

## Where AI helped

The warmups barely needed it. ROT13, base64 and hex are one command each, and most of the web and OSINT warmups are just reading a file.

The investigations are where it paid off:

- In NW04 and NW05 it cut the pcaps down to POST requests and per-host DNS counts, then checked them against the host inventory and the approved-destination list in one pass.
- DF04 came with four CSV exports from different log sources. It merged them into a single timeline for the suspect workstation in seconds, a job that's slow and error-prone in a spreadsheet.
- RE04 and RE05 are stripped binaries. It read the `objdump` output, explained the XOR loops and wrote the few lines of Python that decode the hidden tables, all without running either binary.
- WEB05 hides its flag three files deep. It traced the chain from the release history script to the retired admin console and showed how each file pointed to the next.

## Where the operator still mattered

Every investigation had a decoy built to catch someone who grabs the first plausible answer: a handle one letter off in OS04, an approved backup drive on the same host in DF04, a monitoring domain with a similar name in NW05. The AI sorted these out well when it had every file. But the CTF site wasn't reachable from the sandbox, so it only saw what I handed it. If I had skipped an attachment or pasted half a challenge description, it would have built a confident answer on partial evidence. Complete inputs were on me.

Flag format was the other recurring problem. A few challenges didn't say how to handle hyphens, underscores or capital letters. For CR05, DF04, NW05 and RE05 I had a primary flag and a backup version ready and let the board decide.

DF05 is the clearest case. An analyst, human or AI, can't recover a deleted note from an image that doesn't exist. Noticing the missing download button, checking the API and reporting it to the instructor was a judgment call that no amount of analysis would have made.

## The write-ups

- [Cryptography](/ctf/security-skills-ctf-cryptography/): ROT13, base64, hex, an OpenSSL-encrypted config, and a tampered update caught by SHA-256
- [Website security](/ctf/security-skills-ctf-web/): page source, robots.txt, CSS-hidden elements, client-side role checks, and a retired admin console left in a public bundle
- [Network security](/ctf/security-skills-ctf-network/): HTTP and DNS in Wireshark, an unauthorized upload, and DNS exfiltration fragments
- [Digital forensics](/ctf/security-skills-ctf-forensics/): text evidence, strings, PNG metadata, and a USB copy reconstructed from Windows event logs
- [OSINT](/ctf/security-skills-ctf-osint/): profiles, archived pages, a former employee with a lookalike handle, and a typosquatted payroll portal
- [Reverse engineering](/ctf/security-skills-ctf-reverse-engineering/): reading source, `strings` on an ELF, and two stripped binaries with XOR-masked data

## The one that couldn't be solved

DF05 (Deleted Report) asks you to recover a deleted note from a FAT disk image. The challenge pop-up had no download button. I checked the CTFd API at `/api/v1/challenges/20` and it returned `"files": []`, so the image was never uploaded. I reported it to my instructor. If a file shows up, I'll add DF05 to the forensics post.

One small lesson from that: CTFd's `/api/v1/challenges/<id>` endpoint works for regular players and is a quick way to check what a challenge is supposed to include. The `/files` sub-endpoint is admin-only and will just bounce you to the login page.

## Takeaways

The recurring theme across all six categories is that hiding something isn't the same as protecting it. Base64 isn't encryption. `display:none` isn't access control. A robots.txt `Disallow` line is a map. A role check in browser JavaScript is a suggestion. A retired admin page that still ships in the static bundle is still public. A "masked" string in a binary is one XOR away from plain text.

The harder challenges add a second theme: check your answer against more than one source. Almost every 100 and 125-point challenge had a plausible wrong answer that only one file supported.

The third theme is about the workflow. AI shortened every investigation, mostly by doing the parsing, filtering and decoding that eat the clock. It didn't change what a good answer looks like, which is one that holds up against every source you were given. Making sure all the sources were actually in front of it, reading its reasoning, and owning what went into the flag box stayed my job.
