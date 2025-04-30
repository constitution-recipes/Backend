# myapi/api/v1/routers.py
# C:\Users\agile\PycharmProjects\FastapiProject
from fastapi import APIRouter
from api.v1.endpoints import user, recipe

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(recipe.router, prefix="/recipes", tags=["recipes"])

# api_router.include_router(item.router, prefix="/items", tags=["items"])