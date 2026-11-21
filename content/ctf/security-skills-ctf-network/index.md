---
title: "Security Skills CTF: network security"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["ctf", "security-skills", "writeup", "ai-assisted", "network", "wireshark", "DNS", "pcap"]
description: "Reading HTTP and DNS in Wireshark, then catching an unauthorized upload and a DNS exfiltration sequence by correlating pcaps with inventories."
platform: "Security Skills"
difficulty: "easy"
category: "network"
---

Five challenges, 375 points, all pcap analysis. The warmups are single-packet captures. The last two mix suspicious traffic in with normal office noise and give you a host inventory and an approved-destinations list to sort it out.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## NW01: first HTTP packet (25)

One GET request with the flag in the query string:

```
GET /welcome?flag=Professor{http_get_seen} HTTP/1.1
Host: training.example
```

In Wireshark, filter on `http` and expand the request. With tshark:

```bash
tshark -r NW01-http-get.pcap -Y http.request -T fields -e http.request.uri
```

Flag: `Professor{http_get_seen}`

## NW02: a DNS text record (50)

A DNS response for `training.example` with a TXT answer.

```bash
tshark -r NW02-dns-txt.pcap -Y dns.txt -T fields -e dns.txt
```

Flag: `Professor{dns_txt_record}`

TXT records do real work (SPF, DKIM, domain verification), but they also get abused for command and control and data exfiltration because DNS usually gets out when other protocols don't. That comes back in NW05.

## NW03: read an HTTP reply (75)

A `200 OK` with a plain-text body. Follow TCP Stream in Wireshark, or:

```bash
tshark -r NW03-http-reply.pcap -q -z follow,tcp,ascii,0
```

Flag: `Professor{follow_tcp_stream}`

## NW04: unauthorized upload (100)

A capture of a few minutes of workstation traffic, a host inventory, and a list of approved destinations. One workstation sent a document somewhere it shouldn't have. The flag is the hostname plus the filename stem.

Filtering on `http.request.method == "POST"` cuts the capture down to three uploads:

| Source | Host | Destination | File |
|---|---|---|---|
| 10.30.4.12 | WS-03 | portal.corp.test | weekly-timesheet.csv |
| 10.30.4.27 | WS-12 | support-vendor.test | device-support.zip |
| 10.30.4.18 | WS-07 | drop-gateway.test (203.0.113.77) | client-roster.csv |

The first two go to approved destinations. `drop-gateway.test` isn't on the list at all, and the server answered `201 Created`, so the upload went through. The inventory maps 10.30.4.18 to WS-07 in Customer Success.

```bash
tshark -r workstation_traffic.pcap -Y 'http.request.method=="POST"' \
  -T fields -e ip.src -e http.host -e http.request.uri
```

The format wants the hostname in lowercase without hyphens and the file stem with hyphens turned into underscores.

Flag: `Professor{ws07_client_roster}`

The rest of the capture is GETs to update servers, status pages and help pages. Those matter because two of those destinations are on the approved list as downloads-only or GET-only. A POST to either of them would also have been a violation, so it's worth checking all three uploads against the list rather than stopping at the one with the scariest name.

## NW05: strange DNS (125)

A resolver trace with three workstations making ordinary DNS lookups, plus one host sending short numbered queries to a domain no approved service uses. You need the host and the fragments in order, with repeats counted once.

Counting queries by source and name makes it obvious. Every host queries `intranet.corp.test`, `ping.office-metrics.test`, `tickets.corp.test` and so on. Only 10.30.6.14 queries this:

```
01-k4.metrics-sync.test   (x2)
02-m7.metrics-sync.test   (x2)
03-r2.metrics-sync.test   (x2)
```

The inventory maps 10.30.6.14 to WS-14 in Customer Services. Each fragment was sent twice, so after removing duplicates and putting them in order by the leading number you get `k4`, `m7` and `r2`.

```bash
tshark -r resolver_trace.pcap \
  -Y 'dns.flags.response==0 && dns.qry.name contains "metrics-sync"' \
  -T fields -e ip.src -e dns.qry.name
```

Flag: `Professor{ws14_k4m7r2}`

The decoy is `ping.office-metrics.test`. The name is close, but all three workstations query it on a regular schedule, which is what monitoring traffic looks like. `metrics-sync.test` comes from one host, carries sequence numbers, and isn't on any approved list. Data packed into subdomain labels with a counter is a classic DNS tunneling pattern.

## Operator notes

All of the pcap work ran through tshark in the sandbox. For NW04 and NW05 the AI ran the filters, counted queries per host, and checked the results against the inventory and the approved list. That last step saved the most time. In NW04 it caught that two approved destinations were GET-only, so all three POSTs had to be checked, not just the one going to the obviously bad domain. In NW05 it separated the scheduled monitoring lookups from the numbered queries by looking at who sent them and how often.

Format was the open question again. The fragments carry sequence numbers (`01-k4`, `02-m7`, `03-r2`), and the challenge didn't say whether those belong in the flag. I submitted without them and kept `Professor{ws14_01k402m703r2}` as the backup.

## What this section teaches

Filtering gets you to the interesting packets. The answer comes from the inventory and the approved list. Both of the harder challenges were impossible to solve from the pcap alone, which is how real network investigations usually go.
