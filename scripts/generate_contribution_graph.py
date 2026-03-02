#!/usr/bin/env python3
"""
Generate animated contribution graph SVG with alien spaceship roller coaster.
The alien rides along the commit activity curve like a roller coaster, with
expressions that change based on the trend (excited when surging, scared when
dropping, bored when flat).

Fetches real contribution data from GitHub GraphQL API for user zw-g.
Falls back to hardcoded data when no GITHUB_TOKEN is available.
"""

import json
import math
import os
import sys
from datetime import datetime, timezone, timedelta

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    HAS_REQUESTS = False

# ── Config ──────────────────────────────────────────────────────────────────
USERNAME = "zw-g"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(REPO_DIR, "assets")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "contribution-rollercoaster.svg")

# Hardcoded fallback data (52 weeks, roughly matching zw-g's actual pattern)
FALLBACK_DATA = [
    0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    2, 1, 0, 3, 2, 4, 5, 8, 12, 15, 20, 8,
]

# ── Chart Dimensions ────────────────────────────────────────────────────────
SVG_W = 800
SVG_H = 200
PAD_L = 50       # left padding (room for y-axis)
PAD_R = 25       # right padding
PAD_T = 40       # top padding (title + spaceship headroom)
PAD_B = 25       # bottom padding (month labels)
CHART_W = SVG_W - PAD_L - PAD_R   # 725
CHART_H = SVG_H - PAD_T - PAD_B   # 135

# ── Colors ──────────────────────────────────────────────────────────────────
C_BG = "#0D1117"
C_LINE = "#90EE90"
C_TEXT = "#8B949E"
C_TITLE = "#90EE90"
C_GRID = "rgba(255,255,255,0.06)"
C_ALIEN = "#90EE90"
C_ALIEN_DARK = "#6BC56B"
C_ACCENT = "#FFD700"


# ═══════════════════════════════════════════════════════════════════════════
#  DATA FETCHING
# ═══════════════════════════════════════════════════════════════════════════

def fetch_contributions(username):
    """Fetch weekly contribution counts from GitHub GraphQL API."""
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        print("⚠ No GITHUB_TOKEN found, using fallback data", file=sys.stderr)
        return None

    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({"query": query, "variables": {"username": username}})

    try:
        if HAS_REQUESTS:
            resp = requests.post(
                "https://api.github.com/graphql",
                headers=headers,
                data=payload,
                timeout=15,
            )
            data = resp.json()
        else:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=payload.encode(),
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())

        weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        weekly_totals = []
        for week in weeks:
            total = sum(day["contributionCount"] for day in week["contributionDays"])
            weekly_totals.append(total)

        # Keep last 52 weeks
        result = weekly_totals[-52:] if len(weekly_totals) > 52 else weekly_totals
        print(f"✓ Fetched {len(result)} weeks of data for {username}", file=sys.stderr)
        return result

    except Exception as e:
        print(f"✗ Error fetching contributions: {e}", file=sys.stderr)
        return None


# ═══════════════════════════════════════════════════════════════════════════
#  GEOMETRY — Points & Smooth Paths
# ═══════════════════════════════════════════════════════════════════════════

def compute_points(data):
    """Convert weekly counts to (x, y) chart coordinates."""
    n = len(data)
    max_val = max(data) if max(data) > 0 else 1
    points = []
    for i, val in enumerate(data):
        x = PAD_L + (i / max(n - 1, 1)) * CHART_W
        y = PAD_T + CHART_H - (val / max_val) * CHART_H
        points.append((round(x, 1), round(y, 1)))
    return points, max_val


def smooth_path(points):
    """Generate smooth SVG cubic-bezier path via Catmull-Rom interpolation."""
    if len(points) < 2:
        return ""

    d = f"M{points[0][0]},{points[0][1]}"
    tension = 5  # lower = more curvy

    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[min(len(points) - 1, i + 1)]
        p3 = points[min(len(points) - 1, i + 2)]

        cp1x = round(p1[0] + (p2[0] - p0[0]) / tension, 1)
        cp1y = round(p1[1] + (p2[1] - p0[1]) / tension, 1)
        cp2x = round(p2[0] - (p3[0] - p1[0]) / tension, 1)
        cp2y = round(p2[1] - (p3[1] - p1[1]) / tension, 1)

        d += f" C{cp1x},{cp1y} {cp2x},{cp2y} {p2[0]},{p2[1]}"

    return d


def area_path(points):
    """Generate closed area path for gradient fill beneath the curve."""
    line = smooth_path(points)
    last_x = points[-1][0]
    first_x = points[0][0]
    bottom = PAD_T + CHART_H
    return f"{line} L{last_x},{bottom} L{first_x},{bottom}Z"


# ═══════════════════════════════════════════════════════════════════════════
#  EXPRESSION LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def determine_expression(data):
    """
    Determine alien expression from the recent commit trend.
      Trending up  → excited  (things are popping off!)
      Flat         → bored    (zzz...)
      Trending down→ scared   (oh no, the drop!)
    """
    if len(data) < 8:
        return "bored"

    recent = data[-4:]
    prev = data[-8:-4]
    r_avg = sum(recent) / len(recent)
    p_avg = sum(prev) / len(prev)

    if p_avg == 0 and r_avg == 0:
        return "bored"
    if p_avg == 0:
        return "excited"  # went from nothing to something

    ratio = r_avg / p_avg
    if ratio > 1.25:
        return "excited"
    elif ratio < 0.75:
        return "scared"
    else:
        return "bored"


# ═══════════════════════════════════════════════════════════════════════════
#  SVG BUILDING BLOCKS
# ═══════════════════════════════════════════════════════════════════════════

def svg_stars():
    """Twinkling background stars (deterministic positions)."""
    seeds = [
        (45, 14), (120, 28), (198, 9), (275, 22), (348, 15),
        (415, 27), (502, 11), (568, 32), (642, 16), (712, 24),
        (768, 10), (88, 34), (162, 19), (242, 7), (318, 30),
        (388, 12), (458, 29), (528, 17), (598, 26), (678, 8),
        (748, 28), (58, 46), (192, 52), (335, 48), (472, 44),
        (618, 50), (755, 42), (110, 58), (380, 56), (550, 62),
    ]
    lines = []
    for idx, (sx, sy) in enumerate(seeds):
        r = round(0.6 + (idx % 3) * 0.3, 1)
        delay = round((idx * 0.37) % 3.5, 1)
        opacity = round(0.12 + (idx % 4) * 0.06, 2)
        lines.append(
            f'    <circle cx="{sx}" cy="{sy}" r="{r}" '
            f'fill="white" class="star" style="animation-delay:{delay}s;opacity:{opacity}"/>'
        )
    return "\n".join(lines)


def svg_gridlines(max_val):
    """Subtle horizontal grid lines."""
    lines = []
    # 4 grid lines at 25%, 50%, 75%, 100% of max
    for frac in [0.25, 0.5, 0.75]:
        gy = round(PAD_T + CHART_H * (1 - frac), 1)
        val = round(max_val * frac)
        lines.append(
            f'    <line x1="{PAD_L}" y1="{gy}" x2="{SVG_W - PAD_R}" y2="{gy}" '
            f'stroke="{C_GRID}" stroke-width="0.5" stroke-dasharray="3,4"/>'
        )
        # Small value label on left
        lines.append(
            f'    <text x="{PAD_L - 6}" y="{gy + 3}" fill="{C_TEXT}" '
            f'font-family="\'Segoe UI\',system-ui,sans-serif" font-size="8" '
            f'text-anchor="end" opacity="0.5">{val}</text>'
        )
    return "\n".join(lines)


