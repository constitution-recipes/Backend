from fastapi import APIRouter, Depends
from typing import List
from db.session import get_recipe_db
from schemas.recipe_stats import RecipeStat
from crud.recipe_stats import generate_recipe_stats, get_recipe_stats

router = APIRouter()

@router.post("/generate", response_model=List[RecipeStat], summary="레시피 통계 생성", description="레시피 데이터를 집계하여 통계를 생성하고 저장합니다.")
async def generate_stats(db=Depends(get_recipe_db)) -> List[RecipeStat]:
    """category, difficulty, constitution, ingredient별 레시피 통계를 생성합니다."""
    return await generate_recipe_stats(db)

@router.get("/", response_model=List[RecipeStat], summary="레시피 통계 조회", description="저장된 레시피 통계를 조회합니다.")
async def retrieve_stats(db=Depends(get_recipe_db)) -> List[RecipeStat]:
    """저장된 레시피 통계를 반환합니다."""
    return await get_recipe_stats(db) 