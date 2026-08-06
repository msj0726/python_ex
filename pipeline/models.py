"""과제에서 사용하는 필드를 검증하기 위한 Pydantic v2 스키마."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class WeatherHourly(BaseModel):
    """서울의 한 시간 단위 날씨 관측값 또는 예보값."""

    time: datetime
    temperature_2m: float = Field(ge=-90, le=60)
    precipitation_probability: int = Field(ge=0, le=100)


class WeatherResponse(BaseModel):
    """Open-Meteo가 반환하는 병렬 배열의 구조와 값을 검증한다."""

    model_config = ConfigDict(extra="ignore")

    timezone: str
    hourly: dict[str, list]

    @field_validator("timezone")
    @classmethod
    def timezone_must_be_seoul(cls, value: str) -> str:
        if value != "Asia/Seoul":
            raise ValueError("timezone must be Asia/Seoul")
        return value

    @model_validator(mode="after")
    def validate_hourly_arrays(self) -> "WeatherResponse":
        required = ("time", "temperature_2m", "precipitation_probability")
        if any(key not in self.hourly for key in required):
            raise ValueError(f"hourly must contain: {', '.join(required)}")
        lengths = {len(self.hourly[key]) for key in required}
        if len(lengths) != 1 or not lengths or next(iter(lengths)) == 0:
            raise ValueError("hourly arrays must be non-empty and have equal lengths")
        return self

    def rows(self) -> list[WeatherHourly]:
        return [
            WeatherHourly(
                time=time,
                temperature_2m=temperature,
                precipitation_probability=probability,
            )
            for time, temperature, probability in zip(
                self.hourly["time"],
                self.hourly["temperature_2m"],
                self.hourly["precipitation_probability"],
                strict=True,
            )
        ]


class Country(BaseModel):
    """Countries.dev 응답에서 선택한 대한민국 국가 정보."""

    model_config = ConfigDict(extra="ignore")

    name: str = Field(min_length=1)
    alpha2Code: str = Field(pattern=r"^[A-Z]{2}$")
    alpha3Code: str = Field(pattern=r"^[A-Z]{3}$")
    capital: str = Field(min_length=1)
    region: str = Field(min_length=1)
    population: int = Field(gt=0)


class IpLocation(BaseModel):
    """ip-api 응답에서 선택한 IP 기반 위치 정보."""

    model_config = ConfigDict(extra="ignore")

    status: str
    query: str = Field(min_length=7)
    country: str = Field(min_length=1)
    countryCode: str = Field(pattern=r"^[A-Z]{2}$")
    regionName: str = Field(min_length=1)
    city: str = Field(min_length=1)
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    timezone: str = Field(min_length=1)

    @field_validator("status")
    @classmethod
    def status_must_be_success(cls, value: str) -> str:
        if value != "success":
            raise ValueError("ip-api request was not successful")
        return value
