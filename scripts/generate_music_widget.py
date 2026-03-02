#!/usr/bin/env python3
"""
Generate a "Recently Liked" music widget SVG for GitHub profile README.
Fetches the most recently liked song from YouTube Music via YouTube Data API v3.

Works both locally (reads oauth.json) and in GitHub Actions (reads env vars).
"""

import base64
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

SVG_WIDTH = 420
SVG_HEIGHT = 130
THUMB_SIZE = 80


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

    # Get best available thumbnail
    thumbs = snippet.get("thumbnails", {})
    thumb_url = None
    for quality in ("medium", "high", "default"):
        if quality in thumbs:
            thumb_url = thumbs[quality]["url"]
            break

    video_id = snippet.get("resourceId", {}).get("videoId", "")
    return {
        "title": title,
        "artist": channel,
        "thumbnail_url": thumb_url,
        "video_id": video_id,
    }


def fetch_thumbnail_b64(url):
    """Download thumbnail and return base64 data URI."""
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10, context=SSL_CTX) as resp:
            data = resp.read()
            ct = resp.headers.get("Content-Type", "image/jpeg")
            b64 = base64.b64encode(data).decode()
            return f"data:{ct};base64,{b64}"
    except Exception as e:
        print(f"Thumbnail fetch failed: {e}", file=sys.stderr)
        return None


