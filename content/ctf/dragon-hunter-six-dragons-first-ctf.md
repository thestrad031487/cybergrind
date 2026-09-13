---
title: "Dragon Hunter: Six Dragons, One First CTF"
date: 2026-09-12
author: "Jason Wacker"
section: "ctf"
platform: "Dragon Hunter (securityskills.online)"
difficulty: "medium"
category: "web"
tags: ["ctf", "web-security", "sql-injection", "ssrf", "jwt", "recon", "beginner"]
description: "A first-CTF narrative walkthrough of a six-challenge 'dragon hunt' web security course — from a forgotten HTML comment to forging a JWT signature."
draft: true
---

# **Defeating the Six Dragons: My First Web Security CTF Write-Up**

I recently wrapped up my first CTF write-up, and it was a blast. The challenge platform was called **Dragon Hunter**—a themed environment with six "dragons" of escalating difficulty, each hiding a classic web security concept behind a monster-hunting persona.  
Here’s how I tackled all six: what I looked for, what I tried, what finally clicked, and the moments where the obvious answer turned out to be a total trap.

**A quick heads-up on flags:** I’ve redacted actual flag values to [REDACTED] since this comes from coursework on a live platform other students might still be using. The real meat of a CTF write-up is the methodology, tools, and reasoning anyway!

## **The Setup**

Every challenge came with a "Dragon Record"—flavor text laying out the dragon’s habits and quirks—along with a Hunter Objective: explore the den, track down what was left behind, and recover a Professor{...} mark.

Strip away the fun fantasy skin, and it was a super clean beginner-to-advanced web security roadmap: recon, injection, server-side trust abuse, and cryptographic forgery.

## **Dragon 1 — Emberling: The Forgotten Backup**

Emberling was young and apparently terrible at housekeeping. The brief practically hit me over the head with a sign that said *check the page source*.  
I popped open dev tools, and sure enough, hanging out in an HTML comment right above the main content was:

```html  
<!-- forgotten-backup: /den/backup/emberling-hoard.zip.bak -->  
```

This isn't just a CTF trick—developers leave .bak, .old, and .zip files floating around web roots in the real world all the time. Browsers don't render HTML comments, but anyone opening View Source can read them instantly. Navigating directly to that backup archive bagged the first flag: [REDACTED].

**Takeaway:** Always check the page source before overthinking things. Comments, forgotten routes, and stray backup files are some of the oldest low-hanging fruit on the web.

## **Dragon 2 — Cinder: Don't Trust the "Keep Out" Sign**

Cinder's record noted that it "trusts instructions intended for automated visitors" and suggested looking at crawler metadata. That was a dead giveaway for robots.txt—the standard file site admins use to tell well-behaved search engine crawlers which pages to skip.

Here’s the catch: robots.txt is a *courtesy request*, not an access control wall. When a site owner puts a path under Disallow:, they are essentially handing you a custom map of everywhere they don’t want people poking around. Naturally, it’s one of the first places an attacker looks. Browsing directly to /robots.txt revealed the flag sitting right out in the open.

**Takeaway:** Files like robots.txt, sitemap.xml, and .well-known/ are standard first-pass recon targets. They're written for bots, but humans can read them just fine.

## **Dragon 3 — Vermax: Two Paths, One Truth**

Vermax was described as an old mapmaker who loved creating convincing decoy routes. The brief warned that path names hinting at "legacy," "old," or "alternate" locations were clues meant to guide you, not necessarily the actual destination.

This led me right to sitemap.xml. Unlike robots.txt (which tries to hide things), a sitemap's entire job is to advertise pages to search engines. Vermax’s sitemap had multiple routes listed, but not all of them were real. By sifting through the URLs and comparing naming patterns against the context in the brief, I separated the decoys from the real target and grabbed the flag.

**Takeaway:** Recon tools don't always hand you a single clear answer on a silver platter. Sometimes they give you a handful of plausible leads, and the real skill is using context to figure out which one is legitimate.

## **Dragon 4 — Inkscale: The Archive That Trusts Your Words Too Much**

