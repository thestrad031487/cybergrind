---
title: "Fixing a Silent Failure: Migrating CyberGrind's Daily Pipeline to Self-Hosted Infrastructure"
date: 2026-07-19
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["homelab", "automation", "ollama", "self-hosted", "incident-response", "orange-book"]
description: "A practitioner's account of tracking down a silent pipeline failure, root-causing it properly instead of patching around it, and turning the fix into a full migration: self-hosted commentary, a new strategic briefing series, and audio narration."
---

It started as a small thing: a reader — well, me, reading my own site — noticed nine days in July with headlines but no "From the Trenches" commentary underneath them. Easy enough to backfill by hand. But backfilling isn't fixing, and I've learned the hard way that a bug you patch around instead of root-causing just shows up again wearing a different date.

This is the account of what turned into a seven-phase project: finding out *why* those nine days broke, discovering the actual fix required rethinking where and how the entire daily pipeline runs, and using that as the excuse to finally build two things I'd been wanting anyway — a strategic CISO-angle companion series, and self-hosted audio narration.

## The symptom vs. the cause

The nine missing days all had one thing in common: a complete headline list, zero commentary section. My first assumption was the obvious one — the machine running the cron job (my MacBook) had been asleep and missed the trigger entirely.

That was half right. But when I actually read the code generating these posts, the real bug was worse than a missed cron trigger. Here's the relevant function, more or less as it existed:

```python
def generate_commentary(headlines):
    # ... build prompt, call Ollama ...
    try:
        with urllib.request.urlopen(req, timeout=300) as response:
            return json.loads(response.read().decode())["response"]
    except Exception as e:
        print(f"Ollama commentary generation failed: {e}")
        return None
```

And downstream:

```python
commentary = generate_commentary(headlines)
if not commentary:
    print("Warning: commentary generation failed, post will be created without it")
content = generate_post(headlines, commentary)
```

Read that closely. If Ollama fails for *any* reason — not running, network hiccup, model not loaded — the script prints a warning to a log nobody's watching, and then **publishes the post anyway**, missing section and all. No error. No alert. No retry. Just a slightly incomplete blog post going live, indistinguishable at a glance from an intentional headlines-only day.

That's the actual lesson of this whole project: a silent partial failure is worse than a loud total one. A crashed script gets noticed. A script that "succeeds" while quietly doing less than it promised can run wrong for nine days before anyone catches it.

## Phase 1: Finding out Ollama was already there

The instinct was to spin up new infrastructure — install Ollama on the always-on server, migrate everything over. Turned out to be unnecessary. A quick check of the existing `ai-stack` Docker Compose file showed Ollama was already running there, GPU-accelerated, two months uptime, with five models already pulled. It had just never been the *commentary* pipeline's Ollama — that lived only on the MacBook.

Lesson here, and it's a boring one but worth stating: **inventory what you already have before you build something new.** The migration got dramatically simpler the moment I checked instead of assumed.

## Phase 2: Fixing the actual script

Two real defects needed fixing, plus one platform dependency that needed removing entirely:

1. **The macOS coupling.** The old script called `osascript` for GUI notification dialogs and started `ollama serve` as a local subprocess — both things that only work on a machine with an active desktop session. Moved to the server, both got replaced: a simple reachability check against the container that's already running, plus optional Slack alerting through infrastructure that already existed.
2. **The silent failure.** Commentary generation now retries twice with a delay, and if it still fails, the script exits without writing the post at all. An incomplete post is worse than a missing one — a missing post is an obvious gap; an incomplete one looks finished.
3. **Unicode sanitization.** While auditing the headline-ingestion code, I found something unrelated but worth mentioning: a scraped headline from one day's post contained a block of invisible, zero-width Unicode characters embedded in its link text — the kind of thing that renders as nothing but sits in the raw markdown regardless. I didn't dig into what it encoded. I stripped it, and added sanitization at the point headlines get ingested, so hidden content in third-party scraped text gets neutralized before it ever reaches a commit. Small reminder that "trust the feed" is a supply chain assumption like any other.

## Phase 3: Adding a second, strategic voice

With the pipeline actually reliable, it was a reasonable time to expand it rather than just fix it. The tactical "From the Trenches" commentary is written for practitioners — patch this, watch that CVE. A parallel **CISO Briefing** series reframes the same day's headlines for a governance audience: business risk, regulatory exposure, budget justification, what actually belongs in a board update instead of a ticket.

