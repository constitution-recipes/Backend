from fastapi import APIRouter, Depends, HTTPException, status, Security
from db.session import get_recipe_db
from schemas.recipe import Recipe, BookmarkCreate, BookmarkOut, RecipeUpdateRequest
from crud.recipe import create_recipe as crud_create_recipe, get_recipe_by_id as crud_get_recipe_by_id, add_bookmark, remove_bookmark, get_user_bookmarks, update_recipe as crud_update_recipe
from crud.user import get_current_user, oauth2_scheme
from typing import List
from schemas.auto_generate import AutoGenerateRecipeRequest
import httpx
from core.config import AI_DATA_URL

router = APIRouter()

@router.get(
    "/get_all_recipes",
    response_model=List[Recipe],
    summary="모든 레시피 조회",
    description="MongoDB 'recipes' 컬렉션에 저장된 모든 레시피를 반환합니다."
)
async def list_recipes(db=Depends(get_recipe_db)):
    """저장된 모든 레시피를 조회하여 반환합니다."""
    docs = await db['recipes'].find().to_list(length=1000)
    for doc in docs:
        doc['id'] = str(doc['_id'])
    return docs

@router.get(
    "/{recipe_id}", response_model=Recipe, summary="레시피 조회"
)
async def read_recipe(recipe_id: str, db=Depends(get_recipe_db)):
    recipe_doc = await crud_get_recipe_by_id(db, recipe_id)
    if not recipe_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다.")
    return recipe_doc

@router.post(
    "/save",
    response_model=Recipe,
    status_code=status.HTTP_201_CREATED,
    summary="새 레시피 생성",
    description="JSON 형태의 레시피를 받아 MongoDB 'recipes' 컬렉션에 저장합니다."
)
async def create_recipe(recipe: Recipe, db=Depends(get_recipe_db)):
    """레시피 JSON을 받아 MongoDB 'recipes' 컬렉션에 저장합니다."""
#         return await crud_create_recipe(db, recipe.model_dump())

# @router.post("/", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
# async def create_bookmark(
#     bookmark: BookmarkCreate,
#     token: str = Security(oauth2_scheme),
#     user_id: str = Depends(get_current_user),
# ):
#     return await add_bookmark(user_id, bookmark.recipe_id)

# @router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_bookmark(
#     recipe_id: str,
#     token: str = Security(oauth2_scheme),
#     user_id: str = Depends(get_current_user),
# ):
#     result = await remove_bookmark(user_id, recipe_id)
#     if result["deleted"] == 0:
#         raise HTTPException(status_code=404, detail="Bookmark not found")
#     return

# @router.get("/", response_model=List[BookmarkOut])
# async def list_bookmarks(
#     token: str = Security(oauth2_scheme),
#     user_id: str = Depends(get_current_user),
# ):
#     return await get_user_bookmarks(user_id)
    return await crud_create_recipe(db, recipe.model_dump()) 

@router.post("/save/", include_in_schema=False)
async def create_recipe_slash(recipe: Recipe, db=Depends(get_recipe_db)):
    return await crud_create_recipe(db, recipe.model_dump())

@router.post(
    "/auto_generate",
    response_model=List[Recipe],
    summary="자동 레시피 생성",
    description="체질 및 선택 항목 기반 자동 레시피 생성"
)
async def auto_generate_recipe(req: AutoGenerateRecipeRequest, db=Depends(get_recipe_db)):
    """Ai-Data LLM 서비스에 요청해 자동 생성된 레시피를 반환합니다."""
    url = f"{AI_DATA_URL}/api/v1/constitution_recipe/auto_generate"
    # LLM 서비스 호출: timeout 및 오류 처리
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.post(url, json=req.dict())
            resp.raise_for_status()
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="LLM 레시피 서비스 호출 타임아웃")
        except httpx.HTTPError as e:
            raise HTTPException(status_code=502, detail=f"LLM 레시피 생성 실패: {e}")
    # JSON 응답 파싱
    try:
        generated = resp.json()
    except ValueError:
        raise HTTPException(status_code=502, detail="LLM 응답 JSON 파싱 실패")

    # DB에 저장 및 반환
    saved_recipes: list[dict] = []
    for item in generated:
        saved = await crud_create_recipe(db, item)
        saved_recipes.append(saved)
    return saved_recipes 

@router.delete(
    "/delete_all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="모든 레시피 삭제",
    description="MongoDB 'recipes' 컬렉션의 모든 레시피를 삭제합니다."
)
async def delete_all_recipes(db=Depends(get_recipe_db)):
    """저장된 모든 레시피를 삭제합니다."""
    try:
        result = await db['recipes'].delete_many({})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="삭제할 레시피가 없습니다."
            )
        return {"message": f"{result.deleted_count}개의 레시피가 삭제되었습니다."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"레시피 삭제 중 오류가 발생했습니다: {str(e)}"
        ) 

@router.patch(
    "/{recipe_id}/edit",
    response_model=Recipe,
    summary="레시피 수정 및 수정 사유 저장",
    description="레시피 필드를 수정하고 수정 사유를 기록합니다."
)
async def update_recipe_endpoint(recipe_id: str, req: RecipeUpdateRequest, db=Depends(get_recipe_db)):
    existing = await crud_get_recipe_by_id(db, recipe_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다.")
    updated = await crud_update_recipe(db, recipe_id, req.model_dump())
    return updated 