#!/usr/bin/env python3
"""
Update README.md with a live weather card using basmilius/weather-icons animated SVGs.
Data source: Open-Meteo API (no API key required).
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Installing requests...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests

# ─── Config ───────────────────────────────────────────────────────────────────

LOCATION = "Menlo Park, CA"
LATITUDE = 37.4529
LONGITUDE = -122.1817
TIMEZONE = "America/Los_Angeles"

API_URL = (
    f"https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    f"&current=temperature_2m,apparent_temperature,weather_code,"
    f"wind_speed_10m,relative_humidity_2m,is_day"
    f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
    f"&temperature_unit=fahrenheit&timezone={TIMEZONE}&forecast_days=3"
)

ICON_BASE = "https://raw.githubusercontent.com/basmilius/weather-icons/dev/production/fill/svg"

# Script directory → repo root
SCRIPT_DIR = Path(__file__).resolve().parent
README_PATH = SCRIPT_DIR.parent / "README.md"

START_MARKER = "<!-- WEATHER:START -->"
END_MARKER = "<!-- WEATHER:END -->"

# ─── Mappings ─────────────────────────────────────────────────────────────────

def get_icon_name(code: int, is_day: bool = True) -> str:
    """Map WMO weather code to basmilius icon name."""
    suffix = "-day" if is_day else "-night"
    mapping = {
        0: f"clear{suffix}",
        1: f"partly-cloudy{suffix}",
        2: f"partly-cloudy{suffix}",
        3: f"overcast{suffix}",
        45: f"fog{suffix}",
        48: f"fog{suffix}",
        51: "drizzle",
        53: "drizzle",
        55: "drizzle",
        56: "sleet",
        57: "sleet",
        61: "rain",
        63: "rain",
        65: "thunderstorms-rain",
        66: "sleet",
        67: "sleet",
        71: "snow",
        73: "snow",
        75: "snow",
        77: "hail",
        80: "rain",
        81: "rain",
        82: "rain",
        85: "snow",
        86: "snow",
        95: "thunderstorms",
        96: "thunderstorms-rain",
        99: "thunderstorms-rain",
    }
    return mapping.get(code, f"partly-cloudy{suffix}")


WEATHER_DESCRIPTIONS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    56: "Freezing drizzle",
    57: "Heavy freezing drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Light snow",
    73: "Snow",
    75: "Heavy snow",
    77: "Hail",
    80: "Light showers",
    81: "Showers",
    82: "Heavy showers",
    85: "Light snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


def get_forecast_emoji(code: int) -> str:
    """Map WMO weather code to a compact emoji for the forecast row."""
    if code == 0:
        return "☀️"
    elif code in (1,):
        return "🌤️"
    elif code in (2,):
        return "⛅"
    elif code in (3,):
        return "☁️"
    elif code in (45, 48):
        return "🌫️"
    elif code in (51, 53, 55, 56, 57, 61, 63, 80, 81, 82):
        return "🌧️"
    elif code in (65, 66, 67):
        return "🌧️"
    elif code in (71, 73, 75, 77, 85, 86):
        return "🌨️"
    elif code in (95, 96, 99):
        return "⛈️"
    return "🌤️"


# ─── Main ─────────────────────────────────────────────────────────────────────

def fetch_weather() -> dict:
    """Fetch weather data from Open-Meteo."""
    resp = requests.get(API_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def build_card(data: dict) -> str:
    """Build the HTML weather card from API data."""
    current = data["current"]
    daily = data["daily"]

    temp = round(current["temperature_2m"])
    feels = round(current["apparent_temperature"])
    code = current["weather_code"]
    wind = round(current["wind_speed_10m"])
    humidity = current["relative_humidity_2m"]
    is_day = bool(current["is_day"])

    icon_name = get_icon_name(code, is_day)
    icon_url = f"{ICON_BASE}/{icon_name}.svg"
    description = WEATHER_DESCRIPTIONS.get(code, "Unknown")

    # Today's high/low
    high = round(daily["temperature_2m_max"][0])
    low = round(daily["temperature_2m_min"][0])

    # 3-day forecast
    forecast_parts = []
    for i in range(3):
        date_str = daily["time"][i]
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = dt.strftime("%a")
        fc_code = daily["weather_code"][i]
        fc_emoji = get_forecast_emoji(fc_code)
        fc_high = round(daily["temperature_2m_max"][i])
        fc_low = round(daily["temperature_2m_min"][i])
        forecast_parts.append(f"{day_name}: {fc_emoji} {fc_high}°F / {fc_low}°F")

    forecast_line = " · \n".join(forecast_parts)

    # Timestamp — use the timezone from the API response
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo(TIMEZONE)
        now = datetime.now(tz)
        updated = now.strftime("%a %b %-d, %-I:%M %p %Z").strip()
    except Exception:
        now = datetime.now()
        updated = now.strftime("%a %b %-d, %-I:%M %p PST").strip()

    card = f"""{START_MARKER}
<div align="center">
<table>
<tr>
<td align="center" width="160">
<img src="{icon_url}" width="80" /><br/>
<strong>{temp}°F</strong><br/>
<sub>{description}</sub><br/>
<sub>Feels like {feels}°F</sub>
</td>
<td align="left">
<strong style="font-size:1.1em">📍 {LOCATION}</strong><br/>
<sub>💨 Wind: {wind} mph · 💧 Humidity: {humidity}%</sub><br/>
<sub>🌡️ High: {high}°F · Low: {low}°F</sub><br/><br/>
<strong>3-Day Forecast:</strong><br/>
<sub>
{forecast_line}
</sub><br/>
<sub><i>Updated: {updated}</i></sub>
</td>
</tr>
</table>
</div>
{END_MARKER}"""

    return card


def update_readme(card: str) -> None:
    """Replace the weather section in README.md."""
    readme = README_PATH.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    if pattern.search(readme):
        new_readme = pattern.sub(card, readme)
    else:
        # Markers not found — abort rather than corrupt the file
        print(f"⚠️  Markers not found in {README_PATH}. Skipping update.")
        sys.exit(1)

    README_PATH.write_text(new_readme, encoding="utf-8")
    print(f"✅ README updated: {README_PATH}")


def main():
    try:
        data = fetch_weather()
        card = build_card(data)
        update_readme(card)
    except requests.RequestException as e:
        print(f"⚠️  Weather API error: {e}")
        print("README left unchanged.")
        sys.exit(0)  # Don't fail the GH Action — just skip
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
