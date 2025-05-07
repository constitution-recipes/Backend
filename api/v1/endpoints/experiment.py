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
    provider: str
    model: str
    prompt_str: str
    results: List[Dict[str, Any]]
    # 토큰 및 비용 정보 추가
    total_input_tokens: Optional[int] = None
    total_output_tokens: Optional[int] = None
    total_cost: Optional[float] = None
    avg_cost_per_message: Optional[float] = None  # 메시지당 평균 비용 추가
    cost_score: Optional[float] = None  # 비용 기반 정규화 점수
    combined_score: Optional[float] = None  # 레시피 점수와 비용 점수의 조합
    duration: Optional[int] = None  # 실험 총 소요 시간 (ms)
    time_per_message: Optional[float] = None  # 메시지당 평균 소요 시간 (ms)

router = APIRouter()

# 비용 기반 점수 계산 함수 (min-max 정규화) - 메시지당 비용 사용
def calculate_cost_score(cost_per_message, expected_min_cost=0.00001, expected_max_cost=0.01):
    """
    메시지당 비용을 min-max 정규화로 0~1 사이 점수로 변환 (비용이 낮을수록 높은 점수)
    
    Args:
        cost_per_message: 메시지당 평균 비용
        expected_min_cost: 예상 최소 메시지당 비용
        expected_max_cost: 예상 최대 메시지당 비용
    
    Returns:
        0~1 사이의 정규화된 점수 (비용이 낮을수록 1에 가까움)
    """
    if cost_per_message is None:
        return None
    
    # 범위를 벗어난 값 처리
    if cost_per_message <= expected_min_cost:
        return 1.0
    elif cost_per_message >= expected_max_cost:
        return 0.0
    
    # min-max 정규화 (비용이 낮을수록 높은 점수)
    return 1 - ((cost_per_message - expected_min_cost) / (expected_max_cost - expected_min_cost))

# 레시피 점수와 비용 점수를 결합하는 함수
def combine_scores(recipe_score, cost_score, recipe_weight=0.7, cost_weight=0.3):
    """
    레시피 점수와 비용 점수를 가중치를 적용하여 결합
    
    Args:
        recipe_score: 레시피 품질 평가 점수 (0~1)
        cost_score: 비용 기반 정규화 점수 (0~1)
        recipe_weight: 레시피 점수 가중치
        cost_weight: 비용 점수 가중치
    
    Returns:
        결합된 종합 점수 (0~1)
    """
    if recipe_score is None or cost_score is None:
        return recipe_score
    
    return (recipe_score * recipe_weight) + (cost_score * cost_weight)

@router.post("/test", response_model=TestResponse, summary="모델 및 프롬프트 테스트 및 저장")
async def test_experiment(req: TestRequest, db=Depends(get_recipe_db)):
    try:
        start_time = datetime.now()
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
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        message_count = len(results)
        time_per_message = duration_ms / message_count if message_count > 0 else None
        
        # 토큰 정보 추출
        total_input_tokens = data.get('total_input_tokens', 0)
        total_output_tokens = data.get('total_output_tokens', 0)
        total_cost = data.get('total_cost', 0.0)
        avg_cost_per_message = data.get('avg_cost_per_message', 0.0)
        
        # 비용 기반 점수 계산 (메시지당 평균 비용 사용)
        cost_score = calculate_cost_score(avg_cost_per_message)
        
        # 전체 평균 점수 계산
        const_len = len(results)
        overall_average = (sum(item.get('average_score', 0) for item in results) / const_len) if const_len > 0 else 0.0
        
        # 레시피 점수와 비용 점수를 결합한 종합 점수 계산
        combined_score = combine_scores(overall_average, cost_score)
        
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
            # recipe_json 필드가 없으면 {}로
            if 'recipe_json' not in item or item['recipe_json'] is None:
                item['recipe_json'] = {}
                
            # 개별 결과에 비용 점수 추가
            if 'cost' in item and item['cost'] is not None:
                # 개별 아이템의 비용 점수는 그대로 유지 (항목별로는 메시지당 비용 계산이 어려움)
                item['cost_score'] = calculate_cost_score(item['cost'] / 1)  # 개별 항목은 메시지 수가 1로 간주
                item['combined_score'] = combine_scores(item.get('average_score', 0), item['cost_score'])
            
            # DB 저장
            await create_experiment(db, item)
            # 내부 MongoDB ObjectId 제거
            item.pop('_id', None)
        
        # 토큰 정보도 DB에 저장
        token_info = {
            'experiment_id': experiment_id,
            'total_input_tokens': total_input_tokens,
            'total_output_tokens': total_output_tokens,
            'total_cost': total_cost,
            'avg_cost_per_message': avg_cost_per_message,
            'cost_score': cost_score,
            'combined_score': combined_score,
            'duration': duration_ms,
            'time_per_message': time_per_message,
            'created_at': datetime.utcnow()
        }
        await db['experiment_tokens'].insert_one(token_info)
        
        # 응답 반환: 실험 ID, 전체 평균, 개별 결과 리스트, 토큰 정보
        return TestResponse(
            experiment_id=experiment_id,
            overall_average=overall_average,
            provider=req.provider,
            model=req.model,
            prompt_str=req.prompt_str,
            results=results,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            avg_cost_per_message=avg_cost_per_message,
            cost_score=cost_score,
            combined_score=combined_score,
            duration=duration_ms,
            time_per_message=time_per_message
        )
    except Exception as e:
        print('experiment.py 예외 발생:', str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[TestResponse], summary="모든 실험 기록 조회")