def truncate_text(text, max_chars=30):
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def generate_svg(song, thumb_b64):
    """Generate the SVG widget."""
    title_esc = html.escape(truncate_text(song["title"], 32))
    artist_esc = html.escape(truncate_text(song["artist"], 36))
    video_url = f"https://music.youtube.com/watch?v={song['video_id']}" if song["video_id"] else "#"

    # Fallback placeholder if no thumbnail
    if thumb_b64:
        thumb_element = f'''<image x="20" y="25" width="{THUMB_SIZE}" height="{THUMB_SIZE}" href="{thumb_b64}" clip-path="url(#thumbClip)" preserveAspectRatio="xMidYMid slice"/>'''
    else:
        thumb_element = f'''<rect x="20" y="25" width="{THUMB_SIZE}" height="{THUMB_SIZE}" rx="8" fill="#1a1a2e"/>
      <text x="{20 + THUMB_SIZE // 2}" y="{25 + THUMB_SIZE // 2 + 8}" text-anchor="middle" font-size="28" fill="#FFD700">🎵</text>'''

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" role="img" aria-label="Recently liked song: {title_esc} by {artist_esc}">
  <defs>
    <clipPath id="thumbClip">
      <rect x="20" y="25" width="{THUMB_SIZE}" height="{THUMB_SIZE}" rx="8"/>
    </clipPath>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <style>
    @keyframes tw {{
      0%, 100% {{ opacity: .15 }}
      50% {{ opacity: 1 }}
    }}
    @keyframes bop {{
      0%, 100% {{ transform: translateY(0) }}
      50% {{ transform: translateY(-3px) }}
    }}
    @keyframes eq1 {{
      0%, 100% {{ height: 4px; y: 104px; }}
      50% {{ height: 14px; y: 94px; }}
    }}
    @keyframes eq2 {{
      0%, 100% {{ height: 8px; y: 100px; }}
      50% {{ height: 18px; y: 90px; }}
    }}
    @keyframes eq3 {{
      0%, 100% {{ height: 6px; y: 102px; }}
      50% {{ height: 12px; y: 96px; }}
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: .6 }}
      50% {{ opacity: 1 }}
    }}
    @keyframes noteFloat {{
      0%, 100% {{ transform: translateY(0) rotate(0deg); opacity: .7 }}
      50% {{ transform: translateY(-5px) rotate(8deg); opacity: 1 }}
    }}
    .st {{ fill: #FFD700 }}
    .st1 {{ animation: tw 3s ease-in-out infinite }}
    .st2 {{ animation: tw 3s ease-in-out .7s infinite }}
    .st3 {{ animation: tw 2.8s ease-in-out 1.4s infinite }}
    .st4 {{ animation: tw 3.5s ease-in-out 2.1s infinite }}
    .st5 {{ animation: tw 2.5s ease-in-out .35s infinite }}
    .st6 {{ animation: tw 3.2s ease-in-out 1.8s infinite }}
    .st7 {{ animation: tw 2.6s ease-in-out 2.5s infinite }}
    .alien {{ animation: bop 3s ease-in-out infinite }}
    .eq-bar {{ fill: #90EE90; rx: 1 }}
    .eq1 {{ animation: eq1 0.8s ease-in-out infinite }}
    .eq2 {{ animation: eq2 0.6s ease-in-out infinite .1s }}
    .eq3 {{ animation: eq3 0.7s ease-in-out infinite .2s }}
    .label {{ animation: pulse 3s ease-in-out infinite }}
    .note {{ animation: noteFloat 2.5s ease-in-out infinite }}
    .note2 {{ animation: noteFloat 2.5s ease-in-out 1.2s infinite }}
  </style>

  <!-- Background -->
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="14" fill="#0D1117"/>
  <rect width="{SVG_WIDTH}" height="{SVG_HEIGHT}" rx="14" fill="none" stroke="#90EE90" stroke-width=".5" opacity=".2"/>

  <!-- Subtle inner glow -->
  <rect x="1" y="1" width="{SVG_WIDTH - 2}" height="{SVG_HEIGHT - 2}" rx="13" fill="none" stroke="#90EE90" stroke-width=".3" opacity=".08"/>

  <!-- Stars -->
  <circle class="st st1" cx="12" cy="14" r="1.2"/>
  <circle class="st st2" cx="48" cy="8" r=".8"/>
  <circle class="st st3" cx="135" cy="12" r="1"/>
  <circle class="st st4" cx="210" cy="6" r="1.1"/>
  <circle class="st st5" cx="290" cy="14" r=".9"/>
  <circle class="st st6" cx="350" cy="8" r="1.2"/>
  <circle class="st st7" cx="400" cy="16" r=".8"/>
  <circle class="st st1" cx="375" cy="118" r="1"/>
  <circle class="st st3" cx="30" cy="118" r=".9"/>
  <circle class="st st5" cx="180" cy="120" r=".7"/>
  <circle class="st st2" cx="320" cy="122" r=".8"/>
  <circle class="st st4" cx="80" cy="6" r=".6"/>
  <circle class="st st6" cx="255" cy="10" r=".7"/>
  <circle fill="#334" cx="160" cy="122" r=".4"/>
  <circle fill="#334" cx="230" cy="118" r=".5"/>
  <circle fill="#334" cx="410" cy="65" r=".4"/>

  <!-- Album art thumbnail -->
  {thumb_element}

  <!-- Equalizer bars next to thumbnail -->
  <rect class="eq-bar eq1" x="105" y="94" width="3" height="4" opacity=".7"/>
  <rect class="eq-bar eq2" x="110" y="90" width="3" height="8" opacity=".7"/>
  <rect class="eq-bar eq3" x="115" y="92" width="3" height="6" opacity=".7"/>

  <!-- "Recently Liked" label -->
  <text class="label" x="125" y="42" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="11" fill="#FFD700" font-weight="600">♫ Recently Liked</text>

  <!-- Song title -->
  <text x="125" y="64" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="15" fill="#FFFFFF" font-weight="700">{title_esc}</text>

  <!-- Artist name -->
  <text x="125" y="84" font-family="'Segoe UI','Helvetica Neue',Arial,sans-serif" font-size="12" fill="#90EE90" font-weight="400">{artist_esc}</text>

  <!-- Floating music notes -->
  <g class="note" opacity=".7">
    <text x="108" y="38" font-size="14" fill="#FFD700">♪</text>
  </g>
  <g class="note2" opacity=".5">
    <text x="260" y="26" font-size="10" fill="#90EE90">♫</text>
  </g>

  <!-- Cute alien with headphones -->
  <g class="alien" transform="translate(365, 52)">
    <!-- Body -->
    <ellipse cx="20" cy="38" rx="12" ry="10" fill="#90EE90" stroke="#5a9a5a" stroke-width="1.2"/>
    <!-- Head -->
    <ellipse cx="20" cy="20" rx="15" ry="14" fill="#90EE90" stroke="#5a9a5a" stroke-width="1.2"/>
    <!-- Eyes -->
    <ellipse cx="14" cy="19" rx="4.5" ry="5.5" fill="#0D1117" stroke="#5a9a5a" stroke-width=".8"/>
    <ellipse cx="26" cy="19" rx="4.5" ry="5.5" fill="#0D1117" stroke="#5a9a5a" stroke-width=".8"/>
    <!-- Eye shine -->
    <circle cx="15.5" cy="17.5" r="1.8" fill="#FFD700" opacity=".8"/>
    <circle cx="27.5" cy="17.5" r="1.8" fill="#FFD700" opacity=".8"/>
    <!-- Smile -->
    <path d="M16,26 Q20,30 24,26" fill="none" stroke="#5a9a5a" stroke-width="1" stroke-linecap="round"/>
    <!-- Antennae -->
    <line x1="12" y1="8" x2="6" y2="-2" stroke="#5a9a5a" stroke-width="1.2" stroke-linecap="round"/>
    <circle cx="6" cy="-3" r="2" fill="#FFD700"/>
    <line x1="28" y1="8" x2="34" y2="-2" stroke="#5a9a5a" stroke-width="1.2" stroke-linecap="round"/>
    <circle cx="34" cy="-3" r="2" fill="#FFD700"/>
    <!-- Headphones band -->
    <path d="M3,16 Q3,2 20,0 Q37,2 37,16" fill="none" stroke="#555" stroke-width="2.5" stroke-linecap="round"/>
    <!-- Headphone ear cups -->
    <rect x="-1" y="12" width="7" height="10" rx="3" fill="#444" stroke="#666" stroke-width=".8"/>
    <rect x="34" y="12" width="7" height="10" rx="3" fill="#444" stroke="#666" stroke-width=".8"/>
    <!-- Little arms waving -->
    <path d="M8,36 Q2,32 0,28" fill="none" stroke="#5a9a5a" stroke-width="1.5" stroke-linecap="round"/>
    <path d="M32,36 Q38,32 40,28" fill="none" stroke="#5a9a5a" stroke-width="1.5" stroke-linecap="round"/>
    <!-- Tiny feet -->
    <ellipse cx="14" cy="48" rx="5" ry="3" fill="#90EE90" stroke="#5a9a5a" stroke-width=".8"/>
    <ellipse cx="26" cy="48" rx="5" ry="3" fill="#90EE90" stroke="#5a9a5a" stroke-width=".8"/>
  </g>

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
            "thumbnail_url": None,
            "video_id": "",
        }

    print(f"  🎶 {song['title']} — {song['artist']}")

    # Fetch and embed thumbnail as base64
    print("  Fetching album art...")
    thumb_b64 = fetch_thumbnail_b64(song["thumbnail_url"])
    if thumb_b64:
        print("  ✓ Thumbnail embedded as base64")
    else:
        print("  ⚠ Using fallback placeholder")

    # Generate SVG
    svg = generate_svg(song, thumb_b64)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    with open(OUTPUT_PATH, "w") as f:
        f.write(svg)

    print(f"  ✓ Widget saved to {OUTPUT_PATH}")
    print(f"  Size: {len(svg):,} bytes")


if __name__ == "__main__":
    main()
