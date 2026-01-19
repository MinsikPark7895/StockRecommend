# Python 3.11.6 기반 이미지
FROM python:3.11.6-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 포트 노출 (FastAPI 기본 포트)
EXPOSE 8000

# 애플리케이션 실행 명령 (나중에 FastAPI 앱이 생기면 변경)
CMD ["python", "main.py"]
