# core/config.py
from pydantic_settings import BaseSettings  # pydantic-settings에서 BaseSettings 가져오기
from pydantic import Field

class Settings(BaseSettings):
    MONGO_URL: str = Field(..., alias="MONGO_URL")  # MongoDB Atlas 연결 URL (db name 제외)
    MONGO_USER_DB_NAME: str = Field(..., alias="MONGO_USER_DB_NAME")   # 사용자 정보용 DB 이름
    MONGO_RECIPE_DB_NAME: str = Field(..., alias="MONGO_RECIPE_DB_NAME") # 레시피 정보용 DB 이름
    MONGO_CHAT_DB_NAME: str = Field(..., alias="MONGO_CHAT_DB_NAME")   # 채팅 정보용 DB 이름
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")  # 비밀 키
    ALGORITHM: str = Field(..., alias="ALGORITHM")  # 기본 알고리즘 설정 (선택사항)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(..., alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    AI_DATA_URL: str = Field(..., alias="AI_DATA_URL")

    class Config:
        # .env 파일에서 환경변수를 읽어옵니다.
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

# 설정 값 로드
settings = Settings()

# 환경 변수에 접근할 때는 `settings` 객체를 통해 접근합니다.
MONGO_URL = settings.MONGO_URL
MONGO_USER_DB_NAME = settings.MONGO_USER_DB_NAME
MONGO_RECIPE_DB_NAME = settings.MONGO_RECIPE_DB_NAME
MONGO_CHAT_DB_NAME = settings.MONGO_CHAT_DB_NAME
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
AI_DATA_URL = settings.AI_DATA_URL