# schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str
    allergies: Optional[List[str]] = None
    health_status: Optional[str] = None
    illnesses: Optional[str] = None


class UserProfileUpdate(BaseModel):
    allergies: List[str]
    health_status: str
    illnesses: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone_number: Optional[str]
    allergies: Optional[List[str]]
    health_status: Optional[str]
    illnesses: Optional[str]

    class Config:
        orm_mode = True

    @classmethod
    def from_mongo(cls, document: dict):
        document = cls._preprocess_document(document)
        return cls(**document)

    @staticmethod
    def _preprocess_document(document: dict) -> dict:
        doc = document.copy()

        # _id → id 변환
        doc["id"] = str(doc.get("_id", ""))
        doc.pop("_id", None)

        # 누락된 필드 기본값 보정
        doc.setdefault("phone_number", None)
        doc.setdefault("allergies", None)
        doc.setdefault("health_status", None)
        doc.setdefault("illnesses", None)

        return doc


class SignupResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
