# db/config.py
from core.config import MONGO_URL, MONGO_DB_NAME  # core에서 환경변수 로드한 값 사용

# MongoDB 연결을 위한 추가 설정
def get_db_url():
    return f"{MONGO_URL}{MONGO_DB_NAME}"  # DB 이름을 URL 끝에 추가하여 반환
