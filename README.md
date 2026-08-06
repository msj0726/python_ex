# 데이터 수집 미니 파이프라인 — Day 1

Open-Meteo, Countries.dev, ip-api를 `asyncio.gather()`로 동시에 호출하고,
Pydantic v2로 검증한 뒤 CSV와 Parquet으로 저장해 I/O 시간을 비교합니다.

## 1. 환경 구성

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

활성화 확인:

```bash
which python                       # 경로에 .venv가 보여야 함
python -c "import pydantic; print(pydantic.VERSION)"  # 2.x
```

## 2. 실행

```bash
python main.py
```

`output/`에 `weather`, `country`, `ip_location` 각각의 CSV와 Parquet가 생기며,
터미널에 두 형식의 쓰기 시간, 읽기 시간, 총 파일 크기가 출력됩니다. 성능 수치는
컴퓨터와 실행 시점마다 달라집니다.

> ip-api 무료 엔드포인트는 HTTP를 사용합니다. HTTPS-only 네트워크에서는 요청이
> 차단될 수 있으므로 과제에서 지정한 네트워크 환경에서 실행하세요.

## 3. 품질 검사

```bash
pytest -v
ruff check .
```

테스트는 외부 API를 호출하지 않으므로 안정적으로 스키마의 정상/예외 동작을 검사합니다.


## 구현 흐름

1. `collector.py`: 세 API 요청 코루틴을 `asyncio.gather()`로 동시 실행
2. `models.py`: 필요한 필드의 타입·범위·배열 길이를 Pydantic v2로 검증
3. `storage.py`: 검증 객체를 표로 정규화하고 CSV/Parquet 읽기·쓰기 측정
4. `main.py`: 네트워크/검증 오류를 처리하고 결과 요약 출력
5. `tests/test_models.py`: 정상 데이터와 타입·범위 오류를 `pytest`로 검증


## 실행 결과

```text
수집/검증 완료: 날씨 72건, 국가 1건, IP 위치 1건
형식       쓰기(초)     읽기(초)     전체 크기(bytes)
csv        0.005227   0.002105   2,253
parquet    0.896729   1.290719   12,435
```

```text
4 passed in 0.04s
All checks passed!
```

세 API에서 필요한 데이터가 모두 수집되어 Pydantic 검증을 통과했다. 날씨 72건은
3일 × 24시간의 결과이며, 국가와 IP 위치 데이터는 각각 1건이다. 스키마의 정상 값과
오류 조건을 검사하는 테스트 4건이 통과했고 Ruff에서도 코드 품질 오류가 발견되지 않았다.

