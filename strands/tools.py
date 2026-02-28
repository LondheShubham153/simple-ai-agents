"""Tools for the Strands agent — get IP, location, and weather (works worldwide)."""

import httpx
from strands import tool


@tool
def get_ip_address() -> str:
    """Get the public IP address of the current machine."""
    resp = httpx.get("https://icanhazip.com")
    return resp.text.strip()


@tool
def get_location(ip_address: str) -> str:
    """Get the location (city, region, country, lat, lon) for an IP address.

    Args:
        ip_address: The IP address to look up.
    """
    resp = httpx.get(f"http://ip-api.com/json/{ip_address}")
    data = resp.json()
    return f"{data['city']}, {data['regionName']}, {data['country']} (lat={data['lat']}, lon={data['lon']})"


@tool
def get_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a latitude/longitude. Works worldwide, no API key needed.

    Args:
        latitude: Latitude of the location.
        longitude: Longitude of the location.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
    }
    resp = httpx.get(url, params=params)
    data = resp.json()["current"]
    return (
        f"Temperature: {data['temperature_2m']}°C, "
        f"Humidity: {data['relative_humidity_2m']}%, "
        f"Wind: {data['wind_speed_10m']} km/h, "
        f"Weather code: {data['weather_code']}"
    )
