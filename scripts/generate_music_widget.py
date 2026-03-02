#!/usr/bin/env python3
"""
Generate a "Now Vibing To" music widget SVG for GitHub profile README.
Fetches the most recently liked song from YouTube Music via YouTube Data API v3.

Works both locally (reads oauth.json) and in GitHub Actions (reads env vars).

NOTE: No <image> tags or data: URIs — GitHub's SVG sanitizer strips them.
Album art is a gradient placeholder with a music note icon overlay.
"""

import html
import json
import os
import ssl
import sys
import urllib.request
import urllib.parse
import urllib.error

# SSL context — macOS Python 3.9 doesn't find system certs by default
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

# ─── Config ───────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
OAUTH_PATH = os.path.join(REPO_DIR, "oauth.json")
OUTPUT_PATH = os.path.join(REPO_DIR, "assets", "music-widget.svg")

CLIENT_ID = os.environ.get("YTM_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YTM_CLIENT_SECRET", "")

SVG_WIDTH = 400
SVG_HEIGHT = 160


def load_oauth():
    """Load OAuth tokens from env var (CI) or local file."""
    raw = os.environ.get("YTM_OAUTH_JSON")
    if raw:
        return json.loads(raw)
    if os.path.exists(OAUTH_PATH):
        with open(OAUTH_PATH, "r") as f:
            return json.load(f)
    print("ERROR: No OAuth credentials found.", file=sys.stderr)
    sys.exit(1)


def save_oauth(data):
    """Persist tokens locally (skip in CI)."""
    if not os.environ.get("YTM_OAUTH_JSON"):
        with open(OAUTH_PATH, "w") as f:
            json.dump(data, f, indent=1)


