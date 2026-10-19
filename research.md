# 연구 배경 및 용어 정리

## 연구 주제
전지구 토양수분(Soil Moisture, SM)과 잠열 플럭스(Latent Heat Flux, LH) 사이의 의존성 분석.
선형 및 비선형 관계 식별을 위한 Mutual Information(MI) 활용.

## 핵심 용어
- **SM (Soil Moisture)**: 토양수분
- **LH (Latent Heat Flux)**: 잠열 플럭스
- **MI (Mutual Information)**: 두 변수 사이의 통계적 의존성 측정 지표. 선형·비선형 관계 모두 포함. 독립일 때만 0.
- **MI_total**: SM과 LH 사이의 총 의존성
- **MI_linear**: 선형 성분 (MI_total - MI_nonlinear)
- **MI_nonlinear**: 회귀잔차 기반 비선형 성분

## 사용 데이터 및 모델
- ERA5, GLDAS, GLEAM, JRA-3Q, MERRA2, Noah, Noah-MP, VIC, Catchment
- 분석 기간: 1979–2025년 (일별 자료)

## 전처리 기준
- 365일 high-pass filter 적용
- 필터링된 SM 및 LH 자료 정규화

## MI 계산 방법
- 히스토그램 기반 MI 추정
- 연도별 독립적 MI 계산 후 평균
- MI_mean = (1/N) × Σ MI_y(SM, LH)

## 연구 목표
- 전지구 SM–LH 총 의존성의 공간 분포 제시
- 선형 및 비선형 의존성 성분 분리
- 자료 및 모델별 공간 패턴 비교
- 모델 간 차이가 큰 지역 식별

## 논문 방법론 비교 시 주목할 항목
새 논문을 읽을 때 아래 항목이 이 연구와 어떻게 다른지 확인한다.
- 의존성 측정 방법 (MI vs 상관계수 vs 기타)
- 선형/비선형 분리 방식
- 사용 데이터 및 모델 종류
- 전처리 방법 (필터링 방식, 정규화 여부)
- 분석 공간 범위 (전지구 vs 지역)
