from fastapi import APIRouter, HTTPException, Depends, Security, Request
from pydantic import BaseModel
from typing import List, Dict, Optional
import requests
import json
from core.config import AI_DATA_URL
from db.session import get_user_db
from bson import ObjectId
from crud.user import get_current_user, oauth2_scheme


class ConstitutionRequest(BaseModel):
    # LLM diagnose endpoint requires 'answers' list of question-answer dicts
    answers: List[Dict[str, str]]


class ConstitutionResponse(BaseModel):
    constitution: str
    reason: str
    confidence: float
    can_diagnose: bool
    next_question: Optional[str] = None


router = APIRouter()

@router.post("", response_model=ConstitutionResponse, summary="사용자-LLM 체질진단 프록시", description="LLM으로 체질 진단 수행 후 유저 DB를 업데이트합니다.")
async def proxy_constitution(
    req: ConstitutionRequest,
    request: Request,
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
    db=Depends(get_user_db)
):
    try:
        payload = {"answers": req.answers}
        # LLM 진단 서비스 호출 (trailing slash 필수)
        resp = requests.post(f"{AI_DATA_URL}/api/v1/diagnose/", json=payload, timeout=None)
        try:
            data = resp.json()
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"LLM 응답 JSON 파싱 실패: {err}")
        resp.raise_for_status()
        # 진단 완료 시 DB 업데이트
        if data.get("can_diagnose") and data.get("constitution"):
            update_fields = {
                "constitution": data["constitution"],
                "constitution_reason": data.get("reason", ""),
                "constitution_confidence": float(data.get("confidence", 0)),
            }
            await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
        # 결과 반환
        return ConstitutionResponse(**data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 