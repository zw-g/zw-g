# 🌍 Dynamic Weather Globe Widget for GitHub Profile README

> Research completed: 2026-03-02

## 1. Existing Weather Widgets for Profile READMEs

The ecosystem is **sparse**. No widely-adopted weather widget exists for GitHub profiles.

| Project | Stars | Tech | Notes |
|---------|-------|------|-------|
| [saumiko/weather-readme-widget](https://github.com/saumiko/weather-readme-widget) | 1 | Python/Vercel | Static SVG card, needs OpenWeatherMap API key, Vercel deployment. Not animated. |
| (no other notable projects) | — | — | The `weather-readme` topic on GitHub has **zero** public repos tagged. |

**Takeaway:** This is essentially a greenfield project — nothing off-the-shelf does what we want (animated globe + weather + alien theme). We build custom.

---

## 2. Animated Globe / Earth Generators

### Python Libraries

| Library | What it does | Pros | Cons |
|---------|-------------|------|------|
| **Cartopy** | Geospatial visualization, orthographic projection (looks like a globe) | Proper globe projection, coastlines built-in, matplotlib integration | Heavy install (needs GEOS, Proj, GDAL-like deps), slow CI setup |
| **matplotlib + Basemap** | Similar globe rendering | Mature | Basemap is **deprecated**, don't use |
| **Pillow (PIL)** | Image manipulation, frame-by-frame GIF assembly | Lightweight, pure Python, fast CI | No built-in geo projection — must pre-bake or draw manually |
| **imageio** | Assemble frames into GIF/MP4 | Simple API, pairs with any renderer | Just an assembler, not a renderer |
| [johannesuhl/globeanim](https://github.com/johannesuhl/globeanim) | Projects GeoTIFF → rotating globe GIF | Proven animated globe output | Needs GDAL (very heavy), overkill for our use case |
| **gifos** ([github-readme-terminal](https://github.com/x0rzavi/github-readme-terminal)) | Python GIF generator for profile READMEs | Great GitHub Action pattern, ANSI color support | Terminal-themed, not globe-themed |

### JavaScript / Other

| Tool | Notes |
|------|-------|
| **D3.js + Vercel** | Could render globe SVG server-side, but adds deployment complexity |
| **Three.js + Puppeteer** | Full 3D globe → screenshot frames → GIF. Very heavy for CI. |
| **CSS/SVG animations** | Native animation in SVG — no frames needed, tiny file size |

### Reference Projects (Space / Galaxy Theme)

| Project | Why it's relevant |
|---------|------------------|
| [vinimlo/galaxy-profile](https://github.com/vinimlo/galaxy-profile) | 🔥 **Best reference.** Python-generated animated SVGs with space/galaxy theme. GitHub Actions auto-regenerates every 12h. Exactly the pattern we want. |
| [Platane/snk](https://github.com/Platane/snk) | Animated SVG/GIF via GitHub Actions. Proves the cron→generate→commit pattern works at scale (very popular). |
| [yoshi389111/github-profile-3d-contrib](https://github.com/yoshi389111/github-profile-3d-contrib) | 3D profile images via GitHub Action. TypeScript-based. |

---

## 3. Free Weather APIs (No Auth Required)

### ✅ Recommended: Open-Meteo

- **URL:** `https://api.open-meteo.com/v1/forecast`
- **Auth:** None needed (free for non-commercial, <10k req/day)
- **Tested for Menlo Park:**
  ```
  GET https://api.open-meteo.com/v1/forecast?latitude=37.4529&longitude=-122.1817&current=temperature_2m,weather_code,cloud_cover,wind_speed_10m&temperature_unit=fahrenheit
  ```
- **Response (confirmed working 2026-03-02):**
  ```json
  {
    "current": {
      "temperature_2m": 53.1,
      "weather_code": 1,
      "cloud_cover": 35,
      "wind_speed_10m": 5.4
    }
  }
  ```
- **WMO Weather Codes** (used for weather_code field):
  - 0 = Clear sky ☀️
  - 1 = Mainly clear 🌤️
  - 2 = Partly cloudy ⛅
  - 3 = Overcast ☁️
  - 45, 48 = Fog 🌫️
  - 51, 53, 55 = Drizzle 🌦️
  - 61, 63, 65 = Rain 🌧️
  - 71, 73, 75 = Snow ❄️
  - 80, 81, 82 = Rain showers 🌧️
  - 95, 96, 99 = Thunderstorm ⛈️

### Also Available: wttr.in

- **URL:** `https://wttr.in/Menlo+Park?format=j1`
- **Auth:** None
- **Pros:** Simple, well-known
- **Cons:** Occasionally rate-limited, less structured than Open-Meteo

**Verdict:** Use Open-Meteo as primary (structured JSON, reliable, WMO codes map cleanly to visual states).

---

## 4. Recommended Approaches (Ranked)

### 🏆 Option A: Animated SVG Weather Globe (RECOMMENDED)

**Complexity: Medium — ~2-3 days to implement**

A Python script generates an **animated SVG** that contains:

1. **Space background** — dark (#0D1117) with twinkling star dots (CSS `@keyframes` blink)
2. **Stylized Earth circle** — gradient fill, simplified continent outlines as SVG paths, drawn in alien green (#00FF41)
3. **Glow effect** — SVG `<filter>` with purple (#8B5CF6) feGaussianBlur around the globe edge
4. **Location marker** — pulsing dot on California's position
5. **Weather effects** — animated overlays based on weather_code:
   - ☀️ Clear: golden rays radiating from behind the globe
   - ☁️ Cloudy: drifting cloud shapes (CSS translateX animation)
   - 🌧️ Rain: falling droplet particles (CSS translateY animation)
   - 🌫️ Fog: semi-transparent overlay pulse
6. **Data overlay** — temperature, condition text, "Menlo Park, CA" label
7. **Alien accents** — small alien emoji or green circuit-board patterns in corners

**Why SVG over GIF:**
- SVGs support **CSS animations natively** → smooth, infinite loop, no frame assembly
- File size: **5-20 KB** vs 200KB-2MB for GIF
- Crisp at any resolution (vector)
- GitHub renders SVG in READMEs natively (via `<img>` tag or raw reference)
- No heavy dependencies (Pillow/Cartopy/imageio not needed)

**Dependencies:** Just Python + `requests` (to fetch weather). SVG is generated as a string template.

---

### Option B: Pillow-Rendered Animated GIF Globe

**Complexity: Medium-High — ~3-5 days**

1. Pre-draw a set of **stylized globe frames** (e.g., 24 frames of slow rotation) using Pillow
2. Use a simplified world map (SVG → rasterize → apply alien color palette)
3. Overlay weather effects as composited layers per frame
4. Assemble with `imageio` or Pillow's `save(append_images=...)`

**Pros:** True GIF, universally rendered, more "traditional" animated look  
**Cons:** Larger file size, needs careful optimization (color palette, frame count), more code

---

### Option C: Cartopy Full 3D Globe GIF

**Complexity: High — ~5-7 days**

1. Use Cartopy with Orthographic projection centered on Menlo Park (37.45°N, 122.18°W)
2. Render 36 frames with slow rotation (10° per frame)
3. Custom styling: dark ocean (#0D1117), green landmass (#00FF41), purple gridlines (#8B5CF6)
4. Weather overlay on each frame
5. Assemble into GIF

**Pros:** Most realistic globe look  
**Cons:** Cartopy install in CI is painful (needs `apt-get install libgeos-dev libproj-dev`), slow generation (~30-60s), large output GIF

---

## 5. Color Palette — Alien Theme

```
Primary Green:    #00FF41  (matrix/alien green — for continents, text, accents)
Purple Glow:      #8B5CF6  (for aura, gridlines, weather labels)
Dark Background:  #0D1117  (GitHub dark mode bg — for space)
Star White:       #E6EDF3  (dim white for star dots)
Warm Accent:      #FFD700  (golden — for sun/clear weather rays)
Rain Blue:        #38BDF8  (sky blue — for rain droplets)
Fog Gray:         #6B7280  (muted — for fog overlay)
Cloud White:      #D1D5DB  (soft white — for cloud shapes)
Deep Purple:      #4C1D95  (dark purple — for globe shadow/depth)
```

The globe itself should look like a **hacker's Earth** — wireframe or simplified green-on-black continents, with a purple atmospheric glow. Think "alien mothership monitoring Earth's weather."

---

## 6. Sample GitHub Action Workflow

```yaml
name: Update Weather Globe

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
  workflow_dispatch:  # Manual trigger

permissions:
  contents: write

jobs:
  update-weather:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Generate weather globe
        run: python scripts/generate_weather_globe.py

      - name: Commit and push
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "Weather Globe Bot"
          git add assets/weather-globe.svg
          # Only commit if file changed
          git diff --staged --quiet || git commit -m "🌍 Update weather globe [skip ci]"
          git push
```

### Script outline: `scripts/generate_weather_globe.py`

```python
import requests
import json
from pathlib import Path

# 1. Fetch weather
OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.4529&longitude=-122.1817"
    "&current=temperature_2m,weather_code,cloud_cover,wind_speed_10m"
    "&temperature_unit=fahrenheit"
)
weather = requests.get(OPEN_METEO_URL).json()["current"]

# 2. Map weather_code → visual state
code = weather["weather_code"]
if code <= 1:
    state = "clear"
elif code <= 3:
    state = "cloudy"
elif code in (45, 48):
    state = "foggy"
elif code in range(51, 68):
    state = "rainy"
elif code in range(71, 78):
    state = "snowy"
elif code >= 80:
    state = "stormy"
else:
    state = "clear"

temp = round(weather["temperature_2m"])

# 3. Generate SVG with weather-specific animations
svg = generate_svg(state=state, temp=temp, cloud_cover=weather["cloud_cover"])

# 4. Write to assets/
Path("assets/weather-globe.svg").write_text(svg)
print(f"Generated: {state}, {temp}°F")
```

### README usage:

```markdown
<img src="assets/weather-globe.svg" alt="Weather Globe" width="200" />
```

Place it side-by-side with the alien GIF using an HTML table or flex layout:

```markdown
<p align="center">
  <img src="assets/alien.gif" width="200" />
  <img src="assets/weather-globe.svg" width="200" />
</p>
```

---

## 7. Implementation Plan Summary

| Step | Task | Est. Time |
|------|------|-----------|
| 1 | Design SVG template with globe shape, continents (simplified paths), and glow filter | 2-3 hrs |
| 2 | Add CSS animations for stars, weather overlays (clear/cloudy/rainy/foggy) | 2-3 hrs |
| 3 | Python script: fetch Open-Meteo → inject data into SVG template | 1 hr |
| 4 | Test all weather states with mock data | 1 hr |
| 5 | Set up GitHub Action workflow | 30 min |
| 6 | Style matching with alien GIF (review alien.gif, adjust colors) | 1 hr |
| 7 | Test in actual README rendering | 30 min |
| **Total** | | **~8-10 hrs** |

---

## 8. Key Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| GitHub caches SVG aggressively | Use `?v=timestamp` query param or reference via raw.githubusercontent.com |
| GitHub sanitizes SVG (strips `<script>`, some CSS) | Only use `<style>` with `@keyframes` — these survive GitHub's sanitizer. Verified by galaxy-profile and snk projects. |
| SVG animations don't render in GitHub mobile app | Provide a `<noscript>` fallback or static PNG alternative |
| Open-Meteo goes down | Fallback: cache last known weather in a JSON file; use wttr.in as backup API |
| Globe continent paths are complex | Use ultra-simplified world map (just major landmass outlines, ~50 path points total) |

---

## 9. Final Recommendation

**Go with Option A: Animated SVG Weather Globe.**

It's the sweet spot of visual impact vs. implementation complexity:
- No heavy dependencies (just `requests`)
- Tiny file size (~10KB)
- Smooth CSS animations (not choppy GIF frames)
- Matches the alien aesthetic perfectly (green wireframe Earth on dark space bg)
- Same pattern proven by galaxy-profile and snk (thousands of users)

If Papa wants a more photorealistic rotating globe later, we can upgrade to Option B (Pillow GIF) — but start with SVG for the best effort-to-wow ratio.
