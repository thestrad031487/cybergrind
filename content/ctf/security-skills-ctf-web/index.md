---
title: "Security Skills CTF: website security"
date: 2026-11-21
draft: false
author: "Jason Wacker"
section: "ctf"
tags: ["ctf", "security-skills", "writeup", "ai-assisted", "web", "devtools", "access-control"]
description: "Page source, robots.txt, CSS-hidden elements, a client-side role check, and a retired admin console still shipping in a public static bundle."
platform: "Security Skills"
difficulty: "Beginner"
category: "Web"
---

Five challenges, 375 points. Every one of them is a static site you open locally, so there's no server to attack. They all teach the same lesson from different angles: if the browser has the data, the user has the data.

Part of the [Security Skills CTF series](/ctf/security-skills-ctf-overview/).

## WEB01: view the page source (25)

The page shows a heading and a hint. The flag is in a hidden form field:

```html
<input type="hidden" name="training_flag" value="Professor{view_source_works}">
```

Ctrl+U, then Ctrl+F for `Professor{`. Or from a terminal:

```bash
grep -o 'Professor{[^}]*}' WEB01-home.html
```

Flag: `Professor{view_source_works}`

There's also a Cloudflare analytics script with a `token` value at the bottom of every page on this board. Cloudflare adds that automatically and it has nothing to do with the challenges.

## WEB02: read robots.txt (50)

The zip has an `index.html`, a `robots.txt`, and a `training/` folder.

```
User-agent: *
Disallow: /training/flag.txt
```

`training/flag.txt` holds the flag.

Flag: `Professor{robots_is_not_security}`

`Disallow` asks well-behaved crawlers to stay away. It doesn't stop anyone else, and it tells an attacker exactly which paths you'd rather they didn't see. Checking robots.txt for `/admin`, `/backup` and similar is standard recon.

## WEB03: inspect a hidden message (75)

```html
<p id="secret-message" style="display:none">Professor{inspect_the_element}</p>
```

`display:none` keeps the paragraph from rendering, but it's still in the DOM. Open DevTools, find the element, and untick `display: none` in the Styles pane to make it appear.

Flag: `Professor{inspect_the_element}`

## WEB04: employee portal (100)

A fake employee portal with a "Restricted Reviews" section for managers only. The README says it's intentionally not secure and points you at scripts, storage and control flow.

`portal.js` decides the role like this:

```javascript
function getRole(){
  const u = new URLSearchParams(location.search).get('role');
  if (u) return u;
  try { return localStorage.getItem('northline_role') || 'employee'; }
  catch(e) { return 'employee'; }
}
```

The visitor controls both inputs. Either of these unlocks the manager view:

- Open `index.html?role=manager`
- Run `localStorage.setItem('northline_role','manager')` in the console and reload

You don't even need to do that, though. `data.js` loads the full `restrictedReviews` array into every visitor's browser, and review IR-204 says it outright: the portal trusts a role set entirely in the browser.

Flag: `Professor{client_side_is_not_auth}`

The fix is to keep restricted records on a server and hand them over only after the server checks a session or token it issued itself. Hiding a button doesn't protect the data behind it.

## WEB05: forgotten admin panel (125)

A vendor's static support site that supposedly retired an old admin console. The challenge asks you to trace how the console is still reachable.

Here's the trail:

1. `docs/release-history.html` loads `assets/js/release-history.js`.
2. The v2.8 entry in that script has a `legacyAsset` field: `../legacy/operations-console.html`. The release page even prints it as "Legacy migration asset."
3. That console page loads `assets/js/old-console.js`, which holds three records. The `audit` one is finding IR-88.

```javascript
audit: 'ARCHIVE FINDING IR-88 | Former administrative interface remains reachable
as a static asset. Root cause: old client bundles were never removed.
Proof of exposure: Professor{archived_pages_are_public}'
```

A quick recursive grep finds the flag right away, but following the trail is the point of the exercise.

```bash
grep -rno 'Professor{[^}]*}' site/
```

Flag: `Professor{archived_pages_are_public}`

"Retired" here only meant removed from the main navigation. The files still shipped and the docs still linked to them. Static hosting has no access checks, so anything in the bundle is public. Retired assets need to be deleted from the deploy, and archives belong somewhere that requires authentication.

## Operator notes

This category needed the least help. It's all static HTML and JavaScript, and DevTools reads every bit of it. WEB04 and WEB05 were where the AI saved time. It read `portal.js` and `data.js` together and pointed out that the role check didn't matter because the restricted data shipped to every visitor anyway. In WEB05 it laid out the file trail from the release history to the old console script, which beats clicking through by hand. A recursive grep finds that flag in a second either way. The trail is the part worth writing up, since it's how a retired page actually stays public.

## What this section teaches

All five come down to the same thing: the client is not a trust boundary. View source, DevTools and a text editor are enough to read anything the server sends.
