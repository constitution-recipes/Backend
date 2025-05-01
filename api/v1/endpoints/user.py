# api/v1/endpoints/user.py
from fastapi import APIRouter, HTTPException, Depends, Security, status, Query, Form
from fastapi.security import OAuth2PasswordBearer

from schemas.user import Token, SignupResponse, UserCreate, UserOut, UserProfileUpdate, UserLogin
from crud.user import create_user, get_user_by_email, get_current_user, oauth2_scheme
from core.security import create_access_token, verify_password, hash_password
from db.session import get_user_db
from bson import ObjectId

router = APIRouter()

@router.get("/email-exists")
async def email_exists(email: str = Query(...), db=Depends(get_user_db)):
    existing_user = await db["users"].find_one({"email": email})
    return {"exists": existing_user is not None}

@router.post("/signup", response_model=SignupResponse)
async def signup(user: UserCreate, db=Depends(get_user_db)):
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user.password = hash_password(user.password)
    created_user = await create_user(db, user)
    response_user = UserOut.from_mongo(created_user)
    access_token = create_access_token(data={"sub": str(created_user["id"])})
    return SignupResponse(user=response_user, access_token=access_token, token_type="bearer")

@router.put("/profile", response_model=UserOut)
async def update_profile(
    profile: UserProfileUpdate,
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
    db=Depends(get_user_db),
):
    await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": profile.model_dump(exclude_unset=True)}
    )
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return UserOut.from_mongo(updated_user)

@router.post("/login", response_model=Token)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db=Depends(get_user_db),
):
    db_user = await get_user_by_email(db, username)
    if not db_user or not verify_password(password, db_user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": str(db_user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    return {"msg": "Logged out successfully"}

@router.get(
    "/me",
    response_model=UserOut,
    summary="현재 로그인 사용자 프로필 조회",
    description="토큰을 통해 현재 로그인한 사용자 정보를 반환합니다."
)
async def get_current_user_profile(
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
    db=Depends(get_user_db)
):
    user_doc = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserOut.from_mongo(user_doc)