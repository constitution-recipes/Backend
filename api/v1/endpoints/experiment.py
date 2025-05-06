# Backend/api/v1/endpoints/experiment.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import requests
import json
from datetime import datetime
import uuid  # for experiment_id generation
import traceback

from core.config import AI_DATA_URL
from db.session import get_recipe_db
from crud.experiment import create_experiment

# 요청 모델: 다중 대화 세트만 받도록 변경
class TestConversation(BaseModel):
    id: Optional[str] = None
    sid: Optional[str] = None
    messages: List[Dict[str, str]]

class TestRequest(BaseModel):
    message_list: List[TestConversation]
    # AI 공급자 및 모델 연결 정보
    provider: str
    model: str
    prompt_str: str

# 응답 모델: 대화 세트별 평가 결과 리스트
class TestResponse(BaseModel):
    experiment_id: str
    overall_average: float
    results: List[Dict[str, Any]]

router = APIRouter()

@router.post("/test", response_model=TestResponse, summary="모델 및 프롬프트 테스트 및 저장")
async def test_experiment(req: TestRequest, db=Depends(get_recipe_db)):
    try:
        # LLM 마이크로서비스 호출
        resp = requests.post(
            f"{AI_DATA_URL}/api/v1/constitution_recipe/test",
            json=req.dict(),
            timeout=None
        )
        resp.raise_for_status()
        print("resp",resp)
        data = resp.json()
        results = data.get('results', [])
        # 전체 평균 점수 계산
        const_len = len(results)
        overall_average = (sum(item.get('average_score', 0) for item in results) / const_len) if const_len > 0 else 0.0
        # 고유 실험 ID 생성
        experiment_id = str(uuid.uuid4())
        # 실험 결과를 DB에 저장하고, 필요한 필드 추가
        for idx, item in enumerate(results):
            # 그룹 실험 ID
            item['experiment_id'] = experiment_id
            # 대화 식별자와 원본 메시지 추가
            conv = req.message_list[idx]
            item['conversation_id'] = item.get('id') or getattr(conv, 'id', None) or getattr(conv, 'sid', None) or ''
            item['messages'] = conv.messages
            # 요청 메타 정보
            item['provider'] = req.provider
            item['model'] = req.model
            item['prompt_str'] = req.prompt_str
            item['created_at'] = datetime.utcnow()
            # DB 저장
            await create_experiment(db, item)
            # 내부 MongoDB ObjectId 제거
            item.pop('_id', None)
        # 응답 반환: 실험 ID, 전체 평균, 개별 결과 리스트
        return TestResponse(
            experiment_id=experiment_id,
            overall_average=overall_average,
            results=results
        )
    except Exception as e:
        print('experiment.py 예외 발생:', str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TestResponse], summary="모든 실험 기록 조회")
async def list_experiments(db=Depends(get_recipe_db)):
    """DB에서 모든 실험을 가져와 experiment_id별로 그룹핑 후 반환합니다."""
    docs = await db['experiments'].find().to_list(10000)
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for doc in docs:
        exp_id = doc.get('experiment_id')
        if not exp_id or not isinstance(exp_id, str):  # None, '', 타입 체크
            continue
        grouped.setdefault(exp_id, []).append(doc)
    response_list: List[TestResponse] = []
    for exp_id, items in grouped.items():
        # 전체 평균 재계산
        overall_avg = sum(item.get('average_score', 0) for item in items) / len(items) if items else 0.0
        results: List[Dict[str, Any]] = []
        for item in items:
            results.append({
                'conversation_id': item.get('conversation_id'),
                'messages': item.get('messages'),
                'qa_result': item.get('qa_result', []),
                'qa_score': item.get('qa_score', 0),
                'recipe_result': item.get('recipe_result', []),
                'recipe_score': item.get('recipe_score', 0),
                'average_score': item.get('average_score', 0),
                'timestamp': item.get('created_at'),
            })
        response_list.append(TestResponse(
            experiment_id=exp_id,
            overall_average=overall_avg,
            results=results
        ))
    return response_list 