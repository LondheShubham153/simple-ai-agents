"""Tools for the Gemini agent — get IP, location, and weather (works worldwide)."""

import httpx
from google import genai
from google.genai import types


# --- Tool handlers (simple async functions) ---


async def get_ip_address() -> str:
    """Get the public IP address of the current machine."""
    async with httpx.AsyncClient() as client:
        resp = await client.get("https://icanhazip.com")
        return resp.text.strip()


async def get_location(ip_address: str) -> str:
    """Get the location (city, region, country, lat, lon) for an IP address.

    Args:
        ip_address: The IP address to look up.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"http://ip-api.com/json/{ip_address}")
        data = resp.json()
        return f"{data['city']}, {data['regionName']}, {data['country']} (lat={data['lat']}, lon={data['lon']})"


async def get_weather(latitude: float, longitude: float) -> str:
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
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()["current"]
        return (
            f"Temperature: {data['temperature_2m']}°C, "
            f"Humidity: {data['relative_humidity_2m']}%, "
            f"Wind: {data['wind_speed_10m']} km/h, "
            f"Weather code: {data['weather_code']}"
        )


# --- Registry ---

TOOL_HANDLERS = {
    "get_ip_address": get_ip_address,
    "get_location": get_location,
    "get_weather": get_weather,
}


def get_tools(client: genai.Client) -> types.Tool:
    """Build Gemini tool declarations from our handler functions."""
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration.from_callable(client=client, callable=fn)
            for fn in TOOL_HANDLERS.values()
        ]
    )


async def execute_tool(fc: types.FunctionCall) -> str:
    """Look up and run a tool by its FunctionCall."""
    handler = TOOL_HANDLERS[fc.name]
    args = dict(fc.args) if fc.args else {}
    return await handler(**args)
