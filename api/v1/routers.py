# myapi/api/v1/routers.py
# C:\Users\agile\PycharmProjects\FastapiProject
from fastapi import APIRouter
from api.v1.endpoints import user, recipe, chat, chat_sessions, constitution, bookmark

api_router = APIRouter()
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/users/chat", tags=["chat"])
api_router.include_router(recipe.router, prefix="/recipes", tags=["recipes"])
api_router.include_router(chat_sessions.router, prefix="/chat", tags=["chat"])
api_router.include_router(constitution.router, prefix="/constitution", tags=["constitution"])
api_router.include_router(bookmark.router, prefix="/bookmarks", tags=["bookmarks"])

# api_router.include_router(item.router, prefix="/items", tags=["items"])