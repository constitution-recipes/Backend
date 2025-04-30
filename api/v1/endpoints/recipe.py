from fastapi import APIRouter, Depends, HTTPException, status
from db.session import get_recipe_db
from schemas.recipe import Recipe
from crud.recipe import create_recipe as crud_create_recipe, get_recipe_by_id as crud_get_recipe_by_id

router = APIRouter()

@router.post(
    "",
    response_model=Recipe,
    status_code=status.HTTP_201_CREATED,
    summary="새 레시피 생성",
    description="JSON 형태의 레시피를 받아 MongoDB 'recipes' 컬렉션에 저장합니다."
)
async def create_recipe(recipe: Recipe, db=Depends(get_recipe_db)):
    """레시피 JSON을 받아 MongoDB 'recipes' 컬렉션에 저장합니다."""
    return await crud_create_recipe(db, recipe.model_dump())

@router.get("/{recipe_id}", response_model=Recipe, summary="레시피 조회")
async def read_recipe(recipe_id: str, db=Depends(get_recipe_db)):
    recipe_doc = await crud_get_recipe_by_id(db, recipe_id)
    if not recipe_doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="레시피를 찾을 수 없습니다.")
    return recipe_doc 