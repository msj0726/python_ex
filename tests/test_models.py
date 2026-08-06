"""Schema validation tests without depending on external APIs."""

import pytest
from pydantic import ValidationError

from pipeline.models import Country, IpLocation, WeatherHourly, WeatherResponse


def test_weather_valid_data() -> None:
    response = WeatherResponse.model_validate(
        {
            "timezone": "Asia/Seoul",
            "hourly": {
                "time": ["2026-08-06T00:00", "2026-08-06T01:00"],
                "temperature_2m": [25.1, 24.8],
                "precipitation_probability": [10, 20],
            },
        }
    )
    assert len(response.rows()) == 2


def test_precipitation_probability_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        WeatherHourly(
            time="2026-08-06T00:00",
            temperature_2m=25.0,
            precipitation_probability=101,
        )


def test_country_rejects_invalid_code() -> None:
    with pytest.raises(ValidationError):
        Country(
            name="Korea",
            alpha2Code="KOR",
            alpha3Code="KOR",
            capital="Seoul",
            region="Asia",
            population=51_000_000,
        )


def test_ip_rejects_failed_status() -> None:
    with pytest.raises(ValidationError):
        IpLocation(
            status="fail",
            query="8.8.8.8",
            country="United States",
            countryCode="US",
            regionName="Virginia",
            city="Ashburn",
            lat=39.03,
            lon=-77.5,
            timezone="America/New_York",
        )
