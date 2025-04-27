# core/config.py
from pydantic_settings import BaseSettings  # pydantic-settings에서 BaseSettings 가져오기

class Settings(BaseSettings):
    MONGO_URL: str  # MongoDB Atlas 연결 URL (db name 제외)
    MONGO_DB_NAME: str  # MongoDB 데이터베이스 이름
    SECRET_KEY: str  # 비밀 키
    ALGORITHM: str  # 기본 알고리즘 설정 (선택사항)
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        # .env 파일에서 환경변수를 읽어옵니다.
        env_file = ".env"
        env_file_encoding = "utf-8"

# 설정 값 로드
settings = Settings()

# 환경 변수에 접근할 때는 `settings` 객체를 통해 접근합니다.
MONGO_URL = settings.MONGO_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES