"""
check_result.py — ERA5 NetCDF 파일 자동 검증 스크립트

사용법:
    python scripts/check_result.py <파일경로> [옵션]

옵션:
    --vars VAR1 VAR2 ...         필수 변수 이름 목록
    --time-start YYYY-MM-DD      시작 날짜 (예: 2023-01-01)
    --time-end   YYYY-MM-DD      종료 날짜 (예: 2023-03-31)
    --area N W S E               예상 영역 [북 서 남 동] (예: 40 120 30 135)
    --nan-threshold 0.05         NaN 허용 비율 (기본 5%)

예시:
    python scripts/check_result.py era5_surface.nc \\
        --vars t2m tp \\
        --time-start 2023-01-01 --time-end 2023-03-31 \\
        --area 40 120 30 135
"""

import sys
import argparse
from pathlib import Path
import numpy as np

# ── 물리적 합리성 기준 ──────────────────────────────────────────────────────
PHYSICAL_BOUNDS = {
    't2m':  (183.0, 333.0),   # 2m 기온 (K)
    'tp':   (0.0,   0.5),     # 강수량 (m/hr)
    'msl':  (85000, 108000),  # 해면기압 (Pa)
    'u10':  (-100,  100),     # 10m 동서바람 (m/s)
    'v10':  (-100,  100),     # 10m 남북바람 (m/s)
    'r':    (0.0,   100.0),   # 상대습도 (%)
    'u':    (-200,  200),     # 상층 동서바람 (m/s)
    'v':    (-200,  200),     # 상층 남북바람 (m/s)
    'z':    (-1000, 600000),  # 지위고도 (m²/s²)
}

PASS = '\033[92m[PASS]\033[0m'
FAIL = '\033[91m[FAIL]\033[0m'
WARN = '\033[93m[WARN]\033[0m'
INFO = '\033[94m[INFO]\033[0m'


def parse_args():
    p = argparse.ArgumentParser(description='ERA5 NetCDF 검증 스크립트')
    p.add_argument('filepath', help='검증할 .nc 파일 경로')
    p.add_argument('--vars', nargs='+', default=[], help='필수 변수 이름 목록')
    p.add_argument('--time-start', default=None, help='예상 시작 날짜 (YYYY-MM-DD)')
    p.add_argument('--time-end',   default=None, help='예상 종료 날짜 (YYYY-MM-DD)')
    p.add_argument('--area', nargs=4, type=float, default=None,
                   metavar=('N', 'W', 'S', 'E'), help='예상 영역 [북 서 남 동]')
    p.add_argument('--nan-threshold', type=float, default=0.05,
                   help='NaN 허용 비율 (기본: 0.05 = 5%%)')
    return p.parse_args()


def check_file_exists(path: Path):
    print(f"\n{'='*55}")
    print(f"  ERA5 파일 검증 — {path.name}")
    print(f"{'='*55}")
    if not path.exists():
        print(f"{FAIL} 파일을 찾을 수 없음: {path}")
        sys.exit(1)
    size_mb = path.stat().st_size / 1024 / 1024
    if size_mb < 0.001:
        print(f"{FAIL} 파일 크기 0 — 다운로드 실패 가능성")
        sys.exit(1)
    print(f"{PASS} 파일 존재 확인 ({size_mb:.2f} MB)")


def load_dataset(path: Path):
    try:
        import xarray as xr
        ds = xr.open_dataset(path)
        print(f"{PASS} 파일 열기 성공")
        return ds
    except Exception as e:
        print(f"{FAIL} 파일 열기 실패 — {e}")
        sys.exit(1)


def check_variables(ds, required_vars):
    print(f"\n{INFO} 변수 확인")
    existing = list(ds.data_vars)
    print(f"  파일 내 변수: {existing}")
    failed = False
    for var in required_vars:
        if var in existing:
            print(f"  {PASS} '{var}' 존재")
        else:
            print(f"  {FAIL} '{var}' 없음")
            failed = True
    return not failed


