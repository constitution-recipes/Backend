# api/v1/endpoints/user.py
from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader, OAuth2PasswordRequestForm, OAuth2PasswordBearer

from schemas.user import Token, SignupResponse  # 또는 schemas.user에서 정의했다면 해당 위치에서 import

from core.security import create_access_token, verify_password, hash_password
from schemas.user import UserCreate, UserOut, UserProfileUpdate, UserLogin
from crud.user import create_user, get_user_by_email, get_current_user, oauth2_scheme
from db.session import get_db  # DB 세션을 가져오는 함수
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Form

router = APIRouter()

@router.post("/signup", response_model=SignupResponse)
async def signup(user: UserCreate, db=Depends(get_db)):
    # 이메일 중복 체크
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 비밀번호
    user.password = hash_password(user.password)

    # 사용자 생성
    created_user = await create_user(db, user)

    # MongoDB ObjectId를 문자열로 변환
    # _id 필드는 보통 str(created_user["_id"])로 문자열로 변환해서 id 필드로 넘기고 _id는 제거하는 게 일반적인 패턴
    created_user["id"] = str(created_user["_id"])
    created_user.pop("_id", None)  # response_model에는 _id가 없으므로 제거

    # 반환할 데이터를 UserOut 모델에 맞게 구성
    # 반환할 데이터 준비
    response_user = UserOut.from_mongo(created_user)


    # 생성된 사용자의 _id를 사용하여 JWT 토큰 생성
    access_token = create_access_token(data={"sub": str(created_user["id"])})
    # 토큰과 함께 사용자 정보 반환
    return SignupResponse(
        user=response_user,
        access_token=access_token,
        token_type="bearer"
    )

#profile: UserProfileUpdate
#사용자가 보낸 수정할 프로필 데이터 (body)를 받음
#: {"allergies": ["peanut"], "illnesses": "none"}
# user_id: str = Depends(get_current_user)
# JWT 토큰에서 유저 ID를 추출해줌
# get_current_user() 함수는 보통 토큰을 검증하고 유저 ID(sub)를 반환
# 이 ID로 MongoDB에서 _id를 찾을 수 있음

# db=Depends(get_db)
# MongoDB 세션 (Motor 클라이언트) 주입
#
# from fastapi import Security
# from fastapi.security import APIKeyHeader
# # # 스웨거에서 jwt 액세스 토큰 인증을 사용하기 위한 설정
# def verify_header(access_token=Security(APIKeyHeader(name='access-token'))):
#     return access_token

@router.put("/profile", response_model=UserOut)
# 서버는 Depends(get_current_user)를 사용하여 요청에 포함된 JWT 토큰을 확인하고, 이를 바탕으로 사용자 인증을 진행합니다.
async def update_profile(
        profile: UserProfileUpdate,
        token: str = Security(oauth2_scheme),  # direct security dependency for Swagger UI
        user_id: str = Depends(get_current_user), # get_current_user handles token extraction
        db=Depends(get_db),
):
    print('profile object:', profile)
    print('profile.illnesses:', profile.illnesses)
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},# _id가 user_id인 문서를 찾아서,
        {"$set": profile.model_dump(exclude_unset=True)}
        # 전달받은 프로필 중 값이 들어있는 필드만 $set으로 덮어씀
        # exclude_unset=True는 요청 본문에 없는 필드는 수정하지 않도록 방지함
    )
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return UserOut.from_mongo(updated_user)

# @router.post("/login", response_model=Token)
# async def login(user: UserLogin, db=Depends(get_db)):
#     db_user = await get_user_by_email(db, user.email)
#     if not db_user or not verify_password(user.password, db_user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     access_token = create_access_token(data={"sub": db_user["_id"]})
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(
    username: str = Form(...),  # username은 email을 의미
    password: str = Form(...),
    db=Depends(get_db)
):
    db_user = await get_user_by_email(db, username)
    if not db_user or not verify_password(password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(db_user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    # JWT 토큰을 삭제하는 방식은 클라이언트 측에서 처리되므로, 여기서는 빈 응답만 반환
    return {"msg": "Logged out successfully"}

# # Swagger Bearer 폼 생성용 (실 운영에서는 쓰지않음?)
# @router.post("/token", response_model=Token)
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),  # ← Swagger용 Form 형식
#     db=Depends(get_db)
# ):
#     db_user = await get_user_by_email(db, form_data.username)
#     if not db_user or not verify_password(form_data.password, db_user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")
#
#     access_token = create_access_token(data={"sub": str(db_user["_id"])})
#     return {"access_token": access_token, "token_type": "bearer"}

@router.post("/token")
async def login():
    return {"access_token": "test", "token_type": "bearer"}