from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import requests
from core.config import AI_DATA_URL
import json
from db.session import get_recipe_db, get_chat_db
from crud.recipe import create_recipe as crud_create_recipe
from crud.chat import add_chat_message as crud_add_chat_message
import httpx

class ChatProxyRequest(BaseModel):
    session_id: Optional[str] = None
    feature: Optional[str] = None
    messages: list[dict[str, str]]

class ChatProxyResponse(BaseModel):
    message: str
    is_recipe: bool = False

router = APIRouter()

@router.post(
    "",
    response_model=ChatProxyResponse,
    summary="사용자-LLM 프록시 챗",
    description="클라이언트 대화를 LLM 서비스로 프록시하고, 응답을 반환합니다."
)
async def proxy_chat(
    req: ChatProxyRequest,
    request: Request,
    recipe_db=Depends(get_recipe_db),
    chat_db=Depends(get_chat_db)
):
    try:
        print(f"AI_DATA_URL: {AI_DATA_URL}")
        print(f"req: {req.dict()}")
        # 사용자가 보낸 메시지를 DB에 저장
        if req.session_id and req.messages:
            last_msg = req.messages[-1]
            if last_msg.get('role') == 'user':
                await crud_add_chat_message(chat_db, req.session_id, 'user', last_msg.get('content'))
        url = f"{AI_DATA_URL}/api/v1/constitution_recipe"
        payload = {"messages": [{"role": m["role"], "content": m["content"]} for m in req.messages]}
        if req.session_id:
            payload["session_id"] = req.session_id
        if req.feature:
            payload["feature"] = req.feature
        resp = requests.post(url, json=payload, timeout=None)
        print(f"status_code: {resp.status_code}")
        try:
            data = resp.json()
            print(f"data: {data}")
        except Exception as json_err:
            print(f"JSON decode error: {json_err}")
            print(f"Response text: {resp.text}")
            raise HTTPException(status_code=500, detail=f"AI 서버 응답이 JSON이 아님: {resp.text}")
        resp.raise_for_status()
        if data.get("is_recipe") and isinstance(data.get("message"), str):
            try:
                recipes_list = json.loads(data["message"])
                # 현재 요청 URL에서 '/api/v1/' 이전 호스트 정보 추출
                api_base = str(request.url).split("/api/v1/")[0]
                stored = []
                async with httpx.AsyncClient() as client:
                    for recipe in recipes_list:
                        r = await client.post(f"{api_base}/api/v1/recipes/save", json=recipe)
                        r.raise_for_status()
                        stored.append(r.json())
                data["message"] = json.dumps(stored, ensure_ascii=False)
                print("레시피 API 저장 및 업데이트 성공: total=", len(stored))
            except Exception as e:
                print("레시피 API 저장 실패:", e)
        if "message" not in data:
            raise HTTPException(status_code=500, detail=f"AI 서버 응답에 'message' 필드가 없음: {data}")
        # 백엔드로부터 받은 응답을 DB에 저장
        assistant_content = data["message"]
        if req.session_id:
            await crud_add_chat_message(chat_db, req.session_id, 'assistant', assistant_content)
        return ChatProxyResponse(message=data["message"], is_recipe=data.get("is_recipe", False))
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 