# 🩺🍽️ ChiDiet Backend

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/Pydantic-176C9B?style=for-the-badge&logo=pydantic&logoColor=white"> <img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white"> <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white">

## Project Overview
ChiDiet 백엔드 API 서버는 한의학 기반 체질 진단 및 개인화된 레시피 추천 기능을 제공하는 플랫폼의 핵심 엔진입니다. FastAPI와 MongoDB를 사용해 높은 성능과 확장성을 보장하며, WebSocket을 통한 실시간 채팅 기능과 JWT 기반 인증을 지원합니다.

## Project Structure
```
Backend
 ┣ .github
 ┣ .gitignore
 ┣ Dockerfile
 ┣ requirements.txt
 ┣ main.py
 ┣ api
 ┃ ┗ v1
 ┃   ┣ routers
 ┃   ┗ endpoints
 ┃     ┣ chat.py
 ┃     ┗ recipe.py
 ┣ core
 ┣ crud
 ┣ db
 ┃ ┣ config.py
 ┃ ┣ mongo.py
 ┃ ┗ session.py
 ┣ models
 ┣ schemas
 ┗ utils
```

## Usage
### `docker`
- **이미지 빌드**: Dockerfile을 사용해 백엔드 이미지를 빌드합니다.
- **컨테이너 실행**: 빌드된 이미지를 사용해 API 서버를 실행합니다.

```bash
docker build -t backend .
docker run -d -p 6000:6000 backend
```

## Getting Started
### Setup
#### Local Development
1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```
2. 환경 변수 설정 (`.env` 파일 생성)
   ```env
   MONGODB_URI=<your-mongodb-uri>
   JWT_SECRET_KEY=<your-secret-key>
   ```
3. 개발 서버 실행
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 6000
   ```

#### Docker Deployment
1. Docker 이미지 빌드 및 실행
   ```bash
   docker build -t chi-diet-backend .
   docker run -d -p 1492:1492 chi-diet-backend
   ```

## License
This project is licensed under the MIT License.