def svg_month_labels(n_weeks):
    """Month labels along the x-axis."""
    now = datetime.now()
    start_date = now - timedelta(weeks=n_weeks)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    labels = []
    seen = set()

    # Walk through each month boundary, starting from start month
    d = start_date.replace(day=1)
    while d <= now + timedelta(days=31):
        # How many weeks from start_date?
        weeks_from_start = (d - start_date).days / 7
        x = PAD_L + (weeks_from_start / max(n_weeks - 1, 1)) * CHART_W
        month_key = (d.year, d.month)
        if month_key not in seen and PAD_L - 10 <= x <= SVG_W - PAD_R + 10:
            seen.add(month_key)
            labels.append(
                f'    <text x="{x:.0f}" y="{SVG_H - 8}" fill="{C_TEXT}" '
                f'font-family="\'Segoe UI\',system-ui,sans-serif" font-size="9" '
                f'text-anchor="middle">{months[d.month - 1]}</text>'
            )
        # Next month
        if d.month == 12:
            d = d.replace(year=d.year + 1, month=1)
        else:
            d = d.replace(month=d.month + 1)

    return "\n".join(labels)


def svg_data_dots(points, data):
    """Small dots at non-zero data points for visual weight."""
    dots = []
    for i, (x, y) in enumerate(points):
        if data[i] > 0:
            r = round(min(1.2 + data[i] * 0.08, 2.5), 1)
            dots.append(
                f'    <circle cx="{x}" cy="{y}" r="{r}" fill="{C_LINE}" opacity="0.6"/>'
            )
    return "\n".join(dots)


# ── Alien Expressions ───────────────────────────────────────────────────────

def svg_alien_excited():
    """Excited alien — wide sparkly eyes, big open mouth, blush. WHEEE!"""
    return """
    <!-- Alien head (mint green, oversized like the GIF) -->
    <ellipse cx="0" cy="-7" rx="6.5" ry="6" fill="{c}" stroke="{cd}" stroke-width="0.5"/>
    <!-- Wide excited eyes (big almond shapes like the GIF) -->
    <ellipse cx="-2.5" cy="-8.5" rx="2.5" ry="2.8" fill="white" stroke="#333" stroke-width="0.2"/>
    <ellipse cx="2.5" cy="-8.5" rx="2.5" ry="2.8" fill="white" stroke="#333" stroke-width="0.2"/>
    <ellipse cx="-2.3" cy="-8" rx="1.5" ry="1.7" fill="#111"/>
    <ellipse cx="2.7" cy="-8" rx="1.5" ry="1.7" fill="#111"/>
    <!-- Eye sparkles (like the daisy highlights in the GIF) -->
    <circle cx="-1.5" cy="-9" r="0.7" fill="white"/>
    <circle cx="3.4" cy="-9" r="0.7" fill="white"/>
    <circle cx="-2.8" cy="-7.5" r="0.4" fill="white"/>
    <circle cx="2" cy="-7.5" r="0.4" fill="white"/>
    <!-- Big excited open mouth -->
    <ellipse cx="0" cy="-3.5" rx="2.2" ry="1.6" fill="#2D2D48" stroke="#1a1a30" stroke-width="0.2"/>
    <!-- Tiny tongue -->
    <ellipse cx="0.4" cy="-2.5" rx="1" ry="0.6" fill="#FF8B8B"/>
    <!-- Rosy blush cheeks -->
    <ellipse cx="-4.5" cy="-5.5" rx="1.3" ry="0.7" fill="#FF8B8B" opacity="0.4"/>
    <ellipse cx="4.5" cy="-5.5" rx="1.3" ry="0.7" fill="#FF8B8B" opacity="0.4"/>
    <!-- Tiny raised hands (excitement!) -->
    <circle cx="-8" cy="-9" r="1.5" fill="{c}" stroke="{cd}" stroke-width="0.3"/>
    <circle cx="8" cy="-9" r="1.5" fill="{c}" stroke="{cd}" stroke-width="0.3"/>
""".format(c=C_ALIEN, cd=C_ALIEN_DARK)


