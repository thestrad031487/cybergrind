---
title: "Who actually uses a leaked AWS key? Tracing it with rotating canaries"
date: 2026-10-08
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["honeypot", "aws", "canarytokens", "llmjacking", "cloudflare-workers", "threat-intel"]
description: "I put fake AWS keys on my site and changed them every day. Most of the people who used them had never visited my site."
draft: false
---

Every honeypot write-up says the same thing about leaked cloud keys: put one on the internet and someone will try it within hours. That's true. I watched it happen on day one.

What those write-ups usually can't tell you is who tries the key. I assumed it would be the scanner that found it. So I started handing out a different fake key each day and logging exactly who received which one. Over five days of that data, the reports labeled about 20 key uses as coming from addresses that had never asked my site for the file, and 2 from addresses that had.

The scanner that finds a key is usually not the one that uses it. Keys go into a pipeline, and the people at the end of it never touch your server.

## How the trap works

cybergrind.org runs on Cloudflare Pages. In front of it sits a small Cloudflare Worker that answers the paths scanners always ask for: `/.env`, `/.git/config`, `/.aws/credentials`, `/wp-login.php`, `/phpmyadmin` and a few others. Everything else passes through to the real site.

`/.env` and `/.aws/credentials` return AWS access keys that are [canarytokens](https://docs.canarytokens.org/guide/aws-keys-token). The keys have no permissions. When anyone makes an AWS API call with one, I get an alert with their IP, user agent and the API call they made. `/.git/config` returns a git remote URL with a unique credential in it, so if someone tries to clone with it, I know which request it was originally served to.

Each hit is logged to Workers KV. A daily digest posts to Slack, and a small script on my home server reads the alerts and the digest every morning and writes a report. The script uses fixed rules for severity and a local model only for a short summary, and it treats every field as hostile input. That part deserves its own post.

## The first week looked like everyone else's

Most of the traffic was what you'd expect: mass scanning from hosting providers. Google Cloud, TC Datacenter in Poland, TECHOFF, RouterHosting and Virtuo showed up over and over.

The user agents were more interesting. One Google Cloud address requested `/.env` with about ten different AI crawler user agents in a few seconds: Claude-SearchBot, OAI-SearchBot, Perplexity-User, cohere-ai, MistralAI, Kimi, Hunyuan, Googlebot and more. None of those crawlers run from random cloud customer addresses. My guess is that the scanner is looking for sites whose firewall rules let AI bots through, since plenty of sites added those exceptions this year.

The decoy keys were tested within hours of going live. The most common first call was Bedrock's `ListFoundationModels`, followed by SES and EC2. That lines up with what [Sysdig calls LLMjacking](https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack): stolen cloud keys used to run someone else's AI workloads on your bill.

So far, nothing you haven't read before.

## None of them had fetched the key

On October 3, four different sources used the decoy key: two in Tunisia, one in Paris and one in Ireland. I went back through the Worker's log to see when each of them had grabbed the `.env` file.

None of them had. Not one of the four had ever requested it.

With a single key handed to everyone, that was as far as I could get. The key had clearly been passed around, but I couldn't tell how fast or through whom. So I changed the setup.

## Rotating canaries

I created seven canary keys and called them slots. The Worker now serves a different slot each day (the UTC day number mod 7), and every request for `/.env` or `/.aws/credentials` records which slot it was given. The log is kept for 30 days. Each canarytoken's memo includes its slot number, so every alert says which day's key was used.

That's enough to sort every key use into one of three groups:

- self-fetched, where the address using the key is the one that downloaded it
- hand-off, where the key was downloaded by someone else and the user never requested it
- legacy, where the user had the original single key from before rotation started

There are limits. Several addresses fetch the same slot on a busy day, so a hand-off tells me which day's harvest a key came from, not which harvester passed it along. Slots repeat every week. And this is one small site, so treat the numbers as patterns, not statistics.

## What the slots showed

### Self-serve scanners are the slow ones

Only two addresses in the slot data downloaded a key and used it themselves. One used it 2 hours 41 minutes after downloading it, the other after 2 hours 12 minutes. Before rotation, a TC Datacenter address pulled the key on October 2 and used it within a day.

These are the bots most people picture: scan, grab, test. They turned out to be the minority, and they weren't fast.

### A checker on Cloudflare's network

The most active key user was a group of Cloudflare addresses in AS13335 (`104.22.93.x`, `172.70.38.x` and `172.68.138.x`). They checked my keys against Bedrock again and again, and they never once requested a key from my site.

Every one of their requests had no User-Agent header. Every AWS SDK and the AWS CLI sends one, so something else was signing these calls. My best explanation is a key checker running as a Cloudflare Worker and signing requests with a small SigV4 library such as [aws4fetch](https://github.com/mhart/aws4fetch). A Worker's outbound `fetch()` doesn't add a User-Agent unless the code sets one. That would explain both the Cloudflare addresses and the missing header. I can't prove it from my side, but it's the simplest explanation that fits.

The timing is what convinced me this is a pipeline. New keys reached the checker quickly: slot 4 was checked 23 to 25 minutes after the most recent download of it, and slot 5 about an hour after. Old keys kept coming back too. Slot 3 was checked again two and a half days after it had been served, which looks like a stored list being rechecked on a schedule.

The addresses that downloaded those slots included Google Cloud hosts cycling through fake GPTBot, Googlebot and ClaudeBot user agents, plus a handful of VPS providers. Put the pieces together and you get scrapers feeding a shared list of keys to a checker that keeps retesting it.

### One operator, two kinds of stolen credentials

One user stood out from the start. They connected from Tunisia with a tool that identifies itself as `nyx-recon-validator/1.0`. I couldn't find any public reference to it.

On October 3 they validated the key from a mobile connection, then three minutes later from a fixed home line on a different carrier, which looks like a phone hotspot followed by home internet. About an hour later they switched to Python's Boto3, and the SDK's user agent reported macOS on Apple Silicon. They looked at EKS/ECS, EC2 and KMS, tried `RunInstances` three times, checked the key again between attempts, and finally called `SimulatePrincipalPolicy`, which is what you'd run to figure out why your calls keep getting denied. That's a person at a MacBook trying to start servers and getting frustrated.

Later in the week the same tool showed up again with something new: a git credential from my `.git/config` decoy. That credential had been served to a Google Cloud address in Taiwan. It was used from three Tunisian IPv6 addresses and from a Google Cloud machine in the US running the same tool. So the same upstream source supplies this operator with both AWS keys and git credentials, and the US machine looks like their cloud box.

### Residential doesn't mean human

My first instinct was to treat sources on home internet connections with clean reputations as probable humans. I had to drop that.

A home connection in Saudi Arabia and another in the Dominican Republic sent the exact same tool fingerprint, and both called Bedrock's `Converse` API with my key. A Verizon mobile address and a Comcast home address did the same thing with `InvokeModel`. Two homes on two continents don't independently run identical tooling against the same key. These are almost certainly residential proxy exits, meaning traffic routed through someone's home connection, often without them knowing. An AbuseIPDB score of 0% means very little when the request is coming out of someone's living room. That's also why I'm not publishing any residential addresses here.

### The retired key keeps getting used

The original key stopped being served on October 3. On October 8 it was used by four more sources. Every one of those uses is secondhand, from someone working off a list made at least five days earlier.

### What they wanted

Bedrock, overwhelmingly. Most key users started by listing models, and by the end of the week several were making real `InvokeModel` and `Converse` calls. SES (sending email) and EC2 (compute) came next. One user called `DeleteAccessKey` on the key they'd been given. That would cut off everyone else holding the same key, and I'd guess that was the point.

## If you run an AWS account

A leaked key should be revoked the day you find it. Rotating it isn't enough. In my data, the gap between a key being scraped and someone using it was minutes to hours, and reuse continued for days after the key stopped being served.

If an account doesn't use Bedrock, block it with a [service control policy](https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html). Most of what I saw was people trying to run models on someone else's bill. If you do use Bedrock, turn on [model invocation logging](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html) so unfamiliar usage shows up somewhere you'll see it.

The first calls are predictable: `GetCallerIdentity` and `ListFoundationModels`. An alert on either one from a principal that has never made those calls before will catch most of this activity early. A SigV4-signed call with no User-Agent in CloudTrail is also unusual enough to deserve a detection rule.

Don't lean on IP reputation. The busiest key users came from Cloudflare's network and from home connections, not from the hosting ranges everyone blocks.

And scan your own repositories. Most of these keys start out somewhere public by accident. I built a [repo secret scanner](/tools/repo-scanner/) for exactly that, after finding one of my own.

## Try it yourself

All of this runs on free tiers: canarytokens for the keys, one Cloudflare Worker and Workers KV for the log. The rotation itself is a few lines of code. Two rules if you build one. Keep the decoy keys without permissions and never put a real credential in a honeypot. And don't publish the residential addresses you catch, because many of them belong to people who have no idea their connection is being used.

## Limitations

This is one site and five days of rotating-key data, plus the week before it. Several addresses download each slot, so hand-offs show which day a key was harvested, not who passed it on. Location and network details come from canarytokens.org and Cloudflare, and proxies blur both. The Cloudflare Workers explanation for the no-User-Agent checker is an inference, not something I can confirm from outside.

The honeypot keeps running. I'll post an update once there's a full month of slot data.

## References

- Sysdig, "LLMjacking: Stolen Cloud Credentials Used in New AI Attack": https://www.sysdig.com/blog/llmjacking-stolen-cloud-credentials-used-in-new-ai-attack
- Sysdig, "The Growing Dangers of LLMjacking": https://www.sysdig.com/blog/growing-dangers-of-llmjacking
- Canarytokens documentation, AWS API Keys token: https://docs.canarytokens.org/guide/aws-keys-token
- aws4fetch, SigV4 request signing for fetch and Cloudflare Workers: https://github.com/mhart/aws4fetch
- AWS Organizations, service control policies: https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html
- Amazon Bedrock, model invocation logging: https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html
