"""Tools for the Bedrock agent — get IP, location, and weather (works worldwide)."""

import httpx


# --- Tool handlers (simple functions) ---


def get_ip_address() -> str:
    """Get the public IP address of the current machine."""
    resp = httpx.get("https://icanhazip.com")
    return resp.text.strip()


def get_location(ip_address: str) -> str:
    """Get the location (city, region, country, lat, lon) for an IP address."""
    resp = httpx.get(f"http://ip-api.com/json/{ip_address}")
    data = resp.json()
    return f"{data['city']}, {data['regionName']}, {data['country']} (lat={data['lat']}, lon={data['lon']})"


def get_weather(latitude: float, longitude: float) -> str:
    """Get current weather for a latitude/longitude. Works worldwide, no API key needed."""
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


# --- Registry ---

TOOL_HANDLERS = {
    "get_ip_address": get_ip_address,
    "get_location": get_location,
    "get_weather": get_weather,
}

TOOL_CONFIG = {
    "tools": [
        {
            "toolSpec": {
                "name": "get_ip_address",
                "description": "Get the public IP address of the current machine.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_location",
                "description": "Get the location (city, region, country, lat, lon) for an IP address.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "ip_address": {
                                "type": "string",
                                "description": "The IP address to look up.",
                            }
                        },
                        "required": ["ip_address"],
                    }
                },
            }
        },
        {
            "toolSpec": {
                "name": "get_weather",
                "description": "Get current weather for a latitude/longitude. Works worldwide, no API key needed.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "latitude": {
                                "type": "number",
                                "description": "Latitude of the location.",
                            },
                            "longitude": {
                                "type": "number",
                                "description": "Longitude of the location.",
                            },
                        },
                        "required": ["latitude", "longitude"],
                    }
                },
            }
        },
    ]
}


def execute_tool(name: str, tool_input: dict) -> str:
    """Look up and run a tool by name."""
    handler = TOOL_HANDLERS[name]
    return handler(**tool_input)
