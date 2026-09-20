# MCP server exposing weather tools via Open-Meteo (no API key required)
from __future__ import annotations

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("singapore-weather")

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# https://open-meteo.com/en/docs -> WMO Weather interpretation codes
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def _geocode(location: str) -> tuple[float, float, str] | None:
    resp = requests.get(GEOCODE_URL, params={"name": location, "count": 1}, timeout=15)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        return None
    top = results[0]
    label = ", ".join(filter(None, [top.get("name"), top.get("country")]))
    return top["latitude"], top["longitude"], label


@mcp.tool()
def get_weather_forecast(location: str, days: int = 3) -> dict:
    """Get a daily weather forecast for a location for the next N days (1-7)."""
    days = max(1, min(days, 7))
    try:
        geo = _geocode(location)
        if geo is None:
            return {"error": f"Could not find coordinates for location '{location}'."}
        lat, lon, label = geo

        resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_sum,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": days,
            },
            timeout=15,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]

        forecast = []
        any_rain = False
        for i, day_str in enumerate(daily["time"]):
            code = daily["weather_code"][i]
            rain_prob = daily["precipitation_probability_max"][i]
            if rain_prob is not None and rain_prob >= 50:
                any_rain = True
            forecast.append(
                {
                    "date": day_str,
                    "condition": WEATHER_CODES.get(code, f"Code {code}"),
                    "temp_max_c": daily["temperature_2m_max"][i],
                    "temp_min_c": daily["temperature_2m_min"][i],
                    "precipitation_mm": daily["precipitation_sum"][i],
                    "rain_probability_pct": rain_prob,
                }
            )

        return {
            "location": label,
            "source": "Open-Meteo (open-meteo.com)",
            "forecast": forecast,
            "rain_likely_in_period": any_rain,
        }
    except requests.RequestException as exc:
        return {"error": f"Weather service unavailable: {exc}"}


@mcp.tool()
def get_current_weather(location: str) -> dict:
    """Get the current weather conditions right now for a location."""
    try:
        geo = _geocode(location)
        if geo is None:
            return {"error": f"Could not find coordinates for location '{location}'."}
        lat, lon, label = geo

        resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,precipitation,weather_code,wind_speed_10m",
                "timezone": "auto",
            },
            timeout=15,
        )
        resp.raise_for_status()
        current = resp.json()["current"]

        return {
            "location": label,
            "source": "Open-Meteo (open-meteo.com)",
            "as_of": current["time"],
            "temperature_c": current["temperature_2m"],
            "condition": WEATHER_CODES.get(current["weather_code"], f"Code {current['weather_code']}"),
            "precipitation_mm": current["precipitation"],
            "wind_speed_kmh": current["wind_speed_10m"],
        }
    except requests.RequestException as exc:
        return {"error": f"Weather service unavailable: {exc}"}


if __name__ == "__main__":
    mcp.run(transport="stdio")
