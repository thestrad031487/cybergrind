"""
safe_text.py - make externally sourced or LLM-generated text safe to publish.

hugo.toml sets markup.goldmark.renderer.unsafe = true, so any raw HTML that
lands in a markdown post is rendered as HTML. Headlines come from NewsAPI and
commentary comes from a local LLM that reads those headlines, so both are
untrusted. Run them through these helpers before writing a post.
"""
import html
import re
from urllib.parse import urlparse

# Zero-width, bidi override, and other invisible formatting characters.
_INVISIBLE = re.compile(r"[​-‏‪-‮⁠-⁯﻿]")
_TAG = re.compile(r"<[^>]*>")
_SHORTCODE = re.compile(r"\{\{\s*[<%]")


def strip_invisible(text):
    return _INVISIBLE.sub("", text or "")


def md_text(text):
    """Plain text for use inside markdown: no HTML, no link syntax, no shortcodes."""
    text = html.escape(strip_invisible(text), quote=False)
    text = text.replace("[", "\\[").replace("]", "\\]")
    text = text.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
    return _SHORTCODE.sub("{ {", text)


def safe_url(url):
    """Return the URL if it is plain http(s) with no characters that break markdown, else ''."""
    url = strip_invisible(url).strip()
    try:
        parts = urlparse(url)
    except ValueError:
        return ""
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return ""
    if any(c in url for c in " <>()\"'`"):
        return ""
    return url


def llm_markdown(text):
    """LLM output: keep its markdown, drop any HTML tags and Hugo shortcodes."""
    text = strip_invisible(text)
    text = _TAG.sub("", text)
    return _SHORTCODE.sub("{ {", text)