async def list_experiments(db=Depends(get_recipe_db)):
    """DB에서 모든 실험을 가져와 experiment_id별로 그룹핑 후 반환합니다."""
    docs = await db['experiments'].find().to_list(10000)
    
    # 토큰 정보 가져오기
    token_docs = await db['experiment_tokens'].find().to_list(1000)
    token_info_map = {doc['experiment_id']: doc for doc in token_docs}
    
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for doc in docs:
        exp_id = doc.get('experiment_id')
        if not exp_id or not isinstance(exp_id, str):  # None, '', 타입 체크
            continue
        grouped.setdefault(exp_id, []).append(doc)
    
    response_list: List[TestResponse] = []
    for exp_id, items in grouped.items():
        # recipe_score만으로 평균 계산
        recipe_scores = [item.get('recipe_score', 0) for item in items]
        overall_avg = sum(recipe_scores) / len(recipe_scores) if recipe_scores else 0.0
        # 대표 provider/model/prompt_str (첫번째)
        provider = items[0].get('provider', '-') if items else '-'
        model = items[0].get('model', '-') if items else '-'
        prompt_str = items[0].get('prompt_str', '-') if items else '-'
        
        # 토큰 정보 추출
        token_info = token_info_map.get(exp_id, {})
        total_input_tokens = token_info.get('total_input_tokens')
        total_output_tokens = token_info.get('total_output_tokens')
        total_cost = token_info.get('total_cost')
        avg_cost_per_message = token_info.get('avg_cost_per_message')
        cost_score = token_info.get('cost_score')
        combined_score = token_info.get('combined_score')
        
        # 토큰 정보가 없는 이전 데이터의 경우 계산
        if total_cost is not None and avg_cost_per_message is None:
            # 이전 데이터를 위한 예상 메시지 수 계산 (최소 1)
            est_message_count = max(len(items), 1)
            avg_cost_per_message = total_cost / est_message_count
            cost_score = calculate_cost_score(avg_cost_per_message)
            combined_score = combine_scores(overall_avg, cost_score)
        
        results: List[Dict[str, Any]] = []
        for item in items:
            # 개별 결과의 비용 점수 계산 (이전 데이터 호환성)
            cost = item.get('cost')
            item_cost_score = item.get('cost_score')
            item_combined_score = item.get('combined_score')
            
            if cost is not None and item_cost_score is None:
                item_cost_score = calculate_cost_score(cost / 1)  # 개별 항목은 메시지 수가 1로 간주
                item_combined_score = combine_scores(item.get('average_score', 0), item_cost_score)
            
            result_item = {
                'conversation_id': item.get('conversation_id'),
                'messages': item.get('messages'),
                'qa_result': item.get('qa_result', []),
                'qa_score': item.get('qa_score', 0),
                'recipe_result': item.get('recipe_result', []),
                'recipe_score': item.get('recipe_score', 0),
                'average_score': item.get('average_score', 0),
                'timestamp': item.get('created_at'),
                'provider': item.get('provider', '-'),
                'model': item.get('model', '-'),
                'prompt_str': item.get('prompt_str', '-'),
                'recipe_json': item.get('recipe_json', None),
                'input_tokens': item.get('input_tokens'),
                'output_tokens': item.get('output_tokens'),
                'cost': cost,
                'cost_score': item_cost_score,
                'combined_score': item_combined_score
            }
            results.append(result_item)
        
        response_list.append(TestResponse(
            experiment_id=exp_id,
            overall_average=overall_avg,
            provider=provider,
            model=model,
            prompt_str=prompt_str,
            results=results,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            total_cost=total_cost,
            avg_cost_per_message=avg_cost_per_message,
            cost_score=cost_score,
            combined_score=combined_score,
            duration=token_info.get('duration'),
            time_per_message=token_info.get('time_per_message')
        ))
    
    # 종합 점수 기준으로 정렬 (없으면 레시피 점수 기준)
    response_list.sort(key=lambda x: x.combined_score if x.combined_score is not None else x.overall_average, reverse=True)
    
    return response_list

@router.delete("/{experiment_id}", summary="experiment_id로 실험 전체 삭제")
async def delete_experiment(experiment_id: str, db=Depends(get_recipe_db)):
    try:
        # 실험 데이터 삭제
        result = await db['experiments'].delete_many({"experiment_id": experiment_id})
        # 토큰 정보도 삭제
        token_result = await db['experiment_tokens'].delete_many({"experiment_id": experiment_id})
        return {"deleted_count": result.deleted_count + token_result.deleted_count}
    except Exception as e:
        print('experiment.py DELETE 예외 발생:', str(e))
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 