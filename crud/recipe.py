from bson import ObjectId

async def create_recipe(db, recipe_data: dict) -> dict:
    """MongoDB 'recipes' 컬렉션에 레시피를 저장하고, id 필드를 문자열로 변환해 반환합니다."""
    # 클라이언트로부터 들어온 id 필드 제거
    recipe_data.pop('id', None)
    result = await db['recipes'].insert_one(recipe_data)
    recipe_data['id'] = str(result.inserted_id)
    return recipe_data

async def get_recipe_by_id(db, recipe_id: str) -> dict | None:
    """주어진 ID의 레시피를 조회하여 id 필드를 문자열로 변환해 반환합니다."""
    doc = await db['recipes'].find_one({'_id': ObjectId(recipe_id)})
    if not doc:
        return None
    doc['id'] = str(doc['_id'])
    return doc 