def check_time_range(ds, time_start, time_end):
    if 'time' not in ds.coords:
        print(f"\n{WARN} 시간 좌표 없음 — 건너뜀")
        return True
    import pandas as pd
    times = pd.to_datetime(ds.time.values)
    actual_start = times.min()
    actual_end   = times.max()
    print(f"\n{INFO} 시간 범위 확인")
    print(f"  실제 범위: {actual_start.date()} ~ {actual_end.date()} ({len(times)}개 시각)")
    ok = True
    if time_start:
        exp = pd.Timestamp(time_start)
        if actual_start > exp + pd.Timedelta(days=1):
            print(f"  {FAIL} 시작일 불일치 — 예상 {time_start}, 실제 {actual_start.date()}")
            ok = False
        else:
            print(f"  {PASS} 시작일 일치 ({actual_start.date()})")
    if time_end:
        exp = pd.Timestamp(time_end)
        if actual_end < exp - pd.Timedelta(days=1):
            print(f"  {FAIL} 종료일 불일치 — 예상 {time_end}, 실제 {actual_end.date()}")
            ok = False
        else:
            print(f"  {PASS} 종료일 일치 ({actual_end.date()})")
    return ok


def check_area(ds, area):
    if area is None:
        return True
    n, w, s, e = area
    ok = True
    print(f"\n{INFO} 영역 확인 (예상: 북{n} 서{w} 남{s} 동{e})")
    for dim, lo, hi, label in [
        ('latitude',  s, n, '위도'),
        ('longitude', w, e, '경도'),
    ]:
        if dim not in ds.coords:
            print(f"  {WARN} '{dim}' 좌표 없음 — 건너뜀")
            continue
        vals = ds[dim].values
        vmin, vmax = float(vals.min()), float(vals.max())
        tol = 1.0  # 1도 허용 오차
        if vmin > lo + tol or vmax < hi - tol:
            print(f"  {FAIL} {label} 범위 불일치 — 예상 {lo}~{hi}, 실제 {vmin:.2f}~{vmax:.2f}")
            ok = False
        else:
            print(f"  {PASS} {label} 범위 정상 ({vmin:.2f} ~ {vmax:.2f})")
    return ok


def check_nan(ds, threshold):
    print(f"\n{INFO} 결측값(NaN) 확인 (허용 비율: {threshold*100:.0f}%)")
    ok = True
    for var in ds.data_vars:
        arr = ds[var].values
        total = arr.size
        n_nan = int(np.isnan(arr).sum())
        ratio = n_nan / total
        if ratio > threshold:
            print(f"  {FAIL} '{var}': NaN {n_nan}/{total} ({ratio*100:.1f}%) — 허용 초과")
            ok = False
        else:
            print(f"  {PASS} '{var}': NaN {n_nan}/{total} ({ratio*100:.1f}%)")
    return ok


def check_physical_bounds(ds):
    print(f"\n{INFO} 물리적 범위 확인")
    ok = True
    for var in ds.data_vars:
        if var not in PHYSICAL_BOUNDS:
            continue
        lo, hi = PHYSICAL_BOUNDS[var]
        arr = ds[var].values
        vmin = float(np.nanmin(arr))
        vmax = float(np.nanmax(arr))
        if vmin < lo or vmax > hi:
            print(f"  {FAIL} '{var}': 값 범위 {vmin:.2f}~{vmax:.2f} — 기준 {lo}~{hi}")
            ok = False
        else:
            print(f"  {PASS} '{var}': {vmin:.2f} ~ {vmax:.2f} (정상)")
    return ok


def main():
    args = parse_args()
    path = Path(args.filepath)

    check_file_exists(path)
    ds = load_dataset(path)

    results = []
    results.append(check_variables(ds, args.vars))
    results.append(check_time_range(ds, args.time_start, args.time_end))
    results.append(check_area(ds, args.area))
    results.append(check_nan(ds, args.nan_threshold))
    results.append(check_physical_bounds(ds))

    ds.close()

    print(f"\n{'='*55}")
    if all(results):
        print(f"  최종 결과: {PASS} 모든 항목 통과 — 다음 단계 진행 가능")
        sys.exit(0)
    else:
        n_fail = results.count(False)
        print(f"  최종 결과: {FAIL} {n_fail}개 항목 실패 — 원인 확인 후 재요청 필요")
        sys.exit(1)
    print(f"{'='*55}\n")


if __name__ == '__main__':
    main()
