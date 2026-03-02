#!/usr/bin/env python3
"""
Generate a cute hand-drawn weather globe SVG for GitHub profile.
Fetches real weather data from Open-Meteo API for Menlo Park, CA.
"""

import json
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
LAT = 37.4529
LON = -122.1817
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "weather-globe.svg")

# WMO Weather codes → condition categories
WMO_CONDITIONS = {
    0: "clear",
    1: "clear", 2: "cloudy", 3: "cloudy",
    45: "fog", 48: "fog",
    51: "drizzle", 53: "drizzle", 55: "drizzle",
    56: "drizzle", 57: "drizzle",
    61: "rain", 63: "rain", 65: "rain",
    66: "rain", 67: "rain",
    71: "snow", 73: "snow", 75: "snow",
    77: "snow",
    80: "rain", 81: "rain", 82: "rain",
    85: "snow", 86: "snow",
    95: "storm", 96: "storm", 99: "storm",
}

WMO_LABELS = {
    0: "Clear Sky",
    1: "Mostly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 48: "Foggy",
    51: "Light Drizzle", 53: "Drizzle", 55: "Heavy Drizzle",
    56: "Freezing Drizzle", 57: "Freezing Drizzle",
    61: "Light Rain", 63: "Rain", 65: "Heavy Rain",
    66: "Freezing Rain", 67: "Freezing Rain",
    71: "Light Snow", 73: "Snow", 75: "Heavy Snow",
    77: "Snow Grains",
    80: "Light Showers", 81: "Showers", 82: "Heavy Showers",
    85: "Snow Showers", 86: "Heavy Snow Showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def fetch_weather():
    """Fetch current weather from Open-Meteo API."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={LAT}&longitude={LON}"
        f"&current=temperature_2m,weather_code,is_day"
        f"&temperature_unit=fahrenheit"
        f"&timezone=America/Los_Angeles"
    )
    try:
        if HAS_REQUESTS:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "weather-globe/1.0"})
            resp.raise_for_status()
            data = resp.json()
        else:
            req = urllib.request.Request(url, headers={"User-Agent": "weather-globe/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
        current = data["current"]
        return {
            "temp_f": round(current["temperature_2m"]),
            "weather_code": current["weather_code"],
            "is_day": current["is_day"],
            "condition": WMO_CONDITIONS.get(current["weather_code"], "clear"),
            "label": WMO_LABELS.get(current["weather_code"], "Unknown"),
        }
    except Exception as e:
        print(f"⚠ Weather fetch failed: {e}. Using fallback.", file=sys.stderr)
        return {
            "temp_f": 65,
            "weather_code": 0,
            "is_day": 1,
            "condition": "clear",
            "label": "Clear Sky",
        }


def weather_overlay(condition, is_day):
    """Generate doodle-style weather overlay SVG elements."""
    elements = []

    if condition == "clear":
        if is_day:
            # Cute sun with doodly rays peeking from top-right
            elements.append("""
    <!-- sun -->
    <circle cx="155" cy="45" r="14" fill="#FFD700" stroke="#000" stroke-width="2.5"/>
    <line x1="155" y1="24" x2="155" y2="18" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    <line x1="170" y1="30" x2="175" y2="25" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    <line x1="176" y1="45" x2="182" y2="45" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    <line x1="140" y1="30" x2="135" y2="25" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    <line x1="170" y1="60" x2="175" y2="65" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    <line x1="140" y1="60" x2="135" y2="65" stroke="#000" stroke-width="2" stroke-linecap="round"/>""")
        else:
            # Cute crescent moon
            elements.append("""
    <!-- moon -->
    <circle cx="155" cy="42" r="12" fill="#FFD700" stroke="#000" stroke-width="2.5"/>
    <circle cx="161" cy="38" r="10" fill="#F0F4FF" stroke="none"/>""")

    elif condition == "cloudy":
        # Cute puffy doodle clouds
        elements.append("""
    <!-- clouds -->
    <g class="cloud-float">
      <circle cx="138" cy="38" r="10" fill="#fff" stroke="#000" stroke-width="2"/>
      <circle cx="152" cy="34" r="13" fill="#fff" stroke="#000" stroke-width="2"/>
      <circle cx="166" cy="38" r="10" fill="#fff" stroke="#000" stroke-width="2"/>
      <rect x="132" y="38" width="40" height="10" rx="4" fill="#fff" stroke="none"/>
      <line x1="132" y1="42" x2="172" y2="42" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    </g>""")
        if is_day:
            elements.append("""
    <circle cx="125" cy="40" r="10" fill="#FFD700" stroke="#000" stroke-width="2" opacity="0.7"/>""")

    elif condition in ("rain", "drizzle"):
        # Cloud + rain drops
        elements.append("""
    <!-- rain cloud -->
    <g>
      <circle cx="100" cy="38" r="9" fill="#D3D3D3" stroke="#000" stroke-width="2"/>
      <circle cx="112" cy="33" r="12" fill="#D3D3D3" stroke="#000" stroke-width="2"/>
      <circle cx="124" cy="38" r="9" fill="#D3D3D3" stroke="#000" stroke-width="2"/>
      <rect x="94" y="38" width="36" height="8" rx="3" fill="#D3D3D3" stroke="none"/>
      <line x1="94" y1="42" x2="130" y2="42" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    </g>
    <!-- rain drops -->
    <g class="rain-fall">
      <line x1="100" y1="48" x2="98" y2="56" stroke="#87CEEB" stroke-width="2" stroke-linecap="round"/>
      <line x1="110" y1="50" x2="108" y2="58" stroke="#87CEEB" stroke-width="2" stroke-linecap="round"/>
      <line x1="120" y1="48" x2="118" y2="56" stroke="#87CEEB" stroke-width="2" stroke-linecap="round"/>
    </g>""")

    elif condition == "snow":
        # Cloud + snowflakes
        elements.append("""
    <!-- snow cloud -->
    <g>
      <circle cx="100" cy="38" r="9" fill="#E8E8E8" stroke="#000" stroke-width="2"/>
      <circle cx="112" cy="33" r="12" fill="#E8E8E8" stroke="#000" stroke-width="2"/>
      <circle cx="124" cy="38" r="9" fill="#E8E8E8" stroke="#000" stroke-width="2"/>
      <rect x="94" y="38" width="36" height="8" rx="3" fill="#E8E8E8" stroke="none"/>
      <line x1="94" y1="42" x2="130" y2="42" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    </g>
    <!-- snowflakes -->
    <g class="snow-fall">
      <text x="99" y="55" font-size="8" fill="#87CEEB">❄</text>
      <text x="111" y="58" font-size="6" fill="#87CEEB">❄</text>
      <text x="121" y="54" font-size="7" fill="#87CEEB">❄</text>
    </g>""")

    elif condition == "fog":
        # Wavy fog lines
        elements.append("""
    <!-- fog lines -->
    <g opacity="0.5" class="fog-drift">
      <path d="M60,60 Q80,56 100,60 Q120,64 140,60" fill="none" stroke="#B0B0B0" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M50,72 Q75,68 100,72 Q125,76 150,72" fill="none" stroke="#B0B0B0" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M65,84 Q85,80 105,84 Q125,88 145,84" fill="none" stroke="#B0B0B0" stroke-width="2" stroke-linecap="round"/>
    </g>""")

    elif condition == "storm":
        # Cloud + lightning bolt
        elements.append("""
    <!-- storm cloud -->
    <g>
      <circle cx="100" cy="36" r="10" fill="#A9A9A9" stroke="#000" stroke-width="2"/>
      <circle cx="114" cy="30" r="13" fill="#A9A9A9" stroke="#000" stroke-width="2"/>
      <circle cx="128" cy="36" r="10" fill="#A9A9A9" stroke="#000" stroke-width="2"/>
      <rect x="93" y="36" width="42" height="9" rx="3" fill="#A9A9A9" stroke="none"/>
      <line x1="93" y1="40" x2="135" y2="40" stroke="#000" stroke-width="2" stroke-linecap="round"/>
    </g>
    <!-- lightning -->
    <polygon points="114,44 108,54 113,54 107,66 118,52 113,52 118,44" fill="#FFD700" stroke="#000" stroke-width="1.5" stroke-linejoin="round"/>
    <!-- rain -->
    <g class="rain-fall">
      <line x1="100" y1="48" x2="98" y2="55" stroke="#87CEEB" stroke-width="2" stroke-linecap="round"/>
      <line x1="126" y1="48" x2="124" y2="55" stroke="#87CEEB" stroke-width="2" stroke-linecap="round"/>
    </g>""")

    return "\n".join(elements)


def generate_svg(weather):
    """Generate the complete cute hand-drawn weather globe SVG."""
    temp = weather["temp_f"]
    condition = weather["condition"]
    label = weather["label"]
    is_day = weather["is_day"]

    # Timestamp in PST
    pst = timezone(timedelta(hours=-8))
    now = datetime.now(pst)
    timestamp = now.strftime("Updated %b %d, %I:%M %p PST")

    overlay = weather_overlay(condition, is_day)

    # Night sky background color
    bg_color = "#F0F4FF" if is_day else "#1a1a2e"
    star_color = "#000" if is_day else "#FFD700"
    text_color = "#000" if is_day else "#E0E0E0"
    label_bg = "#fff" if is_day else "#2D2D3D"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 220" width="200" height="220">
  <style>
    @keyframes twinkle {{
      0%, 100% {{ opacity: 0.3; }}
      50% {{ opacity: 1; }}
    }}
    @keyframes gentle-spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    @keyframes cloud-float {{
      0%, 100% {{ transform: translateX(0); }}
      50% {{ transform: translateX(6px); }}
    }}
    @keyframes rain-fall {{
      0% {{ transform: translateY(0); opacity: 1; }}
      100% {{ transform: translateY(8px); opacity: 0; }}
    }}
    @keyframes snow-fall {{
      0% {{ transform: translateY(0) rotate(0deg); opacity: 1; }}
      100% {{ transform: translateY(10px) rotate(45deg); opacity: 0; }}
    }}
    @keyframes fog-drift {{
      0%, 100% {{ transform: translateX(0); opacity: 0.4; }}
      50% {{ transform: translateX(8px); opacity: 0.6; }}
    }}
    @keyframes bob {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-3px); }}
    }}
    .star {{ animation: twinkle 3s ease-in-out infinite; }}
    .star-d1 {{ animation-delay: 0s; }}
    .star-d2 {{ animation-delay: 0.8s; }}
    .star-d3 {{ animation-delay: 1.6s; }}
    .star-d4 {{ animation-delay: 2.2s; }}
    .star-d5 {{ animation-delay: 0.4s; }}
    .cloud-float {{ animation: cloud-float 4s ease-in-out infinite; }}
    .rain-fall {{ animation: rain-fall 1s ease-in infinite; }}
    .snow-fall {{ animation: snow-fall 2s ease-in infinite; }}
    .fog-drift {{ animation: fog-drift 5s ease-in-out infinite; }}
    .globe-bob {{ animation: bob 4s ease-in-out infinite; }}
    text {{ font-family: -apple-system, 'Segoe UI', sans-serif; }}
  </style>

  <!-- background -->
  <rect width="200" height="220" rx="16" fill="{bg_color}" stroke="#000" stroke-width="2.5"/>

  <!-- decorative stars/dots -->
  <circle cx="20" cy="20" r="2" fill="{star_color}" class="star star-d1"/>
  <circle cx="175" cy="18" r="1.5" fill="{star_color}" class="star star-d2"/>
  <circle cx="15" cy="85" r="1.5" fill="{star_color}" class="star star-d3"/>
  <circle cx="185" cy="90" r="2" fill="{star_color}" class="star star-d4"/>
  <circle cx="30" cy="50" r="1" fill="{star_color}" class="star star-d5"/>
  <circle cx="170" cy="130" r="1.5" fill="{star_color}" class="star star-d1"/>
  <circle cx="22" cy="140" r="1" fill="{star_color}" class="star star-d3"/>

  <!-- small doodle daisies -->
  <g transform="translate(172,70)" class="star star-d2">
    <circle cx="0" cy="0" r="2" fill="#FFD700"/>
    <circle cx="0" cy="-4" r="1.5" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="3.8" cy="-1.2" r="1.5" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="2.4" cy="3.2" r="1.5" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="-2.4" cy="3.2" r="1.5" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="-3.8" cy="-1.2" r="1.5" fill="#fff" stroke="#000" stroke-width="0.5"/>
  </g>
  <g transform="translate(28,110)" class="star star-d4">
    <circle cx="0" cy="0" r="1.5" fill="#FFD700"/>
    <circle cx="0" cy="-3" r="1" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="2.8" cy="-1" r="1" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="1.8" cy="2.4" r="1" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="-1.8" cy="2.4" r="1" fill="#fff" stroke="#000" stroke-width="0.5"/>
    <circle cx="-2.8" cy="-1" r="1" fill="#fff" stroke="#000" stroke-width="0.5"/>
  </g>

  <!-- globe group -->
  <g class="globe-bob">
    <!-- ocean circle -->
    <circle cx="100" cy="95" r="52" fill="#87CEEB" stroke="#000" stroke-width="3"/>

    <!-- simplified doodle continents (cute blobs, not accurate) -->
    <!-- North America blob -->
    <path d="M72,68 Q78,60 90,62 Q96,60 98,65 Q102,62 105,68 Q108,75 104,82
             Q100,88 95,86 Q88,90 82,86 Q76,82 72,75 Z"
          fill="#90EE90" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>

    <!-- South America blob -->
    <path d="M92,98 Q96,94 100,97 Q103,100 102,108 Q100,116 96,120
             Q92,118 90,112 Q88,106 90,102 Z"
          fill="#90EE90" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>

    <!-- Europe/Africa blob -->
    <path d="M112,72 Q116,68 120,72 Q122,78 120,85 Q118,92 116,98
             Q114,104 110,108 Q108,104 108,96 Q106,88 108,80 Q110,76 112,72 Z"
          fill="#90EE90" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>

    <!-- Asia blob -->
    <path d="M122,66 Q128,62 134,66 Q138,70 140,76 Q138,80 134,82
             Q130,84 126,80 Q122,76 120,72 Z"
          fill="#90EE90" stroke="#000" stroke-width="2.5" stroke-linejoin="round"/>

    <!-- Australia blob -->
    <path d="M130,100 Q136,97 140,100 Q142,104 138,108 Q134,110 130,106 Z"
          fill="#90EE90" stroke="#000" stroke-width="2" stroke-linejoin="round"/>

    <!-- globe shine (cute doodle highlight) -->
    <path d="M70,72 Q72,65 78,62" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" opacity="0.6"/>
  </g>

  <!-- weather overlay -->
  {overlay}

  <!-- temperature display -->
  <text x="100" y="168" text-anchor="middle" font-size="22" font-weight="bold" fill="{text_color}" stroke="{label_bg}" stroke-width="3" paint-order="stroke">{temp}°F</text>

  <!-- condition label -->
  <text x="100" y="184" text-anchor="middle" font-size="10" fill="{text_color}" opacity="0.8">{label}</text>

  <!-- location label -->
  <text x="100" y="200" text-anchor="middle" font-size="9" fill="{text_color}" opacity="0.6">📍 Menlo Park, CA</text>

  <!-- timestamp -->
  <text x="100" y="214" text-anchor="middle" font-size="7" fill="{text_color}" opacity="0.4">{timestamp}</text>
</svg>"""

    return svg


def main():
    weather = fetch_weather()
    print(f"🌍 Weather: {weather['label']} | {weather['temp_f']}°F | {'Day' if weather['is_day'] else 'Night'}")

    svg = generate_svg(weather)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(svg)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"✅ Saved to {OUTPUT_FILE} ({size_kb:.1f} KB)")

    if size_kb > 20:
        print(f"⚠ SVG is {size_kb:.1f} KB (target <20KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
