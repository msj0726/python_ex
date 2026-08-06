"""Day 1 데이터 수집 파이프라인의 명령줄 실행 진입점."""

import asyncio
from pathlib import Path

import httpx

from pipeline.collector import collect_all
from pipeline.storage import build_frames, save_and_benchmark


async def main() -> None:
    try:
        weather, country, ip_location = await collect_all()
    except (httpx.HTTPError, ValueError) as exc:
        raise SystemExit(f"Collection failed: {exc}") from exc

    frames = build_frames(weather, country, ip_location)
    benchmark = save_and_benchmark(frames, Path("output"))

    print(f"수집/검증 완료: 날씨 {len(frames['weather'])}건, 국가 1건, IP 위치 1건")
    print("형식       쓰기(초)     읽기(초)     전체 크기(bytes)")
    for file_format, values in benchmark.items():
        print(
            f"{file_format:<10} "
            f"{values['write_seconds']:.6f}   "
            f"{values['read_seconds']:.6f}   "
            f"{int(values['total_bytes']):,}"
        )


if __name__ == "__main__":
    asyncio.run(main())