With Inkscale, the CTF shifted from passive recon into active exploitation. The flavor text mentioned that "every question placed before the archive is recorded exactly as it was worded" and "the archive has never learned discretion."  
That’s textbook wording for a SQL Injection (SQLi) vulnerability—a backend blindly concatenation user input into database queries.

The challenge was set up like a standard login portal asking for a Designation and Scale Cipher (username and password). I dropped the classic SQLi auth-bypass payload into the username field:

```  
' OR '1'='1' --  
```

Here's how that breaks down:

> 1. The initial single quote ' breaks out of the app's intended string literal.  
> 2. The OR '1'='1' injects a condition that always evaluates to true.  
> 3. The -- tells the database to treat everything after it (the actual password check) as a comment and ignore it.

The database checked the query, saw a true condition, and logged me straight in without a valid password.

**Takeaway:** Any user input patched directly into a database query without parameterization is an injection waiting to happen. The classic single-quote bypass is ancient, but it still works out in the wild today because developers keep making the exact same concatenation mistakes.

## **Dragon 5 — Farseer: An App That Trusts Its Own Reach**

Farseer featured a "scrying" feature: feed the app a URL, and it would fetch that page *using the application server itself* and display the output back to you. This is classic Server-Side Request Forgery (SSRF)—tricking a server into acting as an unauthorized proxy for requests you can't make yourself.

The brief nudged me in the right direction: "treat the difference between what your browser can reach and what the application server can reach as part of the investigation."  
Because the app server sat inside an internal network, it had access to local services blocked off from the public internet. I pointed the scrying input at 127.0.0.1 on an internal port mentioned in the brief. Sure enough, the server fetched an internal admin panel it had access to, bringing the flag right back to my screen.

**Takeaway:** SSRF is dangerous because vulnerable servers almost always enjoy more network access than external users. An application that blindly fetches URLs on command can easily be turned into a pivot point to breach internal infrastructure.

## **Dragon 6 — Gravelock: Forging the Seal**

Gravelock, "the Warden," guarded the Warden's Seal and "trusted authority above almost everything else." This was the boss fight of the main track, built around JSON Web Tokens (JWTs).

Inspecting the session cookie revealed a standard JWT structure: a header specifying HS256 (HMAC-SHA256) encryption, and a payload with claims like rank: hunter and seal: hunter-guild. The header also included an unusual kid (Key ID) parameter, which servers use to look up which key to verify a token against.

I ran through a few initial attack vectors:

> * Brute-forcing the signing secret with a wordlist (no dice).  
> * I had a kid-parameter manipulation attack queued up as a backup option (a real, documented JWT attack class), but never needed to try it.

Finally, I tried the classic JWT flaw: changing the header algorithm to none and stripping out the signature string completely.

If a backend server doesn't explicitly restrict which algorithms it accepts, it will happily accept an unsigned token as valid. I forged a new JWT with alg: none and bumped my payload claims to rank: warden and seal: warden-seal. The server accepted it without checking for a signature, unlocking the final flag.

**Takeaway:** JWT libraries often support the none algorithm for specific, unsigned workflows. If a server relies on whatever algorithm the incoming token's header claims—rather than enforcing expected algorithms on the backend—it opens the door to total authentication bypasses.

## **Looking Back at the Arc**

Six dragons, six fundamental trust failures:

| Dragon | The Flawed Assumption |
| :---- | :---- |
| **Emberling** | Assuming that hiding text from a rendered page hides it from visitors. |
| **Cinder** | Treating a search crawler request (robots.txt) like an access control boundary. |
| **Vermax** | Assuming discovery mechanisms only list actual, valid destinations. |
| **Inkscale** | Believing user input can be safely stitched directly into raw database queries. |
| **Farseer** | Forgetting that a server's internal network access can be turned into a liability. |
| **Gravelock** | Trusting an untrusted token's own header to dictate how it should be verified. |

It was a really well-designed progression—each challenge escalated both the technical execution and the *category* of trust being exploited, moving from basic client-side assumptions up to full cryptographic forgery. It was a great reminder that most web vulnerabilities aren't super exotic—they're just ordinary assumptions made by developers who didn't expect someone to come along and test them.

There was a bonus track after these six that got *way* harder (and gave me a serious run for my money), but that’s a story for the next write-up!