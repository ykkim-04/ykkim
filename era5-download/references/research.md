# ERA5 다운로드 스킬 — 참고 자료

## CDS API 공식 문서

| 자료 | URL |
|---|---|
| CDS API 시작 가이드 | https://cds.climate.copernicus.eu/api-how-to |
| ERA5 단일기압면 변수 목록 | https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels |
| ERA5 기압면 변수 목록 | https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels |
| ERA5 Land | https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land |
| cdsapi Python 패키지 | https://github.com/ecmwf/cdsapi |

---

## ERA5 주요 변수 정리

### 단일기압면 (Single Levels)

| 변수명 (API) | 설명 | 단위 |
|---|---|---|
| `2m_temperature` | 지상 2m 기온 | K |
| `total_precipitation` | 총 강수량 | m/hr |
| `mean_sea_level_pressure` | 해면기압 | Pa |
| `10m_u_component_of_wind` | 10m 동서바람 | m/s |
| `10m_v_component_of_wind` | 10m 남북바람 | m/s |
| `surface_pressure` | 지면기압 | Pa |
| `2m_dewpoint_temperature` | 2m 이슬점온도 | K |
| `total_cloud_cover` | 전운량 | 0–1 |
| `snowfall` | 강설량 | m of water equiv. |

### 기압면 (Pressure Levels)

| 변수명 (API) | 설명 | 단위 |
|---|---|---|
| `temperature` | 기온 | K |
| `geopotential` | 지위고도 | m²/s² |
| `relative_humidity` | 상대습도 | % |
| `u_component_of_wind` | 동서바람 | m/s |
| `v_component_of_wind` | 남북바람 | m/s |
| `specific_humidity` | 비습 | kg/kg |
| `vertical_velocity` | 연직속도 | Pa/s |

### 표준 기압면

```
1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50, 10 hPa
```

---

## 영역(area) 파라미터 기준

`area`는 `[북, 서, 남, 동]` 순서 (위도·경도 십진수).

| 지역 | area 값 |
|---|---|
| 전구 | `[90, -180, -90, 180]` |
| 한반도 | `[40, 120, 30, 135]` |
| 동아시아 | `[60, 90, 10, 150]` |
| 동남아시아 | `[30, 90, -10, 140]` |
| 유럽 | `[75, -25, 35, 45]` |

---

## 시간 해상도

| 종류 | 사용 가능 시간 |
|---|---|
| 시간 자료 (hourly) | 00:00 ~ 23:00 (매 시간) |
| 6시간 자료 | 00:00, 06:00, 12:00, 18:00 |
| 월 평균 | product_type: `monthly_averaged_reanalysis` |

---

## 파일 형식

| 형식 | format 값 | 비고 |
|---|---|---|
| NetCDF | `'netcdf'` | xarray로 바로 읽기 가능, 권장 |
| GRIB | `'grib'` | cfgrib 필요 |

---

## 물리적 값 범위 (검증 기준)

`check_result.py`에서 사용하는 물리적 합리성 기준:

| 변수 | 최솟값 | 최댓값 | 단위 |
|---|---|---|---|
| 2m 기온 (`t2m`) | 183 K | 333 K | K |
| 강수량 (`tp`) | 0 | 0.5 | m/hr |
| 해면기압 (`msl`) | 85000 Pa | 108000 Pa | Pa |
| 상대습도 (`r`) | 0 % | 100 % | % |
| 동서바람 (`u`) | −100 m/s | 100 m/s | m/s |

---

## API 요청 한도 및 대기 시간

- 동시 활성 요청: **최대 2개**
- 요청 초과 시 자동으로 큐 대기 (수동 개입 불필요)
- 큐 상태 확인: https://cds.climate.copernicus.eu/live/queue
- 소규모 요청(좁은 영역, 단기간): 수 분 이내
- 대규모 요청(전구, 수십 년): 수 시간 이상 가능

---

## xarray로 NetCDF 읽기 예시

```python
import xarray as xr

ds = xr.open_dataset('era5_surface.nc')

# 기본 구조 확인
print(ds)

# 변수 목록
print(list(ds.data_vars))

# 시간 범위
print(ds.time.values[[0, -1]])

# 특정 변수 통계
print(ds['t2m'].mean().item(), 'K')
```

---

## 참고 논문 및 문서

- Hersbach et al. (2020). "The ERA5 global reanalysis." *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049. https://doi.org/10.1002/qj.3803
- ECMWF (2023). *ERA5 data documentation*. https://confluence.ecmwf.int/display/CKB/ERA5
