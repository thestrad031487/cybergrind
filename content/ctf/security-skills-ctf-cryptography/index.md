---
title: "Security Skills CTF: cryptography"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["CTF", "agentic AI", "cryptography"]
keywords: ["security-skills", "writeup", "ai-assisted", "openssl", "hashing"]
description: "ROT13, base64 and hex warmups, an OpenSSL AES-256-CBC config picked out of a job log, and a tampered package found with sha256sum."
platform: "Security Skills"
difficulty: "easy"
category: "crypto"
---

Five challenges, 375 points. The first three are encodings, not encryption, and the challenge text says so. The last two are closer to real incident work.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## CR01: rot13 warmup (25)

One encoded line: `Cebsrffbe{ebg13_vf_fvzcyr}`. ROT13 shifts each letter 13 places, so running it again undoes it.

```bash
tr 'A-Za-z' 'N-ZA-Mn-za-m' < CR01-rot13.txt
```

Flag: `Professor{rot13_is_simple}`

Once you know every flag starts with `Professor{`, you can spot the encoded version of that prefix in the later challenges too. In ROT13 it's `Cebsrffbe{`.

## CR02: base64 warmup (50)

`UHJvZmVzc29ye2Jhc2U2NF9pc19lYXN5fQ==`. The `==` padding and the `UHJvZmVzc29y` prefix (base64 for `Professor`) give it away.

```bash
echo 'UHJvZmVzc29ye2Jhc2U2NF9pc19lYXN5fQ==' | base64 -d
```

Flag: `Professor{base64_is_easy}`

## CR03: hex warmup (75)

`50726f666573736f727b...`. Each pair of hex characters is one byte. `50` is `P`, `7b` is `{`.

```bash
echo '50726f666573736f727b6865785f746f5f746578747d' | xxd -r -p
```

Flag: `Professor{hex_to_text}`

## CR04: encrypted config (100)

This one hands you an encrypted backup, a backup job log, and a maintenance handoff note listing three passwords. The task is to pick the right password and decrypt with AES-256-CBC and PBKDF2.

The file starts with `Salted__`, which is the header `openssl enc` writes, so the tool was obvious. The real work is in the two text files.

The job log shows three jobs, and only one of them wrote `config-backup.enc`:

```
job=BK-771 target=config-archive      mode=aes-256-cbc
job=BK-773 target=config-backup.enc   result=encrypted
job=BK-774 target=network-export      mode=plaintext
```

The handoff note ties BK-773 to `freight-lantern-26`. The other two passwords are decoys. One belongs to BK-771, which encrypted a different file, and the other is a staging credential the note explicitly says not to confuse with the backup passwords.

```bash
openssl enc -d -aes-256-cbc -pbkdf2 -in config-backup.enc -pass pass:freight-lantern-26
```

The output is JSON with `"site_code": "WEST2"` and `"config_id": "CFG73"`. The challenge wants them in lowercase, joined with an underscore.

Flag: `Professor{west2_cfg73}`

Putting a password on the command line is fine for a training value. For anything real, use `-pass stdin` and read it in with `read -s` so it stays out of your shell history and the process list.

## CR05: tampered update (125)

Three package files, a trusted SHA-256 manifest, a deployment log and a triage note. One package doesn't match the manifest. You need its name and the release version that was actually staged on the affected machine.

The hash check finds the bad file right away:

```bash
sha256sum -c trusted_release_manifest.sha256
```

```
audit-client.pkg: OK
report-agent.pkg: FAILED
printer-helper.pkg: OK
```

The version is where the decoy sits. The deployment log mentions `report-agent.pkg` twice:

```
WS-OPS-09 stage report-agent.pkg release=2.4.1 succeeded
WS-OPS-09 integrity-alert staging-cache inconsistency detected
WS-OPS-11 report-agent.pkg release=2.3.9 download skipped (old cache)
```

The triage note says WS-OPS-09 is the affected machine and that another workstation entry may be irrelevant. WS-OPS-11 skipped its download, so 2.3.9 never got staged anywhere. The right version is 2.4.1, and the integrity alert fires 31 seconds after it was staged.

The tampered file also contains the string `UNAPPROVED_PATCH_BLOCK` in its binary data. That's a nice confirmation, but the hash mismatch is the evidence that matters.

Flag: `Professor{report-agent_2.4.1}`

## Operator notes

I ran the warmups myself. For CR04 the AI picked up the `Salted__` header, matched job BK-773 to its password in the handoff note, explained why the other two passwords were decoys, and ran the decrypt. That's three small reads across two files, and having them laid out side by side made the answer easy to check.

CR05 followed the same pattern: hash check first, then the deployment log for the version. The version is where I'd slow down on a real case, because 2.3.9 sits in the same log next to the same package name. The triage note settles it, and I wanted that reasoning written out before I submitted. The challenge also didn't say whether the package name keeps its hyphen in the flag, so I had `Professor{report_agent_2.4.1}` ready as a backup.

## What this section teaches

Encoding changes how data looks, and anyone can reverse it. Encryption needs a key. Hashing tells you whether something changed. The two harder challenges are mostly about reading logs carefully: the crypto step takes one command once you know which input to trust.
