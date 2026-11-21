---
title: "I took apart a discontinued malware cleaner, then built my own"
date: 2026-11-15
author: "Jason Wacker"
section: "orange-book"
tags: ["reverse engineering", "Python", "blue team", "homelab"]
keywords: ["malware analysis", "wazuh", "nsrl", "cybergrind-scanner"]
description: "Reversing Sophos Scan & Clean in an isolated VM, turning what I learned into a property-based scanner, wiring it into Wazuh, and building a 432-million-hash NSRL allowlist without killing a USB enclosure."
draft: false
---

Sophos Scan & Clean was a free second-opinion scanner. You ran it next to your
regular antivirus, it looked at everything on the disk, and it told you what
the other product missed. Sophos has since discontinued it. I'd used it on
enough machines over the years that I wanted to know how it actually made its
calls. What did it look at? How did it decide a file was bad? How did it get
rid of things that fought back?

So I took it apart. Then I used what I learned to build my own scanner, and
over the last few weeks that scanner went from a script on my laptop to
something that runs on my home server, reports into Wazuh, and checks files
against 432 million known-good hashes from NIST.

This post covers the whole path. It's long, so there are diagrams.

## Ground rules for the reversing

This was for learning. Everything happened inside an isolated Kali VM on my
Proxmox host, used from the command line only, with Ghidra and the
[REA](https://github.com/morluto/rea) tool for the heavy lifting. I'm not
publishing any of Sophos's code, keys or data files here, only the design I
could see from the outside of the binaries and how it worked.

## What was inside

The first surprise came early. Scan & Clean is HitmanPro 3.5 underneath. Sophos
bought SurfRight, the company behind HitmanPro, back in 2015.

The part I found most interesting was how it decides. It doesn't run a check
and immediately call a file malicious. Each check sets a property bit on the
file instead, one bit per thing it noticed. Only after all the checks are done
does it collapse those bits into a single verdict, using a fixed priority
order:

Malware > Suspicious > EWS > PUP > Cookie > Repair

The highest bit that's set wins. A file with both a PUP bit and a Suspicious
bit is Suspicious. A file with a Malware bit is Malware, whatever else is set.

![How Scan & Clean decides](/images/cybergrind-scanner/scan-and-clean-model.svg)

A few other things stood out:

- The scoring weights aren't in the code. They come from cloud lookups and a
  7 MB encrypted data blob, so the vendor can retune detection without
  shipping a new binary.
- It reads files with raw NTFS and FAT32 parsing, not the normal Windows file
  API. If a rootkit is hooking the file API to hide itself, raw reads go
  around it.
- Removal is its own machine: a service called Crusader, kernel drivers,
  BootDelete for files that are locked while Windows is running, and 19
  separate repair modules for putting things back the way they were.

## What I took from it

The design idea I liked most was keeping observation separate from judgment.
The checks only say "I saw this." A separate, simple rule decides what it
means. That makes each check easy to write and test, and the verdict logic is
small enough to reason about in one sitting.

I also liked that the priority order protects the worst case. Nothing lower on
the ladder can talk a Malware finding down.

## Building cybergrind-scanner

cybergrind-scanner is a Python command-line tool for Linux, built around that
same model. Every check returns properties, and each property has a name and a
weight. The verdict is the highest weight on the file.

There are four checks right now:

- YARA rules, where the rule's own metadata sets the weight it reports.
- A SHA-256 lookup against MalwareBazaar for known malware samples.
- TLSH fuzzy hashing, which compares a file's similarity digest against
  known-bad digests. A close match comes back as Suspicious, because "looks a
  lot like malware" isn't the same as "is malware."
- An allowlist of known-good hashes stored in Bloom filters. A hit reports
  Clean.

![cybergrind-scanner pipeline](/images/cybergrind-scanner/cgscan-pipeline.svg)

The allowlist is where I copied Scan & Clean's protective rule directly. A
known-good hit can downgrade a PUP or Suspicious finding to Clean. It can never
hide a Malware finding. If a YARA rule or MalwareBazaar says a file is
malware, a hash match against a list of "known software" doesn't get to
overrule that.

The output is JSON with a summary block, plus an exit code that maps to the
verdict: 0 for Clean, 10 for PUP, 20 for Suspicious, 30 for Malware, 2 for
an error. That made it easy to drive from other tools, which mattered for the
next step.

Some housekeeping I'd recommend for any small tool like this: the MalwareBazaar
API key lives in a `.env` file that git ignores, the repo is clean under
gitleaks, and there's a pytest suite (34 tests at the moment).

## Putting it to work in Wazuh

My home server already runs a Wazuh agent, so the scanner went there first. I
split the work by how noisy a folder is.

Quiet folders get scanned in real time. These are places where a new file
showing up is worth a look: `/tmp`, `/var/tmp`, `/dev/shm` and my Downloads
folder. Wazuh's file integrity monitoring sees the new file, and an active
response wrapper scans just that file.

The busy folders are a different story. The server runs self-hosted GitHub
Actions runners, and their `_work` folders churn through thousands of files a
day. Scanning each one in real time would mean thousands of MalwareBazaar
lookups. Those get a nightly sweep instead. A systemd timer runs a small
script that finds files changed in the last 25 hours, caps the list at 2,000,
and hands it to one scanner process with `--files-from`. The 25-hour window
overlaps a little, so a timer that fires late doesn't leave a gap.

![Wazuh integration](/images/cybergrind-scanner/wazuh-integration.svg)

Both paths run the scanner as an unprivileged `cgscan` user and write to the
same JSON log. The Wazuh agent ships that log to the manager, where custom
rules alert on findings and errors and on the nightly summary. Two more
weekly timers keep it current: one refreshes the YARA rules from YARA Forge's core
set, and the other rebuilds the server's own local allowlist.

## The allowlist problem

An allowlist is only as good as what's in it. My first one was built from the
binaries on my own laptop, which was enough to prove the code worked and not
much else.

The obvious source for something bigger is NIST's National Software Reference
Library. The RDS "modern minimal" set is a list of hashes for software NIST
has collected, and it's free. There was a prebuilt NSRL Bloom filter floating
around from another project, but it's keyed on SHA-1, and my scanner works in
SHA-256, so that was out. I had to build my own.

The size is the hard part. The download is an 18.8 GB zip, and it extracts to
about 170 GB of SQLite. My first attempt used an external NVMe drive in a
cheap USB-C enclosure. Partway through the extraction, the enclosure dropped
off the bus. The drive itself was fine and its temperature was fine. The USB
bridge couldn't handle that much sustained writing.

The fix was to stop using the laptop at all. I built it in a throwaway Debian
container on my Proxmox host, with a 240 GB thin disk on the internal NVMe.
The download and the build each ran as a systemd unit inside the container,
so I could close my SSH session and come back later. The build script waited
for the download, checked every CRC in the zip before trusting it, extracted,
deleted the zip, then streamed the SHA-256 column out of the database one row
at a time into the Bloom filter.

![NSRL build](/images/cybergrind-scanner/nsrl-build.svg)

The numbers, for anyone planning the same thing:

| | |
|---|---|
| Hashes | 432,866,777 |
| Bloom filter | 1.56 GB at a 1-in-a-million false-positive rate |
| Build | 1 hour 13 minutes of CPU on 4 cores |
| Peak memory | 5.8 GB |
| Peak disk | about 190 GB |

I'd started the container with 4 GB of RAM and bumped it to 6 GB before the
build. Given the 5.8 GB peak, that was the right call.

The finished file went to my laptop, to the server, and to a backup disk,
each copy checked against the build's SHA-256. Then I deleted the container.

## The 3 GB surprise

With the new bloom on the laptop, I measured a load before shipping it to the
server. It loaded in under a second. It also took 3 GB of memory.

My Bloom filter class read the whole file into memory and then copied it into
a second buffer, so for a moment it held two copies. On the laptop that's
annoying. On the server it would have been a real problem, because the
real-time path starts a fresh scanner process for every file event, and each
one would have grabbed 3 GB.

The fix was to memory-map the file read-only instead. The OS then only pulls
in the pages a lookup actually touches, and checking one hash touches about
20 bits scattered through the file. Peak memory dropped from 2,999 MB to 32
MB on the laptop and 28 MB on the server, and the load time went from 0.64
seconds to 0.09.

While I was in there I fixed a second gap. NSRL covers a lot of Windows and
macOS software but few of the packages a Linux distribution builds itself. My
laptop's `/usr/bin/ls` isn't in NSRL. The server's isn't either. So the
scanner now loads every allowlist it's given and checks them all: NSRL, plus
the machine's own local list. On the server,
`/usr/bin/ls` now comes back as known-good from the local list.

One caution about NSRL: some well-known hacking tools are in it, because NSRL
records software that exists, not software that's safe. A hit means "known,"
not "harmless." That's the other reason the allowlist can't override a
Malware verdict.

## Where it goes next

Right now cybergrind-scanner finds things. It doesn't clean anything up, and it
doesn't run on Windows, which is where most infected machines are. The plan
is to turn it into something I can use on my own machines and on family
computers, and to put it on GitHub once it's in shape.

Roughly in order:

1. Scan a Windows drive offline from a bootable Linux USB. Malware can't hide
   or defend itself when Windows isn't running, which is the same idea behind
   Scan & Clean's raw disk reads.
2. Quarantine before delete. Flagged files go into an encrypted archive with a
   record of where they came from, so a false positive can be put back.
3. Find persistence. Most infections come back through autoruns: Run keys,
   services, scheduled tasks and startup folders. Those can be read from the
   offline registry hives.
4. A readable report of what was found, what was quarantined and what changed.
5. Open-source the repo: license, bring-your-own MalwareBazaar key, and a
   secret scan of the full git history, not just the current files.
6. A local web front end on top of the CLI.

The repo is private until step 5. I'll write up each piece as it lands.

## References

- Ghidra: <https://ghidra-sre.org/>
- REA: <https://github.com/morluto/rea>
- NIST National Software Reference Library: <https://www.nist.gov/itl/ssd/software-quality-group/national-software-reference-library-nsrl>
- MalwareBazaar API: <https://bazaar.abuse.ch/api/>
- YARA: <https://virustotal.github.io/yara/>
- YARA Forge: <https://github.com/YARAHQ/yara-forge>
- TLSH: <https://github.com/trendmicro/tlsh>
- Wazuh active response: <https://documentation.wazuh.com/current/user-manual/capabilities/active-response/index.html>
