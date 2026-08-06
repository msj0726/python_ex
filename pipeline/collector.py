"""Fetch three independent APIs concurrently and validate their JSON."""

import asyncio
from typing import Any

import httpx
from pydantic import ValidationError

from pipeline.models import Country, IpLocation, WeatherResponse

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"


async def fetch_json(client: httpx.AsyncClient, url: str, **params: Any) -> Any:
    """GET one endpoint and raise on HTTP or malformed JSON errors."""
    response = await client.get(url, params=params or None)
    response.raise_for_status()
    return response.json()


async def collect_all() -> tuple[WeatherResponse, Country, IpLocation]:
    """Collect all endpoints at the same time using asyncio.gather."""
    timeout = httpx.Timeout(20.0)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        weather_json, country_json, ip_json = await asyncio.gather(
            fetch_json(
                client,
                WEATHER_URL,
                latitude=37.5665,
                longitude=126.9780,
                hourly="temperature_2m,precipitation_probability",
                forecast_days=3,
                timezone="Asia/Seoul",
            ),
            fetch_json(client, COUNTRY_URL),
            fetch_json(client, IP_URL),
        )

    # model_validate is the Pydantic v2 validation entry point.
    try:
        return (
            WeatherResponse.model_validate(weather_json),
            Country.model_validate(country_json),
            IpLocation.model_validate(ip_json),
        )
    except ValidationError as exc:
        raise ValueError(f"API schema validation failed:\n{exc}") from exc
