---
name: era5-download
description: "Use this skill whenever the user wants to download ERA5 reanalysis data from ECMWF's Climate Data Store (CDS). Triggers include: any mention of ERA5, ECMWF, CDS, reanalysis data, 재분석 자료, 기상 데이터 다운로드. Use when the user wants to retrieve atmospheric variables such as temperature, wind, precipitation, or geopotential for a specific time period or region. Do NOT use for other reanalysis datasets (MERRA-2, JRA-55) or real-time observation data."
---

# ERA5 데이터 다운로드

## 이 스킬이 무엇인가

ERA5는 ECMWF가 제공하는 전지구 대기 재분석 자료다. `cdsapi` Python 패키지를 통해 CDS API로 접근한다.

| 작업 | 방법 |
|---|---|
| **단일기압면 변수** (지표 기온, 강수 등) | `reanalysis-era5-single-levels` |
| **기압면 변수** (상층 바람, 온도 등) | `reanalysis-era5-pressure-levels` |
| **지면·토양 변수** | `reanalysis-era5-land` |
| **월 평균** | 데이터셋 이름에 `-monthly-means` 추가 |

> `cdsapi`는 별도 설치 필요 — `pip install cdsapi`

---

## 사전 설정 (최초 1회)

CDS 계정(https://cds.climate.copernicus.eu) 가입 후 API 키를 홈 디렉토리에 저장:

```bash
# ~/.cdsapirc
url: https://cds.climate.copernicus.eu/api/v2
key: {UID}:{API-KEY}
```

UID와 API-KEY는 CDS 프로필 페이지에서 확인한다.

---

## Quick Start

```python
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': '2m_temperature',
        'year': '2023',
        'month': '01',
        'day': [f'{d:02d}' for d in range(1, 32)],
        'time': ['00:00', '06:00', '12:00', '18:00'],
        'format': 'netcdf',
    },
    'era5_t2m.nc'
)
```

---

## 단일기압면 변수 — `reanalysis-era5-single-levels`

```python
import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-single-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            '2m_temperature',           # 2m 기온
            'total_precipitation',      # 총 강수량
            'mean_sea_level_pressure',  # 해면기압
            '10m_u_component_of_wind',  # 10m 동서바람
            '10m_v_component_of_wind',  # 10m 남북바람
        ],
        'year': '2023',
        'month': ['01', '02', '03'],
        'day': [f'{d:02d}' for d in range(1, 32)],
        'time': ['00:00', '06:00', '12:00', '18:00'],
        'area': [40, 120, 30, 135],     # [북, 서, 남, 동] 한반도
        'format': 'netcdf',
    },
    'era5_surface.nc'
)
```

---

## 기압면 변수 — `reanalysis-era5-pressure-levels`

```python
c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'variable': [
            'temperature',              # 온도
            'geopotential',             # 지위고도
            'relative_humidity',        # 상대습도
            'u_component_of_wind',      # 동서바람
            'v_component_of_wind',      # 남북바람
        ],
        'pressure_level': ['1000', '850', '700', '500', '300', '200'],
        'year': '2023',
        'month': ['06', '07', '08'],
        'day': [f'{d:02d}' for d in range(1, 32)],
        'time': ['00:00', '12:00'],
        'area': [60, 90, 10, 150],      # 동아시아
        'format': 'netcdf',
    },
    'era5_pressure.nc'
)
```

---

## 월 평균 — `reanalysis-era5-single-levels-monthly-means`

```python
c.retrieve(
    'reanalysis-era5-single-levels-monthly-means',
    {
        'product_type': 'monthly_averaged_reanalysis',
        'variable': '2m_temperature',
        'year': [str(y) for y in range(1991, 2021)],  # 30년 기후평균
        'month': [f'{m:02d}' for m in range(1, 13)],
        'time': '00:00',
        'format': 'netcdf',
    },
    'era5_monthly.nc'
)
```

---

## 영역(area) 설정

```python
# 전구
'area': [90, -180, -90, 180]

# 한반도
'area': [40, 120, 30, 135]

# 동아시아
'area': [60, 90, 10, 150]

# 동남아시아
'area': [30, 90, -10, 140]
```

---

## 다운로드 후 검증

다운로드가 끝나면 `scripts/check_result.py`를 반드시 실행해 변수·시간·영역·결측값을 자동 점검한다.

```bash
python scripts/check_result.py era5_surface.nc \
    --vars t2m tp \
    --time-start 2023-01-01 --time-end 2023-03-31 \
    --area 40 120 30 135
```

검증을 통과해야 다음 분석 단계로 넘어간다. 실패하면 원인을 확인하고 재요청한다.

---

## 워크플로

단계를 번호로 고정한다. 각 단계 완료 시 중간 결과를 출력하고 관문을 통과해야 다음 단계로 진행한다.

| 단계 | 작업 | 중간 결과 | 관문 |
|---|---|---|---|
| ① | 요청 파라미터 파악 (변수·기간·영역·형식) | 파라미터 목록 출력 | 사용자 확인 |
| ② | `cdsapi` 설치 및 `~/.cdsapirc` 확인 | "Client ready" 메시지 | 오류 없음 |
| ③ | API 요청 코드 생성 및 실행 | 큐 ID 및 진행 상황 출력 | 요청 수락됨 |
| ④ | 다운로드 완료 확인 | 파일 크기 및 경로 출력 | 파일 존재 확인 |
| ⑤ | `check_result.py` 실행 | 검증 보고서 출력 | 모든 항목 PASS |

---

## 계획

실행 전에 아래 형식으로 계획을 출력하고 사용자 확인을 받는다.

```
=== ERA5 다운로드 계획 ===
데이터셋  : reanalysis-era5-single-levels
변수      : 2m_temperature, total_precipitation
기간      : 2023-01-01 ~ 2023-03-31
영역      : 북40 서120 남30 동135 (한반도)
시간해상도: 6시간 간격
출력 형식 : NetCDF
저장 경로 : era5_surface.nc
예상 크기 : 약 50 MB

진행하시겠습니까? (y/n)
```

사용자가 확인한 뒤에만 API 요청을 실행한다.

---

## 검증

다운로드 완료 후 반드시 `scripts/check_result.py`를 실행한다.

- **실패 시:** 원인을 파악하고 파라미터를 수정해 재요청한다.
- **2회 연속 실패 시:** 자동 재시도를 멈추고 사용자에게 상황을 보고한 뒤 지시를 기다린다.

```python
# 검증 실패 예시 출력
# [FAIL] NaN 비율: t2m 변수에 결측값 67.3% 초과 (허용: 5%)
# [FAIL] 시간 범위: 2020-01-01 ~ 2020-03-31 (요청: 2023)
# → 재요청 또는 사용자 확인 필요
```

---

## 훅·관한

**하지 말 것:**

- 파일을 덮어쓰기 전에 기존 파일 존재 여부를 확인하지 않고 원자적으로 쓰기 금지
- 하드코딩된 경로(`/home/user/data/`) 사용 금지 — 항상 인자로 받을 것
- 검증 실패 상태에서 다음 분석 단계로 넘어가는 것 금지
- 동시 요청 2개 초과 금지 (CDS 정책)

**settings.json 훅 예시:**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -q 'era5.*\\.nc'; then echo '[hook] NetCDF 덮어쓰기 감지 — 기존 파일 백업 필요'; fi"
          }
        ]
      }
    ]
  }
}
```

---

## 서브에이전트

ERA5 다운로드는 단일 순차 작업이 기본이나, **여러 기간 또는 변수군을 병렬 요청**할 때 서브에이전트로 분할한다.

| 조각 | 목표 | 출력 형태 | 도구 | 경계 |
|---|---|---|---|---|
| 에이전트 A | 단일기압면 변수 다운로드 | `era5_surface.nc` | cdsapi, check_result.py | 지표 변수만 |
| 에이전트 B | 기압면 변수 다운로드 | `era5_pressure.nc` | cdsapi, check_result.py | 상층 변수만 |
| 취합 에이전트 | 두 파일 병합 및 최종 검증 | `era5_merged.nc` | xarray, check_result.py | A·B 완료 후 실행 |

**주의:** CDS 동시 요청 한도(2개)를 초과하지 않도록 에이전트 수를 제한한다.

---

## 주의사항

- **날짜 형식:** 반드시 두 자리 문자열 — `'01'`, `'12'` (정수 입력 시 오류)
- **대기 시간:** 요청량에 따라 수 분 ~ 수 시간 소요; 큐 상태는 CDS 웹에서 확인
- **파일 크기:** 전구·장기간·고해상도 요청은 수십 GB 이상 가능; 영역을 먼저 제한할 것
- **변수명:** CDS 웹(https://cds.climate.copernicus.eu)에서 정확한 변수명 복사 권장
- **요청 한도:** 동시 요청은 2개까지; 초과 시 큐에서 대기

---

## Dependencies

`cdsapi` · `xarray` · `netCDF4` (xarray 백엔드)

```bash
pip install cdsapi xarray netCDF4
```