Worth noting honestly: the first attempt used the same lightweight model already in the loop, and it didn't reliably follow formatting rules — multiple closing "takeaway" lines instead of one, unwanted preamble text. Swapping to a larger model on the same box, with a more rigidly numbered rule format (mirroring what already worked reliably for the tactical commentary), fixed it in one iteration. Model capability and prompt structure aren't independently substitutable — a looser prompt on a bigger model outperformed a tighter one on a smaller model, but a numbered, explicit rule list mattered more than raw parameter count once both were in play.

## Phase 4: Teaching the pipeline to talk

The audio piece was the most purely "because I wanted to" addition — self-hosted text-to-speech narration for every post, no cloud API, no per-request cost, fully private. Piper handles the actual synthesis: fast, small, good-enough neural voices that run comfortably on CPU.

One infrastructure decision worth flagging for anyone doing similar work: **pip install with `--break-system-packages` is a flag worth pausing on, not just working around.** That flag exists specifically to override Debian/Ubuntu's protection against exactly the kind of system-Python dependency conflicts it enables. A virtual environment gets the same isolation without needing to override anything — same install, meaningfully less risk to the rest of the system's Python environment.

## Phase 5: The collision nobody warns you about

Wiring the audio player into the Hugo template surfaced the most interesting bug of the whole project. The build failed with:

```
executing "opengraph.html" ... error calling partial: range can't iterate over /audio
```

Turns out PaperMod, the theme this site runs on, already has a *built-in* `audio` front matter convention — used to populate Open Graph `og:audio` meta tags — and it expects that field to be a list. My plain string `audio: "/path.mp3"` broke a completely unrelated built-in template feature I never intended to touch, simply by naming collision.

The fix was trivial once diagnosed — rename the field to something that doesn't collide with theme-reserved names. The bigger takeaway is procedural: **this is exactly the kind of error a local build catches and a blind push doesn't.** I installed Hugo directly on the server, version-matched to what Cloudflare's build pipeline actually runs, specifically so errors like this surface in a terminal instead of a failed deployment log.

## Phase 6: Trusting the test, not the theory

Every individual piece had been validated in isolation by this point — commentary generation, the CISO brief, audio synthesis, the Hugo build. It would have been easy to call that "done" and just push everything live. Instead: delete the day's posts, run the actual orchestrator script exactly as cron would, and watch it work end to end with zero manual intervention — including a legitimate concurrent update to the SBOM files landing mid-pull with no conflict, and a clean commit-push in under a second.

Individually-tested components passing doesn't guarantee the whole chain works together. It's worth actually running the whole thing once, for real, before trusting it to a schedule.

## Phase 7: The part that almost got missed

Cutover felt done — new cron entry added on the server, correct schedule, correct log path. Except the *old* automation was still sitting there: a plain `crontab` entry on the MacBook, still pointed at the old script, still scheduled to fire. Nothing about moving the new pipeline to the server had touched it.

Had that gone unnoticed, this entire project would have ended exactly where it started: two machines, one repo, racing to publish the same day's post. The fix that started this whole effort would have quietly stopped working again, just with a different failure signature.

**Migrations aren't done when the new thing works. They're done when the old thing is confirmed off.**

## What this actually cost, and what it bought

Total build time: one focused session. What came out of it: a pipeline that no longer depends on a laptop staying awake, a second content series that didn't exist before, self-hosted audio on every post, and — the part that matters most — a failure mode that used to fail silently for over a week now fails loudly in under a second, every time, with a log line that says exactly what went wrong.

None of the individual fixes here were sophisticated. Retry logic. A `git pull --rebase`. A renamed front matter field. What mattered was refusing to stop at "backfill the missing days and move on," and instead asking why they went missing in the first place.

---

### References

- Hugo. "PaperMod Theme Documentation." [github.com/adityatelange/hugo-PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- OHF-Voice. "Piper — Fast, Local Neural Text-to-Speech." [github.com/OHF-Voice/piper1-gpl](https://github.com/OHF-Voice/piper1-gpl)
- Ollama. "Local LLM Runtime Documentation." [ollama.com](https://ollama.com/)