def svg_alien_scared():
    """Scared alien — huge wide eyes, tiny worried mouth, sweat drop."""
    return """
    <!-- Alien head -->
    <ellipse cx="0" cy="-7" rx="6.5" ry="6" fill="{c}" stroke="{cd}" stroke-width="0.5"/>
    <!-- Huge scared eyes -->
    <ellipse cx="-2.5" cy="-8.5" rx="2.7" ry="3" fill="white" stroke="#333" stroke-width="0.2"/>
    <ellipse cx="2.5" cy="-8.5" rx="2.7" ry="3" fill="white" stroke="#333" stroke-width="0.2"/>
    <circle cx="-2.5" cy="-7.8" r="1.3" fill="#111"/>
    <circle cx="2.5" cy="-7.8" r="1.3" fill="#111"/>
    <!-- Tiny scared pupils -->
    <circle cx="-1.9" cy="-8.5" r="0.5" fill="white"/>
    <circle cx="3.1" cy="-8.5" r="0.5" fill="white"/>
    <!-- Worried wavy mouth -->
    <path d="M-1.8,-3.5 Q-0.9,-4.5 0,-3.8 Q0.9,-3.2 1.8,-3.8" fill="none" stroke="#2D2D48" stroke-width="0.8" stroke-linecap="round"/>
    <!-- Sweat drop -->
    <path d="M6,-10.5 Q6.5,-12 6,-13 Q5.5,-12 6,-10.5Z" fill="#87CEEB" opacity="0.7"/>
    <!-- Grabbing the rim (scared!) -->
    <ellipse cx="-7" cy="-1" rx="1.5" ry="1" fill="{c}" stroke="{cd}" stroke-width="0.3"/>
    <ellipse cx="7" cy="-1" rx="1.5" ry="1" fill="{c}" stroke="{cd}" stroke-width="0.3"/>
""".format(c=C_ALIEN, cd=C_ALIEN_DARK)


def svg_alien_bored():
    """Bored alien — half-closed droopy eyes, flat mouth, sleepy Z's."""
    return """
    <!-- Alien head -->
    <ellipse cx="0" cy="-7" rx="6.5" ry="6" fill="{c}" stroke="{cd}" stroke-width="0.5"/>
    <!-- Half-closed bored eyes -->
    <ellipse cx="-2.5" cy="-7.5" rx="2.4" ry="1.2" fill="white" stroke="#333" stroke-width="0.2"/>
    <ellipse cx="2.5" cy="-7.5" rx="2.4" ry="1.2" fill="white" stroke="#333" stroke-width="0.2"/>
    <ellipse cx="-2.5" cy="-7.2" rx="1.3" ry="0.8" fill="#111"/>
    <ellipse cx="2.5" cy="-7.2" rx="1.3" ry="0.8" fill="#111"/>
    <!-- Droopy eyelids -->
    <path d="M-4.9,-8.2 Q-2.5,-7.2 0,-8.2" fill="{c}" opacity="0.7"/>
    <path d="M0,-8.2 Q2.5,-7.2 4.9,-8.2" fill="{c}" opacity="0.7"/>
    <!-- Flat bored mouth -->
    <line x1="-1.8" y1="-3.5" x2="1.8" y2="-3.5" stroke="#2D2D48" stroke-width="0.9" stroke-linecap="round"/>
    <!-- Sleepy Z's floating up -->
    <text x="7" y="-10" fill="{t}" font-family="sans-serif" font-size="6" font-weight="bold" opacity="0.5">z</text>
    <text x="10" y="-14" fill="{t}" font-family="sans-serif" font-size="5" font-weight="bold" opacity="0.3">z</text>
    <text x="12" y="-17" fill="{t}" font-family="sans-serif" font-size="4" font-weight="bold" opacity="0.15">z</text>
""".format(c=C_ALIEN, cd=C_ALIEN_DARK, t=C_TEXT)


