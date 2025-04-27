# FROM python:3.10.5-alpine
FROM python:3.10-alpine

# 필수 패키지 설치 (빌드를 위한 의존성)
RUN apk add --no-cache gcc musl-dev libffi-dev libxml2-dev libxslt-dev openssl-dev python3-dev cargo

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 파일을 먼저 복사하고, 의존성 설치
COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 포트 노출
EXPOSE 8000

# 컨테이너 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]