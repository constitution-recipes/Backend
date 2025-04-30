# db/session.py -- MongoDB 연결을 관리, motor를 이용해 mongodb와 연결
# MongoDB는 초기화가 따로 필요하지 않음, 여기서는 필요한 인덱스 등을 설정할 수 있음
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from core.config import settings

# MongoDB 클라이언트 초기화 (TLS CA 번들 설정 포함)
client = AsyncIOMotorClient(
    settings.MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)

# 분리된 데이터베이스 인스턴스
user_db = client.get_database(settings.MONGO_USER_DB_NAME)
recipe_db = client.get_database(settings.MONGO_RECIPE_DB_NAME)

def get_user_db():
    try:
        yield user_db
    finally:
        pass  # DB 연결을 자동으로 종료할 필요가 있을 때 적절한 코드 추가

def get_recipe_db():
    try:
        yield recipe_db
    finally:
        pass  # DB 연결을 자동으로 종료할 필요가 있을 때 적절한 코드 추가
