#!/usr/bin/env python3
"""
status.py – fetch the most-recent public push event for a GitHub user and
render it as a terminal-style "last commit" SVG widget. Stdlib only.

Usage
-----
    python scripts/status.py --user naitikk31 -o assets/status

Writes assets/status-dark.svg and assets/status-light.svg.
A GITHUB_TOKEN or GH_TOKEN in the environment raises the API rate limit
(60 → 5 000 req/hour) but is not required.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = {"User-Agent": "status.py"}

# ── palette (matches banner.py + cards.py exactly) ──────────────────────────
THEMES = {
    "dark": {
        "bg":     "#0d1117",
        "border": "#30363d",
        "prompt": "#39d353",   # accent 1
        "dim":    "#0e4429",   # accent 2
        "text":   "#c9d1d9",
        "muted":  "#8b949e",
    },
    "light": {
        "bg":     "#ffffff",
        "border": "#d0d7de",
        "prompt": "#1a7f37",
        "dim":    "#aceebb",
        "text":   "#1f2328",
        "muted":  "#57606a",
    },
}

FONT  = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
NFONT = "ui-sans-serif,-apple-system,Segoe UI,Helvetica,Arial,sans-serif"


# ── GitHub API ───────────────────────────────────────────────────────────────

def _get(url: str, token: str | None):
    req = urllib.request.Request(url, headers=dict(UA))
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch_last_push(user: str, token: str | None) -> dict:
    """Return repo name, commit message, and relative time of last push."""
    try:
        events = _get(
            f"https://api.github.com/users/{user}/events/public?per_page=30",
            token,
        )
    except urllib.error.HTTPError as e:
        print(f"  API error {e.code}, using placeholder", file=sys.stderr)
        return {"repo": user, "msg": "pushing code somewhere", "ago": "recently"}

    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        commits = ev["payload"].get("commits", [])
        if not commits:
            continue
        repo = ev["repo"]["name"].split("/")[-1]
        msg  = commits[-1]["message"].split("\n")[0]
        when = dt.datetime.fromisoformat(ev["created_at"].replace("Z", "+00:00"))
        return {"repo": repo, "msg": msg, "ago": _relative(when)}

    return {"repo": user, "msg": "all quiet — probably thinking", "ago": "just now"}


def _relative(ts: dt.datetime) -> str:
    seconds = int((dt.datetime.now(dt.timezone.utc) - ts).total_seconds())
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    return f"{seconds // 86400}d ago"


# ── SVG renderer ─────────────────────────────────────────────────────────────

def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )


def render(info: dict, theme: str) -> str:
    c = THEMES[theme]
    W, H, pad = 420, 96, 16

    repo = esc(info["repo"][:30])
    msg  = esc(info["msg"][:50] + ("…" if len(info["msg"]) > 50 else ""))
    ago  = esc(info["ago"])

    # Three macOS-style traffic-light dots in the header
    dots = (
        f'<circle cx="14" cy="15" r="4.5" fill="#ff5f57"/>'
        f'<circle cx="27" cy="15" r="4.5" fill="#ffbd2e"/>'
        f'<circle cx="40" cy="15" r="4.5" fill="#28c840"/>'
    )

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="last commit status" '
        f'font-family="{FONT}">'
        # card background
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="9" '
        f'fill="{c["bg"]}" stroke="{c["border"]}"/>'
        # header strip
        f'<rect x=".5" y=".5" width="{W-1}" height="30" rx="9" fill="{c["dim"]}"/>'
        f'<rect x=".5" y="20" width="{W-1}" height="11" fill="{c["dim"]}"/>'
        + dots +
        # terminal prompt
        f'<text x="{pad}" y="54" font-size="11" fill="{c["muted"]}">$ git log --oneline -1</text>'
        # repo name
        f'<text x="{pad}" y="72" font-size="12.5" fill="{c["prompt"]}" font-weight="600">'
        f'&#x25B8; {repo}</text>'
        # commit message
        f'<text x="{pad + 10}" y="86" font-size="11.5" fill="{c["text"]}">{msg}</text>'
        # time badge
        f'<text x="{W - pad}" y="72" text-anchor="end" font-size="10" '
        f'fill="{c["muted"]}">{ago}</text>'
        f'</svg>'
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--user", default="naitikk31")
    p.add_argument("-o", "--out", type=Path, default=Path("assets/status"))
    args = p.parse_args(argv)

    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    info  = fetch_last_push(args.user, token)
    print(f"  last push: {info['repo']} — {info['msg'][:45]}  ({info['ago']})")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        svg  = render(info, theme)
        dest = args.out.with_name(f"{args.out.name}-{theme}.svg")
        dest.write_text(svg, encoding="utf-8")
        print(f"wrote {dest}")


if __name__ == "__main__":
    main()
