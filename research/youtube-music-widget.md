# YouTube Music "Now Playing" Widget for GitHub Profile README

**Research Date:** 2026-03-02
**Status:** Research Complete

---

## TL;DR — VERDICT: ✅ AVAILABLE (with caveats) / BUILDABLE (improved version)

An existing solution exists: **[moguism/YTMusicReadme](https://github.com/moguism/YTMusicReadme)** (6 stars, last updated Nov 2025). It works — the live demo at `yt-music-readme.vercel.app` returns a valid SVG with song info. However, it's small/rough, and we can do better by forking or building our own with a cleaner design.

---

## 1. Existing Solutions Found

### moguism/YTMusicReadme ⭐ The Only One
- **Repo:** https://github.com/moguism/YTMusicReadme
- **Stars:** 6 | **Language:** Python | **Last updated:** Nov 2025
- **Live demo:** https://yt-music-readme.vercel.app/ (confirmed working — returns SVG)
- **Architecture:** Vercel serverless function → `ytmusicapi` → `get_history()` → generates SVG
- **Auth method:** Browser cookie auth (`browser.json`) + Google Cloud OAuth Client ID/Secret
- **Known issues:**
  - Design is self-admittedly rough ("not the best in the world")
  - Ships a **modified copy** of ytmusicapi (to work around Vercel's read-only filesystem for token storage)
  - YouTube Music history can lag (YTM doesn't always update history immediately)
  - GitHub camo CDN caching means the displayed song can be stale
  - Requires a **private repo** (because `browser.json` with auth cookies must be committed)
  - No themes, no customization options
  - Inspired by tthn0/Spotify-Readme

### No other YouTube Music README widgets exist
- Searched GitHub extensively with multiple query variations — YTMusicReadme is the only one.
- No GitHub Actions-based alternatives found.

---

## 2. API Landscape

### Official YouTube Data API v3
- ❌ **No "currently playing" endpoint** — unlike Spotify which has `currently-playing`
- The YouTube Data API handles videos, playlists, channels — but has zero concept of "what's playing on YouTube Music right now"
- No YouTube Music-specific official API exists at all

### Unofficial: ytmusicapi (sigma67/ytmusicapi)
- **Repo:** https://github.com/sigma67/ytmusicapi | **Version:** 1.11.5
- **The critical function:** `get_history()` — returns play history in reverse chronological order
  - Returns song title, artist, album art thumbnail, videoId, and `played` timestamp
  - This is the closest thing to "now playing" — it shows the **most recently played song**
- **Auth options:**
  1. **OAuth** (recommended): `ytmusicapi oauth` → generates `oauth.json`. Since Nov 2024, also requires Client ID + Client Secret from Google Cloud Console (TV/Limited Input device type)
  2. **Browser auth**: Copy browser cookies from a YTM session → `browser.json`. Simpler but cookies expire.
- **Token refresh:** OAuth tokens auto-refresh. Browser cookies eventually expire and need manual renewal.
- **Key limitation:** There is NO real "currently playing" detection. It's always "most recently played from history." If YTM doesn't log the play to history (which happens sometimes), the widget shows stale data.

---

## 3. How Spotify Widgets Work (for comparison)

### Spotify's Advantage
Spotify has a proper **[Web API](https://developer.spotify.com/documentation/web-api/)** with:
- `GET /v1/me/player/currently-playing` — real-time "what's playing right now"
- `GET /v1/me/player/recently-played` — recent history fallback
- OAuth 2.0 with `refresh_token` — tokens auto-refresh, no cookie hassle

### Popular Spotify widget architectures:
| Project | Hosting | Stars |
|---------|---------|-------|
| [kittinan/spotify-github-profile](https://github.com/kittinan/spotify-github-profile) | Vercel + Firebase → moved to self-hosted (Vercel free tier insufficient) | Very popular |
| [tthn0/Spotify-Readme](https://github.com/tthn0/Spotify-Readme) | PythonAnywhere (free tier) | Popular |
| [novatorem/novatorem](https://github.com/novatorem/novatorem) | Vercel | Original/classic |

### Architecture pattern (all share this):
```
GitHub README <img> tag
  → HTTP GET to serverless endpoint
    → Authenticate with stored OAuth refresh_token
    → Call Spotify API for current/recent track
    → Generate SVG with song info + base64 album art
    → Return SVG with Content-Type: image/svg+xml
```

### Can this work for YouTube Music?
**Yes, with one key difference:** Instead of "currently playing" (real-time), we use `get_history()[0]` (most recently played). The architecture is otherwise identical.

---

## 4. Feasibility: Building Our Own

### Option A: Fork & Improve YTMusicReadme
**Effort:** Low-Medium (2-4 hours)
- Fork moguism/YTMusicReadme
- Improve the SVG design (add themes like Spotify widgets have)
- Fix the bundled ytmusicapi issue (check if upstream PR was merged)
- Deploy to Vercel

### Option B: Build from Scratch (Recommended)
**Effort:** Medium (4-8 hours)
- **Better design**: Port a Spotify widget's SVG theme (e.g., tthn0's dark theme with equalizer animation)
- **Better auth**: Use OAuth flow instead of browser cookies
- **Better hosting**: Vercel serverless Python function

#### Proposed Architecture:
```
┌─────────────────────────────────────────────────────┐
│  GitHub Profile README                               │
│  <img src="https://ytm-readme.vercel.app/api" />    │
└──────────────────┬──────────────────────────────────┘
                   │ HTTP GET
                   ▼
┌─────────────────────────────────────────────────────┐
│  Vercel Serverless Function (Python)                 │
│                                                      │
│  1. Load OAuth creds from env vars                   │
│  2. ytmusicapi.YTMusic(oauth_json,                   │
│       oauth_credentials=OAuthCredentials(...))       │
│  3. history = yt.get_history()                       │
│  4. song = history[0]  # most recent                 │
│  5. Fetch album art → base64                         │
│  6. Generate SVG card (song, artist, art)            │
│  7. Return SVG (Cache-Control: no-cache)             │
└─────────────────────────────────────────────────────┘
```

#### Environment Variables Needed:
- `OAUTH_JSON` — serialized OAuth token JSON (base64 encoded)
- `CLIENT_ID` — Google Cloud OAuth Client ID
- `CLIENT_SECRET` — Google Cloud OAuth Client Secret

#### Token Refresh Challenge:
The biggest issue is that ytmusicapi's OAuth tokens need to be **written back** after refresh. On Vercel's read-only filesystem, this requires:
1. Store tokens in an external store (e.g., Vercel KV / Firebase / a simple JSON in a private gist)
2. Or: use browser auth with long-lived cookies (simpler but less reliable)
3. Or: moguism's approach — patch ytmusicapi to return the refreshed token without writing to disk, store it in env/memory

### Option C: GitHub Actions Approach
**Effort:** Medium | **Different tradeoff**
- GitHub Action runs on a cron (e.g., every 5 min)
- Calls ytmusicapi `get_history()` 
- Generates an SVG or updates README directly
- Commits the result
- **Pros:** No external hosting needed
- **Cons:** 
  - 5-min minimum cron interval (not real-time)
  - Burns GitHub Actions minutes
  - Commits spam in repo history
  - Not truly dynamic — it's a static image that updates periodically

---

## 5. Key Limitations (All Approaches)

| Limitation | Impact | Mitigation |
|-----------|--------|------------|
| No "currently playing" API | Shows last played, not what's playing right now | Acceptable — Spotify widgets also fall back to recent when nothing is playing |
| YTM history can lag | Sometimes a song you just played doesn't appear in history | None — this is a YouTube Music backend issue |
| GitHub camo CDN caching | Even if the SVG updates, GitHub may serve a cached version | Set `Cache-Control: no-cache, no-store` headers; users can force-refresh |
| OAuth token refresh on serverless | Token file needs to be written back after refresh | Use external KV store or patched ytmusicapi |
| Browser cookie auth expiry | Cookies expire after some weeks/months | Use OAuth instead (auto-refreshes) |

---

## 6. Recommendation

### 🏆 Best Path: Fork YTMusicReadme + Improve It

1. **Fork** [moguism/YTMusicReadme](https://github.com/moguism/YTMusicReadme) to a private repo
2. **Improve the SVG** — steal design from tthn0/Spotify-Readme (dark theme, equalizer bars, spinning album art)
3. **Fix token storage** — use Vercel KV (free tier: 256MB) or a Vercel env var that gets updated
4. **Set up Google Cloud OAuth** — create project, get Client ID + Secret, run `ytmusicapi oauth`
5. **Deploy to Vercel** — add env vars, deploy
6. **Add to README:** `<img src="https://your-ytm-widget.vercel.app/" />`

### Setup Steps (estimated 30-60 min):
1. Create Google Cloud project → enable YouTube Data API → create OAuth credentials (TV type)
2. Run `pip install ytmusicapi && ytmusicapi oauth` locally with the client ID/secret
3. Fork/clone YTMusicReadme → push to private GitHub repo
4. Connect to Vercel → set `CLIENT_ID`, `CLIENT_SECRET`, and `OAUTH_JSON` env vars
5. Deploy → test the URL → add `<img>` to GitHub profile README

---

## 7. Alternative: Last.fm Scrobbling Bridge

If the "history lag" issue is too annoying, there's a workaround:
- Use **[YouTube Music Desktop App](https://github.com/nicedayzhu/youtube-music)** (Electron) which supports Last.fm scrobbling
- Then use an existing **Last.fm README widget** (there are several)
- This gives you real-time scrobbling + a mature widget ecosystem
- **Downside:** Requires using the desktop app (not the web/mobile app)

---

## Sources
- https://github.com/moguism/YTMusicReadme
- https://github.com/sigma67/ytmusicapi (v1.11.5)
- https://ytmusicapi.readthedocs.io/en/stable/
- https://github.com/kittinan/spotify-github-profile
- https://github.com/tthn0/Spotify-Readme
- https://developers.google.com/youtube/v3/docs
