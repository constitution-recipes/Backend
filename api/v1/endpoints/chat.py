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
    # 사용자 컨텍스트 필드 추가
    allergies: Optional[list[str]] = None
    constitution: Optional[str] = None
    dietary_restrictions: Optional[list[str]] = None
    health_conditions: Optional[str] = None

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
        # AI 서버로 보낼 payload에 사용자 컨텍스트 포함
        payload = {
            "messages": [{"role": m["role"], "content": m["content"]} for m in req.messages],
            "session_id": req.session_id,
            "feature": req.feature,
            "allergies": req.allergies,
            "constitution": req.constitution,
            "dietary_restrictions": req.dietary_restrictions,
            "health_conditions": req.health_conditions
        }
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
                # 리다이렉트 없이 올바른 스킴과 호스트를 사용하기 위해 base_url 활용
                api_base = str(request.base_url).rstrip("/")
                stored = []
                # 리다이렉트를 따라가도록 설정
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    for recipe in recipes_list:
                        r = await client.post(f"{api_base}/api/v1/recipes/save", json=recipe, follow_redirects=True)
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