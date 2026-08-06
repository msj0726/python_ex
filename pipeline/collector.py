"""서로 독립적인 API 세 개를 동시에 호출하고 JSON 응답을 검증한다."""

import asyncio
from typing import Any

import httpx
from pydantic import ValidationError

from pipeline.models import Country, IpLocation, WeatherResponse

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"


async def fetch_json(client: httpx.AsyncClient, url: str, **params: Any) -> Any:
    """한 API를 GET 방식으로 호출하고 HTTP 또는 JSON 오류를 예외로 처리한다."""
    response = await client.get(url, params=params or None)
    response.raise_for_status()
    return response.json()


async def collect_all() -> tuple[WeatherResponse, Country, IpLocation]:
    """asyncio.gather를 사용하여 모든 API의 데이터를 동시에 수집한다."""
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

    # model_validate는 Pydantic v2에서 데이터 검증을 시작하는 메서드이다.
    try:
        return (
            WeatherResponse.model_validate(weather_json),
            Country.model_validate(country_json),
            IpLocation.model_validate(ip_json),
        )
    except ValidationError as exc:
        raise ValueError(f"API schema validation failed:\n{exc}") from exc
