from typing import List, Dict, Any

async def generate_recipe_stats(db) -> List[Dict[str, Any]]:
    """
    레시피 컬렉션을 기반으로 category, difficulty, constitution, mainIngredient별 통계를 생성하여 'recipe_stats' 컬렉션에 저장합니다.
    """
    recipes_col = db['recipes']
    stats_col = db['recipe_stats']
    results: List[Dict[str, Any]] = []

    # 카테고리별 집계
    pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    async for doc in recipes_col.aggregate(pipeline):
        results.append({"dimension": "category", "value": doc["_id"], "count": doc["count"]})

    # 난이도별 집계
    pipeline = [{"$group": {"_id": "$difficulty", "count": {"$sum": 1}}}]
    async for doc in recipes_col.aggregate(pipeline):
        results.append({"dimension": "difficulty", "value": doc["_id"], "count": doc["count"]})

    # 체질별 집계 (suitableBodyTypes 리스트 언와인드)
    pipeline = [
        {"$unwind": "$suitableBodyTypes"},
        {"$group": {"_id": "$suitableBodyTypes", "count": {"$sum": 1}}}
    ]
    async for doc in recipes_col.aggregate(pipeline):
        results.append({"dimension": "constitution", "value": doc["_id"], "count": doc["count"]})

    # 주요 재료별 집계 (mainIngredient 필드 가정)
    pipeline = [{"$group": {"_id": "$mainIngredient", "count": {"$sum": 1}}}]
    async for doc in recipes_col.aggregate(pipeline):
        results.append({"dimension": "ingredient", "value": doc["_id"], "count": doc["count"]})

    # 기존 통계 문서 삭제 후 재삽입
    await stats_col.delete_many({})
    if results:
        await stats_col.insert_many(results)

    return results

async def get_recipe_stats(db) -> List[Dict[str, Any]]:
    """
    저장된 'recipe_stats' 컬렉션에서 모든 통계를 조회하여 반환합니다.
    """
    stats_col = db['recipe_stats']
    docs = await stats_col.find().to_list(length=1000)
    return [{"dimension": doc["dimension"], "value": doc["value"], "count": doc["count"]} for doc in docs] 