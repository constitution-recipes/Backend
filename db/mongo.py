# db/mongo.py
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
from core.config import settings  # BaseSettings 인스턴스 import
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure  # MongoDB 연결 오류 처리
from contextlib import asynccontextmanager

client: AsyncIOMotorClient = None
db = None

# MongoDB 클라이언트 및 데이터베이스 연결 초기화
@asynccontextmanager
async def init_db(app=None):
    global client, db
    try:
        # MongoDB 연결
        client = AsyncIOMotorClient(
            settings.MONGO_URL,
            tls=True,
            tlsCAFile=certifi.where()
        )
        db_name = settings.MONGO_USER_DB_NAME  # 사용자 정보용 기본 DB 이름
        db = client[db_name]

        # 연결이 성공했는지 확인 (간단히 ping 테스트)
        client.admin.command('ping')  # MongoDB 연결 상태 확인

        print(f"MongoDB 연결 성공: {db_name}")

        # FastAPI 애플리케이션이 종료될 때까지 유지
        yield

    except ConnectionFailure as e:
        print(f"MongoDB 연결 실패: {e}")
        raise Exception("MongoDB 연결에 실패했습니다.")  # 예외를 다시 던져서 다른 로직에서 처리하도록 할 수 있습니다.
    finally:
        if client:
            client.close()  # MongoDB 클라이언트 종료
            print("MongoDB 연결 종료")

# 사용되는 데이터베이스와 컬렉션 가져오기
def get_collection(collection_name: str) -> Collection:
    if db is None:
        raise Exception("MongoDB 데이터베이스에 연결되지 않았습니다.")
    return db.get_collection(collection_name)
