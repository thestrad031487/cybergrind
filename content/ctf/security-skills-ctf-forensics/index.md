---
title: "Security Skills CTF: digital forensics"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["CTF", "agentic AI", "blue team", "supply chain", "Windows", "storage"]
keywords: ["security-skills", "writeup", "ai-assisted", "forensics", "metadata", "windows-event-logs", "usb"]
description: "Text evidence, strings, PNG metadata, and a USB data theft reconstructed from Security, Sysmon and removable-device logs."
platform: "Security Skills"
difficulty: "easy"
category: "forensics"
---

Five challenges, 375 points. I solved four of them for 250. The fifth never had its evidence file uploaded.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## DF01: open the evidence (25)

A five-line text file. The flag is on the `FINDING:` line.

Flag: `Professor{my_first_evidence}`

## DF02: find the text in the binary (50)

A small binary file. `strings` pulls out two readable lines, `TRAINING_DATA` and the flag.

```bash
strings -a DF02-memory.bin
```

Flag: `Professor{strings_are_useful}`

It's also worth running `strings -el`, which finds UTF-16 little-endian text. Windows memory and binaries store a lot of strings that way, and plain `strings` skips them. There weren't any in this file, but it's a good habit.

## DF03: picture properties (75)

The image just says "LOOK AT THE METADATA." The flag sits in a PNG `tEXt` chunk with the key `Description`, which never gets drawn.

```bash
strings DF03-photo.png | grep -A1 Description
exiftool DF03-photo.png
```

Flag: `Professor{metadata_matters}`

Real photos carry much more than this: GPS coordinates, device model, timestamps, editing software. It's worth checking on any image in an OSINT case.

## DF04: suspicious USB (100)

Four CSV exports from Windows hosts: Security events, Sysmon file-create events (event ID 11), a removable-device history, and recent documents. A manager thinks someone copied a restricted document to a USB drive before shift change. The flag needs the last five characters of the drive serial and the document name.

Putting all four sources on one timeline for WS-ACCT-07 (user jnguyen) tells the story:

| Time | Source | Event |
|---|---|---|
| 14:15:03 | Security 4663 | Reads `C:\Shares\Finance\atlas-budget.xlsx` (class: restricted) |
| 14:22:07 | Security 6416 | New USB device, serial AXUSB47, mounted E:, tagged `unregistered` |
| 14:24:47 | Recent docs | Opens atlas-budget.xlsx again |
| 14:25:12 | Sysmon 11 | FileCreate `E:\Exports\atlas-budget.xlsx` |
| 14:38:17 | Device history | AXUSB47 last seen |
| 14:41:02 | Security 4634 | Logoff |

The restricted file is read, an unregistered drive appears, the file is opened again, and a minute later a file with the same name is created on that drive. Then the drive is removed and the user logs off.

There are several decoys:

- ORBIT19 on WS-ACCT-03 and SAGE88 on WS-ACCT-04 are also plugged in during the window, but only public files get written to them.
- ARCH20 is an approved backup drive on the same host, but it was last seen two days earlier.
- `shift-roster.xlsx` shows up on two machines, but it's internal or public, not restricted.

The challenge warns that a single timestamp isn't enough, and it's right. Sysmon alone shows a file landing on E:, but you need the device history to know which physical drive E: was at 14:25 and the recent-documents export to know the file was restricted.

The last five characters of AXUSB47 are `USB47`.

Flag: `Professor{USB47_atlas_budget}`

## DF05: deleted report (125)

This one asks you to recover a deleted Board Review note from a FAT disk image. The challenge had no download link, and the CTFd API confirmed it:

```
GET /api/v1/challenges/20
"files": []
```

The image was never uploaded, which explains why nobody on the board has solved it. I've reported it. If the file turns up, the plan is The Sleuth Kit: `fls -r -d` to list deleted entries, pick the Board Review note over the obsolete decoy, then `icat` to pull the contents by inode.

## Operator notes

DF04 is where the AI did the most useful work of the whole CTF. Four CSV exports with different field names and timestamp styles, several hosts, several drives. It merged them into the timeline above and listed every decoy with the reason it didn't fit. Done in a spreadsheet, that would have taken a lot longer and been easy to get wrong. The challenge didn't specify the case of the serial fragment, so `Professor{usb47_atlas_budget}` was the backup.

DF05 is the other side of it. There was nothing to analyze, and the right move was to confirm that through the API and tell the instructor instead of digging for an answer that wasn't there.

## What this section teaches

The warmups teach you to look at a file in more than one way: as text, as bytes, as metadata. DF04 is the one I'd point a new analyst at. No single log answers the question, and every log has an entry that's close enough to send you the wrong way.