def refresh_token(oauth):
    """Refresh the access token and return updated oauth dict."""
    payload = urllib.parse.urlencode({
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": oauth["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=payload)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            new = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Token refresh failed: {e.code} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    oauth["access_token"] = new["access_token"]
    if "refresh_token" in new:
        oauth["refresh_token"] = new["refresh_token"]
    oauth["expires_in"] = new.get("expires_in", 3599)
    save_oauth(oauth)
    return oauth


def fetch_liked_song(access_token):
    """Fetch the most recently liked song from YouTube Music."""
    params = urllib.parse.urlencode({
        "part": "snippet,contentDetails",
        "playlistId": "LM",
        "maxResults": "1",
    })
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?{params}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {access_token}"})
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"API error: {e.code} {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

    if not data.get("items"):
        return None

    snippet = data["items"][0]["snippet"]
    title = snippet.get("title", "Unknown")
    channel = snippet.get("videoOwnerChannelTitle", "Unknown Artist")
    # Clean up " - Topic" suffix from auto-generated artist channels
    if channel.endswith(" - Topic"):
        channel = channel[: -len(" - Topic")]

    video_id = snippet.get("resourceId", {}).get("videoId", "")
    return {
        "title": title,
        "artist": channel,
        "video_id": video_id,
    }


def truncate_text(text, max_chars=30):
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def generate_svg(song):
    """Generate the premium music widget SVG.

    No <image> tags, no data: URIs, no external URLs.
    Album art = gradient placeholder with music note overlay.
    All animations CSS @keyframes only (no JS, no SMIL).
    """
    title_esc = html.escape(truncate_text(song["title"], 32))
    artist_esc = html.escape(truncate_text(song["artist"], 36))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" role="img" aria-label="Now Vibing To: {title_esc} by {artist_esc}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#0D1117"/>
      <stop offset="100%" stop-color="#161B22"/>
    </linearGradient>
    <linearGradient id="art" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2d1b69"/>
      <stop offset="50%" stop-color="#1a0a3e"/>
      <stop offset="100%" stop-color="#0f0825"/>
    </linearGradient>
  </defs>
  <style>
    @keyframes tw {{
      0%, 100% {{ opacity: .1 }}
      50% {{ opacity: .7 }}
    }}
    @keyframes eq1 {{
      0%, 100% {{ height: 10px; y: 132px; }}
      50% {{ height: 38px; y: 104px; }}
    }}
    @keyframes eq2 {{
      0%, 100% {{ height: 34px; y: 108px; }}
      50% {{ height: 12px; y: 130px; }}
    }}
    @keyframes eq3 {{
      0%, 100% {{ height: 8px; y: 134px; }}
      50% {{ height: 40px; y: 102px; }}
    }}
    @keyframes eq4 {{
      0%, 100% {{ height: 30px; y: 112px; }}
      50% {{ height: 10px; y: 132px; }}
    }}
    @keyframes eq5 {{
      0%, 100% {{ height: 12px; y: 130px; }}
      50% {{ height: 36px; y: 106px; }}
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: .6 }}
      50% {{ opacity: 1 }}
    }}
    .star {{ fill: #FFD700 }}
    .t1 {{ animation: tw 3s ease-in-out infinite }}
    .t2 {{ animation: tw 3s ease-in-out .6s infinite }}
    .t3 {{ animation: tw 2.8s ease-in-out 1.3s infinite }}
    .t4 {{ animation: tw 3.5s ease-in-out 2s infinite }}
    .t5 {{ animation: tw 2.5s ease-in-out .3s infinite }}
    .t6 {{ animation: tw 3.2s ease-in-out 1.7s infinite }}
    .t7 {{ animation: tw 2.6s ease-in-out 2.4s infinite }}
    .b1 {{ animation: eq1 1.2s ease-in-out infinite; }}
    .b2 {{ animation: eq2 0.9s ease-in-out .15s infinite; }}
    .b3 {{ animation: eq3 1.05s ease-in-out .3s infinite; }}
    .b4 {{ animation: eq4 0.85s ease-in-out .1s infinite; }}
    .b5 {{ animation: eq5 1.1s ease-in-out .25s infinite; }}
    .lbl {{ animation: pulse 3s ease-in-out infinite; }}
  </style>

  <!-- Background -->
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="12" fill="url(#bg)"/>

  <!-- Mint border glow -->
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="12" fill="none" stroke="#90EE90" stroke-opacity="0.25" stroke-width="1"/>
  <rect x="1" y="1" width="{SVG_WIDTH - 2}" height="{SVG_HEIGHT - 2}" rx="11" fill="none" stroke="#90EE90" stroke-opacity="0.06" stroke-width="0.5"/>

  <!-- Stars -->
  <circle class="star t1" cx="15" cy="12" r="1"/>
  <circle class="star t2" cx="58" cy="8" r=".7"/>
  <circle class="star t3" cx="145" cy="11" r=".9"/>
  <circle class="star t4" cx="225" cy="6" r="1"/>
  <circle class="star t5" cx="305" cy="13" r=".8"/>
  <circle class="star t6" cx="358" cy="8" r="1"/>
  <circle class="star t7" cx="388" cy="15" r=".7"/>
  <circle class="star t1" cx="370" cy="148" r=".8"/>
  <circle class="star t3" cx="32" cy="150" r=".7"/>
  <circle class="star t5" cx="190" cy="152" r=".6"/>
  <circle class="star t2" cx="285" cy="148" r=".7"/>
  <circle class="star t4" cx="92" cy="6" r=".5"/>
  <circle class="star t6" cx="255" cy="10" r=".6"/>
  <circle class="star t7" cx="340" cy="80" r=".4"/>
  <circle class="star t2" cx="168" cy="22" r=".5"/>
  <circle class="star t5" cx="380" cy="100" r=".5"/>

  <!-- Album art placeholder: gradient square -->
  <rect x="20" y="30" width="100" height="100" rx="12" fill="url(#art)"/>
  <rect x="20" y="30" width="100" height="100" rx="12" fill="none" stroke="#90EE90" stroke-opacity="0.15" stroke-width="0.5"/>

  <!-- Beamed eighth notes on album art -->
  <g transform="translate(48, 55)" opacity="0.18">
    <!-- Left note head -->
    <ellipse cx="4" cy="35" rx="11" ry="7" transform="rotate(-20, 4, 35)" fill="white"/>
    <!-- Right note head -->
    <ellipse cx="32" cy="31" rx="11" ry="7" transform="rotate(-20, 32, 31)" fill="white"/>
    <!-- Left stem -->
    <rect x="13" y="-2" width="3" height="37" rx="1.5" fill="white"/>
    <!-- Right stem -->
    <rect x="41" y="-6" width="3" height="37" rx="1.5" fill="white"/>
    <!-- Beam -->
    <polygon points="13,-2 16,-2 44,-6 44,-3 16,1 13,1" fill="white"/>
  </g>

  <!-- YouTube Music icon (red circle + play triangle) -->
  <circle cx="140" cy="44" r="8" fill="#FF0000"/>
  <polygon points="138,40 138,48 145,44" fill="white"/>

  <!-- "Now Vibing To" label -->
  <text class="lbl" x="153" y="48" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="11" fill="#FFD700" font-weight="600">Now Vibing To</text>

  <!-- Song title -->
  <text x="140" y="76" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="16" fill="#FFFFFF" font-weight="700">{title_esc}</text>

  <!-- Artist -->
  <text x="140" y="96" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="13" fill="#90EE90" font-weight="500">{artist_esc}</text>

  <!-- EQ Bars — 5 tall animated bars, major visual element -->
  <rect class="b1" x="140" y="132" width="8" height="10" rx="2" fill="#90EE90" opacity=".85"/>
  <rect class="b2" x="153" y="108" width="8" height="34" rx="2" fill="#90EE90" opacity=".85"/>
  <rect class="b3" x="166" y="134" width="8" height="8"  rx="2" fill="#90EE90" opacity=".85"/>
  <rect class="b4" x="179" y="112" width="8" height="30" rx="2" fill="#90EE90" opacity=".85"/>
  <rect class="b5" x="192" y="130" width="8" height="12" rx="2" fill="#90EE90" opacity=".85"/>

</svg>'''
    return svg


def main():
    print("🎵 Generating music widget...")

    # Load and refresh token
    oauth = load_oauth()
    print("  Refreshing access token...")
    oauth = refresh_token(oauth)

    # Fetch recently liked song
    print("  Fetching recently liked song...")
    song = fetch_liked_song(oauth["access_token"])
    if not song:
        print("  No liked songs found. Using fallback.")
        song = {
            "title": "Nothing playing yet",
            "artist": "Like a song on YouTube Music!",
            "video_id": "",
        }

    print(f"  🎶 {song['title']} — {song['artist']}")

    # Generate SVG (no thumbnail fetching — GitHub strips <image> data URIs)
    svg = generate_svg(song)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        f.write(svg)

    print(f"  ✓ Widget saved to {OUTPUT_PATH}")
    print(f"  Size: {len(svg):,} bytes")


if __name__ == "__main__":
    main()
