# db/config.py
from core.config import MONGO_URL, MONGO_USER_DB_NAME, MONGO_RECIPE_DB_NAME  # core 설정에서 환경변수 로드

# 사용자 정보용 DB URL
def get_user_db_url():
    return f"{MONGO_URL}{MONGO_USER_DB_NAME}"

# 레시피 정보용 DB URL
def get_recipe_db_url():
    return f"{MONGO_URL}{MONGO_RECIPE_DB_NAME}"
