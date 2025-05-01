# # myapi/main.py

import asyncio
import sys
from fastapi.openapi.utils import get_openapi
from starlette.websockets import WebSocket

from db.mongo import init_db
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.v1.routers import api_router
from fastapi.security import APIKeyHeader
from api.v1.endpoints.chat import router as chat_router
from api.v1.endpoints.recipe import router as recipe_router

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


app = FastAPI(
    title="My FastAPI Project",
    description="API documentation",
    version="1.0.0",
    lifespan=init_db,  # lifespan으로 MongoDB 연결 처리
)
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="My API",
        version="1.0.0",
        description="API for testing",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# # FastAPI에 CORS 예외 URL을 등록
# origins = [
#     #"http://127.0.0.1:5173",    # 또는 "http://localhost:5173"
#     "http://localhost:3001",
#     "http://127.0.0.1:3001",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 웹소켓 연결 처리 예시
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 웹소켓 연결 종료
        await websocket.close()  # 명시적으로 연결 종료


app.include_router(api_router, prefix="/api/v1")  # api_router에 user/chat/recipe 라우터 모두 포함됨


if __name__ == "__main__":
    # Windows 환경에서만 이벤트 루프 정책 설정
    if sys.platform == "win32" and sys.version_info >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.SelectorEventLoopPolicy())
    uvicorn.run("main:app", host="0.0.0.0", port=1492)