def svg_spaceship(expression, ship_x, ship_y):
    """Complete spaceship group with alien, glow, speed lines."""
    face_fn = {
        "excited": svg_alien_excited,
        "scared": svg_alien_scared,
        "bored": svg_alien_bored,
    }
    alien_svg = face_fn.get(expression, svg_alien_bored)()

    # Offset: position spaceship so disc base sits ON the line point
    # Disc center is at local y=2, so shift up by 2
    adj_y = ship_y - 2

    return f"""
  <!-- ═══ ALIEN SPACESHIP ═══ -->
  <!-- Outer group: positioning only (SVG transform) -->
  <g transform="translate({ship_x:.1f},{adj_y:.1f})">
    <!-- Inner group: CSS bobbing animation -->
    <g class="spaceship">

      <!-- Speed/motion lines -->
      <line class="speed-line" x1="-23" y1="-5" x2="-36" y2="-5"
            stroke="{C_LINE}" stroke-width="1" opacity="0.4"/>
      <line class="speed-line" x1="-21" y1="0" x2="-40" y2="0"
            stroke="{C_LINE}" stroke-width="1.3" opacity="0.5"
            style="animation-delay:0.3s"/>
      <line class="speed-line" x1="-22" y1="-10" x2="-33" y2="-10"
            stroke="{C_LINE}" stroke-width="0.8" opacity="0.3"
            style="animation-delay:0.7s"/>

      <!-- Beam / glow underneath -->
      <ellipse class="glow" cx="0" cy="7" rx="12" ry="5"
               fill="{C_LINE}" opacity="0.15"/>
      <ellipse class="glow" cx="0" cy="6" rx="7" ry="3"
               fill="{C_LINE}" opacity="0.1"
               style="animation-delay:0.5s"/>

      <!-- UFO disc body -->
      <ellipse cx="0" cy="2" rx="17" ry="5.5" fill="url(#ufoBody)"
               stroke="#555" stroke-width="0.4"/>
      <!-- Rim highlight -->
      <ellipse cx="0" cy="0.5" rx="14" ry="2.8" fill="#C8C8C8" opacity="0.5"/>
      <!-- Rim lights -->
      <circle cx="-10" cy="2.5" r="1" fill="{C_LINE}" opacity="0.6"/>
      <circle cx="-5" cy="3.5" r="0.8" fill="{C_ACCENT}" opacity="0.5"/>
      <circle cx="0" cy="4" r="1" fill="{C_LINE}" opacity="0.6"/>
      <circle cx="5" cy="3.5" r="0.8" fill="{C_ACCENT}" opacity="0.5"/>
      <circle cx="10" cy="2.5" r="1" fill="{C_LINE}" opacity="0.6"/>

      <!-- Glass dome -->
      <path d="M-9,0 Q-10,-14 0,-17 Q10,-14 9,0"
            fill="url(#dome)" stroke="{C_LINE}" stroke-width="0.4" opacity="0.7"/>
      <!-- Dome highlight arc -->
      <path d="M-5,-13 Q0,-16 5,-13" fill="none" stroke="white"
            stroke-width="0.5" opacity="0.25"/>

      <!-- Alien inside dome -->
{alien_svg}
    </g>
  </g>"""


# ═══════════════════════════════════════════════════════════════════════════
#  CSS STYLES
# ═══════════════════════════════════════════════════════════════════════════

CSS = """
    /* ── Stars ── */
    @keyframes twinkle {
      0%, 100% { opacity: 0.08; }
      50% { opacity: 0.55; }
    }
    .star { animation: twinkle 3s ease-in-out infinite; }

    /* ── Spaceship bob ── */
    @keyframes bob {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-5px); }
    }
    .spaceship { animation: bob 2.8s ease-in-out infinite; }

    /* ── Green glow pulse ── */
    @keyframes glow-pulse {
      0%, 100% { opacity: 0.12; }
      50% { opacity: 0.3; }
    }
    .glow { animation: glow-pulse 2s ease-in-out infinite; }

    /* ── Speed lines ── */
    @keyframes dash {
      0% { opacity: 0.5; transform: translateX(0); }
      100% { opacity: 0; transform: translateX(-8px); }
    }
    .speed-line {
      stroke-linecap: round;
      animation: dash 1.2s linear infinite;
    }

    /* ── Line draw ── */
    @keyframes draw-line {
      to { stroke-dashoffset: 0; }
    }
    .chart-line {
      stroke-dasharray: 2200;
      stroke-dashoffset: 2200;
      animation: draw-line 2.5s ease-out forwards;
    }

    /* ── Area fade in ── */
    @keyframes fade-area {
      0% { opacity: 0; }
      100% { opacity: 1; }
    }
    .chart-area {
      opacity: 0;
      animation: fade-area 1s ease-out 1.8s forwards;
    }
"""


