from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends


from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from schemas.user import TokenData  # 토큰에서 뽑아낸 정보 담을 스키마



# # 스웨거에서 jwt 액세스 토큰 인증을 사용하기 위한 설정
# def verify_header(access_token=Security(APIKeyHeader(name='access-token'))):
#     return access_token


# 비밀번호 암호화를 위한 CryptContext 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 비밀번호 해시 함수
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# 반환타입: bool
# 비밀번호 검증 함수
def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    return pwd_context.verify(plain_pw, hashed_pw)


# 토큰 생성 함수
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire}) # 만료일을 토큰에 포함
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 토큰 검증 함수
def verify_token(token: str):
    try:
        # JWT 디코딩 및 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 만약 토큰에 만료일이 포함되어 있다면, 이를 체크
        if "exp" in payload:
            expiration_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            if expiration_time < datetime.now(tz=timezone.utc):
                raise HTTPException(status_code=403, detail="Token has expired")

        return payload  # payload가 유효한 토큰이라면 반환
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")



