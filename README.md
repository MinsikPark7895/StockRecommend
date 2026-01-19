# StockRecommend

미국 주식 시장을 분석하여 향후 상승 가능성이 높은 주식을 추천하는 AI 기반 주식 추천 시스템입니다.

## 📋 프로젝트 개요

다양한 데이터 소스를 통합 분석하여 아직 상승하지 않았지만 향후 상승 가능성이 높은 미국 주식을 예측하고 추천합니다.

## 🎯 주요 기능

- **다각도 데이터 분석**
  - 주가 데이터 및 기술적 지표 분석
  - 뉴스 데이터 감정 분석 및 키워드 추출
  - 재무제표 기반 펀더멘털 분석
  - 경영진 발언 및 실적 전화회의 분석
  - 계약 전망 및 파트너십 정보 분석
  - 환율, 금리 등 거시경제 지표 반영

- **머신러닝 기반 예측**
  - 시계열 예측 모델 (LSTM, Transformer)
  - 앙상블 모델 (XGBoost, LightGBM)
  - 다중 모델 통합 및 신뢰도 평가

- **스마트 추천 시스템**
  - 리스크 조정 수익률 기반 랭킹
  - 섹터별 분산 추천
  - 추천 근거 및 설명 제공

## 🏗️ 시스템 아키텍처

```
데이터 수집 계층 → 데이터 전처리 계층 → 피처 엔지니어링 계층 
→ 모델링 계층 → 평가/랭킹 계층 → 추천 출력 계층
```

### 주요 모듈

- **Data Collectors**: 주가, 뉴스, 재무제표, 거시경제 데이터 수집
- **Data Processors**: 데이터 정제 및 전처리
- **Feature Engineering**: 기술적/펀더멘털/텍스트 기반 피처 생성
- **Models**: 다양한 ML/DL 모델 학습 및 예측
- **Ranking System**: 주식 랭킹 및 필터링
- **Recommendation Engine**: 최종 추천 생성 및 근거 제공

## 🛠️ 기술 스택

### 데이터 수집
- `yfinance`: 주가 데이터
- `NewsAPI`, `feedparser`: 뉴스 데이터
- `SEC EDGAR`: 재무제표 및 공시 데이터
- `FRED API`: 거시경제 지표

### 데이터 처리
- `pandas`, `numpy`: 데이터 조작 및 분석
- `scikit-learn`: 전처리 및 피처 엔지니어링

### 머신러닝
- `scikit-learn`: 전통적 ML 모델
- `xgboost`, `lightgbm`: 그래디언트 부스팅
- `tensorflow`, `pytorch`: 딥러닝 모델
- `transformers`: NLP 모델 (FinBERT 등)

### 시각화 및 인터페이스
- `matplotlib`, `seaborn`: 데이터 시각화
- `plotly`: 인터랙티브 차트
- `streamlit` / `flask`: 웹 대시보드

## 📁 프로젝트 구조

```
StockRecommend/
├── data_collectors/      # 데이터 수집 모듈
├── data_processors/      # 전처리 모듈
├── feature_engineering/  # 피처 엔지니어링
├── models/               # 모델 정의 및 학습
├── evaluators/           # 평가 및 랭킹
├── backtesting/          # 백테스팅
├── utils/                # 유틸리티
└── main.py              # 메인 실행 파일
```

## 🚀 빠른 시작 (Quick Start)

### 필수 사전 요구사항
- Docker 및 Docker Compose 설치
- Git

### 설치 및 실행

1. **저장소 클론**
   ```bash
   git clone <repository-url>
   cd StockRecommend
   ```

2. **환경 변수 설정**
   ```bash
   # env.example을 복사하여 .env 파일 생성
   cp env.example .env
   
   # .env 파일을 열고 모든 값을 실제 값으로 변경
   # 특히 POSTGRES_PASSWORD와 DATABASE_URL의 비밀번호를 변경하세요!
   ```

3. **Docker 컨테이너 실행**
   ```bash
   docker-compose up -d --build
   ```

4. **서비스 확인**
   ```bash
   # 서비스 상태 확인
   docker-compose ps
   
   # 로그 확인
   docker-compose logs -f
   ```

### 🔒 보안 주의사항

**중요**: 이 프로젝트를 사용하기 전에 반드시 `.env` 파일을 생성하고 강력한 비밀번호를 설정하세요!

- `.env` 파일은 절대 Git에 커밋하지 마세요 (이미 `.gitignore`에 포함됨)
- 프로덕션 환경에서는 반드시 강력한 비밀번호를 사용하세요
- 자세한 보안 가이드는 [SECURITY.md](SECURITY.md)를 참조하세요

## ⚠️ 주의사항

- 본 시스템은 교육 및 연구 목적으로 개발되었습니다.
- 투자 결정에 사용하기 전 충분한 검증이 필요합니다.
- 주식 투자는 손실 위험이 있으며, 본 시스템의 추천은 투자 조언이 아닙니다.
- 실제 투자에 사용할 경우 본인의 판단과 책임 하에 사용하시기 바랍니다.

## 📝 라이선스

[라이선스 정보 추가 예정]

## 🤝 기여

프로젝트 기여를 환영합니다. 이슈나 풀 리퀘스트를 통해 기여해주세요.