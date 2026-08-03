---
title: "Intune in Practice, Part 7: Running Intune in a Lean Non-Profit IT Shop"
date: 2026-07-27
author: "Jason, Cyber Professional"
section: "orange-book"
tags: ["intune", "endpoint management", "non-profit", "microsoft 365", "it budget", "orange-book"]
description: "Free Intune for non-profits isn't a thing anymore. Practical recommendations for deploying and running Intune when the IT budget is thin, the team is small (sometimes a team of one), and every dollar competes directly with mission funding."
---

Everything covered so far in this series works the same way regardless of company size — the mechanics of enrollment, compliance, Conditional Access, app deployment, and baselines don't change because the org is a non-profit. What changes is the constraints: a much thinner budget, often a very small IT team (sometimes exactly one person wearing every hat), and a board that reasonably wants to know why any dollar isn't going toward the mission. This post is about running Intune well inside those constraints, drawn from real lean-IT-shop experience rather than enterprise assumptions.

## The licensing reality has changed — plan around it, not the old assumption

If your mental model of non-profit Microsoft licensing is "Intune comes free," that assumption is out of date. Microsoft restructured its non-profit technology program: the free tier is now Microsoft 365 Business Basic (up to 300 seats), which does not include Intune or desktop Office apps. Business Premium — the tier that includes Intune — moved from a free donated allocation to a steeply discounted paid tier, commonly cited around a 75% discount off commercial pricing, but a real line item now rather than a $0 one.

The practical planning implication: don't default every user to Business Premium out of habit. Segment your user base honestly. Users who genuinely need desktop Office and managed devices go on Premium; users who only need email and web apps can sit on Business Basic and cost nothing. This single exercise is often the biggest lever a small non-profit IT budget has, and it's worth doing deliberately rather than inheriting whatever licensing mix existed before anyone looked closely.

A second, frequently-missed lever: Azure for Nonprofits provides a separate annual credit (commonly cited around $3,500) that's completely independent of the M365 licensing grant and requires its own application. If you're running any Azure-hosted infrastructure — even something small — and haven't specifically applied for this, it's worth the roughly hour-long application process. A meaningful number of eligible organizations simply never apply because it's a separate program from the one they already know about.

## Prioritize the pairing that gives you the most security per hour invested

With a small team, sequencing matters more than it does at enterprise scale — you genuinely cannot build everything at once, so build the highest-leverage pieces first. The compliance-policy-plus-Conditional-Access pairing from Parts 3 and 4 is the strongest return on a limited number of hours: it's a relatively small configuration effort that meaningfully raises the bar against the most common opportunistic attacks (stolen credentials, unmanaged devices) without requiring ongoing daily attention once it's in place and tuned. Prioritize that over more elaborate app-deployment automation or a fully custom Settings Catalog baseline if you're choosing where to spend your first real block of implementation time.

## Documentation is a force multiplier when you don't have a bench

In a larger IT org, tribal knowledge surviving in one person's head is inconvenient. In a one-person shop, it's a real operational risk — if that person is out sick, on vacation, or leaves, whoever's covering has nothing to work from. Documenting onboarding and offboarding procedures, standard configuration decisions, and the reasoning behind non-default settings isn't overhead here — it's closer to insurance. It doesn't need to be elaborate: a clear, consistently updated set of procedure documents beats an ambitious wiki nobody maintains.

## You don't need an enterprise asset management platform to track a fleet

A full-featured IT asset management platform is often out of reach on a non-profit budget, and often not actually necessary at the scale a lean org is operating at. A well-structured spreadsheet — device inventory, warranty status, assignment, lifecycle stage, with cross-referenced lookup tables rather than static copy-pasted data — covers most of what a small fleet genuinely needs, and it's something one person can build and maintain without a dedicated tooling budget. The goal isn't sophistication for its own sake; it's knowing what you own, who has it, and when it needs replacing, in a format that's actually sustainable for the team maintaining it.

## Stack the grants — don't just take the first offer

TechSoup and Microsoft's nonprofit portal aren't the only programs worth checking. Salesforce, Adobe, and several security vendors run their own nonprofit discount or donation programs independently of the Microsoft ecosystem, and they're rarely bundled together anywhere. It's worth an annual review pass checking what's currently available rather than assuming last year's grant list is still the complete picture — these programs change terms more often than most IT teams have bandwidth to track proactively.

Part 8 closes out the series with the other side of running Intune: what an attacker actually targets in an Intune-managed environment, and the hardening steps that matter most regardless of organization size or budget.

---

### References

- Microsoft Negotiations. "Microsoft 365 Nonprofit Licensing: The Complete Guide (2026)." [microsoftnegotiations.com](https://microsoftnegotiations.com/blog/microsoft-365-nonprofit-licensing)
- Microsoft. "Technology and software grants and discounts for nonprofits." [microsoft.com/en-us/nonprofits](https://www.microsoft.com/en-us/nonprofits/offers-for-nonprofits)
- SerenIT. "Microsoft 365 for Nonprofits in 2026: Free Plans Most Organizations Miss." [serenitllc.com](https://serenitllc.com/blog/microsoft-365-nonprofit-licensing)
- The Register. "Microsoft pulls MS365 Business Premium from nonprofits." [theregister.com](https://www.theregister.com/2025/05/16/microsoft_pulls_ms365_business_premium/)
