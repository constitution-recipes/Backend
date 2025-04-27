# db/session.py -- MongoDB 연결을 관리, motor를 이용해 mongodb와 연결
# MongoDB는 초기화가 따로 필요하지 않음, 여기서는 필요한 인덱스 등을 설정할 수 있음
from motor.motor_asyncio import AsyncIOMotorClient

# MONGO_URL 환경변수에서 가져오기
from core.config import settings

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client.get_database(settings.MONGO_DB_NAME)

def get_db():
    try:
        yield db
    finally:
        pass  # DB 연결을 자동으로 종료할 필요가 있을 때 적절한 코드 추가
