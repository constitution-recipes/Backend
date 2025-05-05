# Backend/crud/experiment.py
# 실험 결과를 저장하는 CRUD 유틸리티
from datetime import datetime

async def create_experiment(db, experiment_data: dict) -> dict:
    """
    MongoDB 'experiments' 컬렉션에 실험 결과를 저장하고 id 필드를 문자열로 변환해 반환합니다.
    """
    result = await db['experiments'].insert_one(experiment_data)
    experiment_data['id'] = str(result.inserted_id)
    return experiment_data 