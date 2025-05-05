# Backend/api/v1/endpoints/experiment.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
import json
from datetime import datetime

from core.config import AI_DATA_URL
from db.session import get_recipe_db
from crud.experiment import create_experiment

# 요청 모델: 실험을 위한 QA 히스토리, 제공자, 모델, 프롬프트
class TestRequest(BaseModel):
    qa_history_json: str
    provider: str
    model: str
    prompt_str: str

# 응답 모델: 프롬프트, 제공자, 모델 정보와 QA/레시피 평가 결과
class TestResponse(BaseModel):
    prompt_str: str
    provider: str
    model: str
    qa_result: List[Dict[str, Any]]
    qa_score: float
    recipe_result: List[Dict[str, Any]]
    recipe_score: float
    average_score: float

router = APIRouter()

@router.post("/test", response_model=TestResponse, summary="모델 및 프롬프트 테스트 및 저장")
async def test_experiment(req: TestRequest, db=Depends(get_recipe_db)):
    try:
        # LLM 마이크로서비스 호출
        url = f"{AI_DATA_URL}/api/v1/constitution_recipe/test"
        resp = requests.post(url, json=req.dict(), timeout=None)
        resp.raise_for_status()
        data = resp.json()
        # 실험 결과 저장
        experiment_data = {
            "prompt_str": data.get("prompt_str"),
            "provider": data.get("provider"),
            "model": data.get("model"),
            "qa_result": data.get("qa_result", []),
            "qa_score": data.get("qa_score", 0),
            "recipe_result": data.get("recipe_result", []),
            "recipe_score": data.get("recipe_score", 0),
            "average_score": data.get("average_score", 0),
            "created_at": datetime.utcnow()
        }
        await create_experiment(db, experiment_data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 