---
title: "Security Skills CTF: OSINT"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["ctf", "security-skills", "writeup", "ai-assisted", "osint", "certificate-transparency", "typosquatting"]
description: "Profiles, linked pages, archived snapshots, a former employee hidden behind a lookalike handle, and a typosquatted payroll login found through CT logs and passive DNS."
platform: "Security Skills"
difficulty: "easy"
category: "osint"
---

Five challenges, 375 points. Everything is an offline snapshot of a made-up organization, so there's no live searching. The harder two are about correlating sources and not falling for names that are one character off.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## OS01: meet the researcher (25)

A profile page for a fictional researcher named Jordan. The flag is on the `Training Flag:` line.

Flag: `Professor{public_profile_found}`

The bio also lists a favorite animal (sea turtle). It isn't used here, but details like that are exactly what ends up in security questions and password guesses.

## OS02: follow the about link (50)

A two-page site. `index.html` links to `about.html`, and the flag is on that page.

Flag: `Professor{follow_the_link}`

On real targets, About, Team and Contact pages are where you find names, roles and email formats.

## OS03: the old announcement (75)

`current.html` and `archive-2024.html`. The flag was removed from the current page but is still in the 2024 snapshot.

Flag: `Professor{old_pages_keep_clues}`

The live-site version of this is the Wayback Machine. Pages get cleaned up, but old copies of them stick around.

## OS04: forgotten employee (100)

A firm can't tell which retired project belonged to a former researcher. You get two staff profiles, an announcement archive, a project register, a 2024 meetup program and a source register. The flag is the project codename and its original launch quarter, not its retirement date.

Two people have nearly the same handle:

- Mara Vale, Research Analyst from 2022 to 2025, handle `mvale`
- Miles Vail, Product Designer from 2023 to now, handle `mvail`

The source register even labels Miles as an "unrelated similar name." He's the current employee and owns ORBIT and GLASSWING. The former employee is Mara.

The project register and the announcement archive both list LANTERN with maintainer `mvale`, retired in October 2025. That's the retirement date the challenge tells you to ignore.

The launch date comes from the meetup program:

```
May 2024: "Shipping LANTERN: opening the first research reporting beta"
(speaker: mvale); launched earlier that quarter
```

May is in Q2, so LANTERN launched in Q2 2024.

Flag: `Professor{lantern_q22024}`

The challenge has two traps: a handle one letter off and a date that's easy to grab. Building a short timeline per handle avoids both.

## OS05: lookalike portal (125)

A payroll company thinks someone stood up a fake login page. You get the official domain list, website snapshots, a certificate transparency export and passive DNS. The flag is the suspicious hostname and its IP.

The official domains are `mariner-payroll.test`, `mariner-help.test`, `mariner-status.test` and `mariner-careers.test`. Two observed hostnames aren't on that list:

| Hostname | Title | Login form | Branding | IP |
|---|---|---|---|---|
| mariner-payr0ll.test | Mariner Payroll, Sign in | yes | copied official mark | 203.0.113.63 |
| mariner-payroll-training.test | Mariner Academy Sandbox | no | training mark | 198.51.100.91 |

The training site isn't on the approved list either, but it has no login form, uses its own branding and is labeled as an internal workshop page. It's unapproved, but it isn't pretending to be anything.

`mariner-payr0ll.test` swaps the "o" in payroll for a zero, copies the official title and brand mark, and has a login form. The CT log shows its certificate issued on October 31 at 11:22 UTC, and passive DNS resolves it to 203.0.113.63 at 11:31, nine minutes later. Every official domain lives in 192.0.2.x.

Flag: `Professor{mariner-payr0ll_203-0-113-63}`

Register a lookalike, get a certificate, point DNS at it and go live: that sequence is how a lot of credential phishing starts. Watching CT logs for your brand name is one of the cheapest early warnings you can set up.

## Operator notes

OSINT is mostly reading, and an AI reads fast. For OS04 it pulled every mention of both handles across five documents and kept them separate, which is what gets you past the mvale/mvail trap. For OS05 it compared each observed hostname with the official list and lined up the certificate issue time against the passive DNS record.

On a real case I'd still read the key source line myself before reporting. In OS04 the launch quarter rests on one phrase in the meetup program, "launched earlier that quarter," and that kind of wording is easy to misread.

## What this section teaches

OSINT is mostly reading carefully and keeping notes per entity. In both harder challenges, the wrong answer is one character or one date away from the right one.
