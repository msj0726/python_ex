"""Normalize validated models and compare CSV/Parquet I/O time."""

from pathlib import Path
from time import perf_counter

import pandas as pd

from pipeline.models import Country, IpLocation, WeatherResponse


def build_frames(
    weather: WeatherResponse, country: Country, ip_location: IpLocation
) -> dict[str, pd.DataFrame]:
    """Convert models to three rectangular tables suitable for both formats."""
    return {
        "weather": pd.DataFrame([row.model_dump(mode="json") for row in weather.rows()]),
        "country": pd.DataFrame([country.model_dump()]),
        "ip_location": pd.DataFrame([ip_location.model_dump()]),
    }


def save_and_benchmark(
    frames: dict[str, pd.DataFrame], output_dir: Path
) -> dict[str, dict[str, float]]:
    """Write/read all tables, returning elapsed seconds and total byte size."""
    output_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, dict[str, float]] = {}

    for file_format in ("csv", "parquet"):
        paths = [output_dir / f"{name}.{file_format}" for name in frames]

        started = perf_counter()
        for path, frame in zip(paths, frames.values(), strict=True):
            if file_format == "csv":
                frame.to_csv(path, index=False)
            else:
                frame.to_parquet(path, index=False)
        write_seconds = perf_counter() - started

        started = perf_counter()
        for path in paths:
            if file_format == "csv":
                pd.read_csv(path)
            else:
                pd.read_parquet(path)
        read_seconds = perf_counter() - started

        result[file_format] = {
            "write_seconds": write_seconds,
            "read_seconds": read_seconds,
            "total_bytes": float(sum(path.stat().st_size for path in paths)),
        }

    return result
