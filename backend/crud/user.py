# # crud/user.py
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pymongo.collection import Collection

from core.config import SECRET_KEY, ALGORITHM
from schemas.user import UserCreate, UserOut
from bson import ObjectId
from typing import Optional

from schemas.user import UserCreate
from bson import ObjectId


# async def create_user(db, user: UserCreate):
#     # 새로운 사용자 생성
#     user_dict = user.model_dump()  # Pydantic 모델을 dict로 변환 -> dict는 사장되어 model_dump() 사용
#     user_dict["_id"] = str(ObjectId())  # MongoDB에서 사용하는 _id 필드를 추가 (ObjectId를 사용)
#
#     result = await db["users"].insert_one(user_dict)  # "users" 컬렉션에 데이터 삽입
#     return {**user_dict, "id": str(result.inserted_id)}  # 반환할 때 id는 삽입된 MongoDB 문서의 _id를 사용

async def create_user(db, user: UserCreate):
    user_dict = user.model_dump()
    result = await db["users"].insert_one(user_dict)

    # 실제 삽입된 _id를 사용하여 반환 객체 구성
    user_dict["_id"] = result.inserted_id
    user_dict["id"] = str(result.inserted_id)
    user_dict.pop("password", None)  # 보안상 제거
    return user_dict



async def get_user_by_email(db, email: str):
    return await db["users"].find_one({"email": email})

from fastapi.security import OAuth2PasswordBearer, APIKeyHeader
from jose import JWTError, jwt
from fastapi import HTTPException, Depends

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/users/login",
    scheme_name="BearerAuth"
)
# oauth2_scheme2 = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")

# 현재 사용자 정보 추출 함수
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid or expired token")


# # 현재 사용자 정보 추출 함수 - login에서 사용
# async def get_current_user2(token: str = Depends(oauth2_scheme2)):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#         return user_id
#     except JWTError:
#         raise HTTPException(status_code=403, detail="Invalid or expired token")






# 사용자 생성 함수
# async def create_user(db: Collection, user: UserCreate) -> UserOut:
#     # 비밀번호를 해시하여 저장
#     hashed_password = hash_password(user.password)
#
#     # MongoDB에 사용자 정보 삽입
#     user_data = {
#         "name": user.name,
#         "email": user.email,
#         "phone": user.phone,
#         "hashed_password": hashed_password,
#     }
#
#     result = await db["users"].insert_one(user_data)
#
#     # 삽입된 사용자 데이터를 반환
#     created_user = await db["users"].find_one({"_id": result.inserted_id})
#
#     # MongoDB의 _id 필드는 ObjectId이므로 이를 문자열로 변환하여 반환
#     return UserOut(
#         id=str(created_user["_id"]),
#         name=created_user["name"],
#         email=created_user["email"],
#         phone=created_user["phone"]
#     )

# from motor.motor_asyncio import AsyncIOMotorClient
# from models.user import UserInDB
# from schemas.user import UserCreate
# from passlib.context import CryptContext
# from schemas.user import UserCreate
# from bson import ObjectId
#
# async def create_user(db, user: UserCreate):
#     new_user = {
#         "email": user.email,
#         "name": user.name,
#         "phone_number": user.phone_number,
#         "password": user.password  # 실제로는 비밀번호 해시화가 필요합니다.
#     }
#
#     result = await db["users"].insert_one(new_user)  # users 컬렉션에 데이터 삽입
#     user_id = str(result.inserted_id)  # 삽입된 데이터의 ObjectId를 문자열로 변환하여 반환
#
#     return {**user.dict(), "id": user_id}
#
#
#
# # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# #
# #
# # # 비밀번호 해싱
# # def hash_password(password: str) -> str:
# #     return pwd_context.hash(password)
# #
# #
# # # 회원가입: 사용자를 MongoDB에 저장
# # async def create_user(db: AsyncIOMotorClient, user: UserCreate):
# #     hashed_password = hash_password(user.password)
# #     user_in_db = UserInDB(**user.dict(), hashed_password=hashed_password)
# #
# #     # MongoDB에 사용자 추가
# #     result = await db["users"].insert_one(user_in_db.dict())
# #
# #     return user_in_db
