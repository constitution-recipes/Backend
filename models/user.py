# models/user.py
from pydantic import BaseModel, EmailStr
from bson import ObjectId
from pydantic.networks import EmailStr


# Pydantic 모델을 사용하여 DB에 저장할 데이터 구조 정의
class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str

    class Config:
        # MongoDB에서 사용하는 ObjectId와 Pydantic을 호환하려면 이 설정을 추가
        orm_mode = True

class UserInDB(User):
    hashed_password: str  # 비밀번호는 해시로 저장됨
