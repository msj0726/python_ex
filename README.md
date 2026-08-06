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

## 4. Git 제출 이력 만들기

```bash
git init
git add .
git commit -m "feat: implement async data collection pipeline"
git log --oneline
```

제출 전 `git status`, `pytest -v`, `ruff check .`, `python main.py` 결과를 캡처하면
채점 항목을 증빙하기 쉽습니다. `.venv/`와 생성 데이터 `output/`은 Git에서 제외됩니다.

## 구현 흐름

1. `collector.py`: 세 API 요청 코루틴을 `asyncio.gather()`로 동시 실행
2. `models.py`: 필요한 필드의 타입·범위·배열 길이를 Pydantic v2로 검증
3. `storage.py`: 검증 객체를 표로 정규화하고 CSV/Parquet 읽기·쓰기 측정
4. `main.py`: 네트워크/검증 오류를 처리하고 결과 요약 출력
5. `tests/test_models.py`: 정상 데이터와 타입·범위 오류를 `pytest`로 검증

## 제출 체크리스트 (100점 대응)

- [ ] `.venv` 활성화 후 `requirements.txt` 설치
- [ ] 세 API가 정상 응답하고 `asyncio.gather()` 동시 수집 확인
- [ ] Pydantic v2 모델과 검증 실패 예외 처리 확인
- [ ] CSV 3개, Parquet 3개 생성 및 성능 결과 출력 확인
- [ ] `pytest` 1건 이상 통과 및 `ruff check .` 오류 없음
- [ ] 코드 설명 주석 포함
- [ ] Git 커밋 이력 존재

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

## Code 분석 결과에 대한 본인 의견

`asyncio.gather()`를 이용하면 서로 독립적인 API 요청을 동시에 처리할 수 있으므로
순차 호출보다 전체 대기 시간을 줄일 수 있다. 또한 수집한 JSON을 바로 저장하지 않고
Pydantic v2 모델로 검증하여 잘못된 타입, 허용 범위를 벗어난 값, 실패 상태 응답이
저장되는 것을 방지하였다.

이번 측정에서는 CSV가 Parquet보다 빠르고 파일 크기도 작았다. 그러나 전체 데이터가
74행으로 매우 작기 때문에 Parquet의 라이브러리 초기화, 스키마 작성, 압축 및 메타데이터
처리 비용이 상대적으로 크게 반영된 결과이다. 따라서 CSV가 항상 우수하다고 결론 내릴
수는 없으며, 대용량 데이터와 일부 열만 조회하는 분석 환경에서는 열 기반 형식인
Parquet이 더 유리할 수 있다.

수집, 검증, 저장 기능을 모듈별로 분리하여 각 코드의 책임을 명확하게 구성하였다.
이 구조는 API나 저장 형식이 변경되더라도 관련 모듈만 수정할 수 있어 유지보수와 테스트에
유리하다고 판단하였다.