# ═══════════════════════════════════════════════════════════════════════════
#  SVG ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════

def generate_svg(data, expression=None):
    """Assemble the complete contribution-rollercoaster SVG."""

    # Normalize data to 52 weeks
    if len(data) < 52:
        data = [0] * (52 - len(data)) + data
    elif len(data) > 52:
        data = data[-52:]

    if expression is None:
        expression = determine_expression(data)

    points, max_val = compute_points(data)
    curve = smooth_path(points)
    area = area_path(points)

    # ── Spaceship position ──
    # Place at the latest data point (current position on the coaster)
    ship_idx = len(data) - 1
    # If there's a peak within the last 6 weeks, ride it instead (more dramatic)
    peak_val = max(data)
    peak_idx = len(data) - 1 - data[::-1].index(peak_val)
    if peak_idx >= len(data) - 6:
        ship_idx = peak_idx

    ship_x = points[ship_idx][0]
    ship_y = points[ship_idx][1]

    # ── Build SVG ──
    stars = svg_stars()
    grid = svg_gridlines(max_val)
    months = svg_month_labels(len(data))
    dots = svg_data_dots(points, data)
    spaceship = svg_spaceship(expression, ship_x, ship_y)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SVG_H}" viewBox="0 0 {SVG_W} {SVG_H}">
  <style>{CSS}  </style>

  <defs>
    <!-- Area gradient -->
    <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{C_LINE}" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="{C_LINE}" stop-opacity="0.02"/>
    </linearGradient>
    <!-- UFO body metallic gradient -->
    <linearGradient id="ufoBody" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#E0E0E0"/>
      <stop offset="40%" stop-color="#B0B0B0"/>
      <stop offset="100%" stop-color="#707070"/>
    </linearGradient>
    <!-- Dome glass gradient -->
    <radialGradient id="dome" cx="0.5" cy="0.3" r="0.7">
      <stop offset="0%" stop-color="{C_LINE}" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="{C_LINE}" stop-opacity="0.08"/>
    </radialGradient>
  </defs>

  <!-- ── Background ── -->
  <rect width="{SVG_W}" height="{SVG_H}" fill="{C_BG}" rx="10"/>

  <!-- ── Stars ── -->
{stars}

  <!-- ── Title ── -->
  <text x="{PAD_L}" y="24" fill="{C_TITLE}"
        font-family="'Segoe UI',system-ui,-apple-system,sans-serif"
        font-size="13" font-weight="600">Commit Activity</text>

  <!-- ── Grid lines ── -->
{grid}

  <!-- ── Baseline ── -->
  <line x1="{PAD_L}" y1="{PAD_T + CHART_H}" x2="{SVG_W - PAD_R}" y2="{PAD_T + CHART_H}"
        stroke="{C_GRID}" stroke-width="0.5"/>

  <!-- ── Area fill ── -->
  <path class="chart-area" d="{area}" fill="url(#areaGrad)"/>

  <!-- ── Smooth curve ── -->
  <path class="chart-line" d="{curve}" fill="none"
        stroke="{C_LINE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- ── Data dots ── -->
{dots}

  <!-- ── Peak marker ── -->
  <circle cx="{points[peak_idx][0]}" cy="{points[peak_idx][1]}" r="3"
          fill="{C_LINE}" opacity="0.8"/>
  <circle cx="{points[peak_idx][0]}" cy="{points[peak_idx][1]}" r="5"
          fill="{C_LINE}" opacity="0.15"/>

  <!-- ── Month labels ── -->
{months}
{spaceship}
</svg>"""

    return svg


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    # Try fetching real data, fall back to hardcoded
    data = fetch_contributions(USERNAME)
    if data is None:
        print("Using fallback (hardcoded) data", file=sys.stderr)
        data = list(FALLBACK_DATA)

    expression = determine_expression(data)
    svg = generate_svg(data, expression)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)

    max_val = max(data) if data else 0
    print(f"✓ Saved → {OUTPUT_FILE}", file=sys.stderr)
    print(f"  {len(data)} weeks | max={max_val} | expression={expression}", file=sys.stderr)


if __name__ == "__main__":
    main()
