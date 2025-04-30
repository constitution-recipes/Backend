from pydantic import BaseModel, Field
from typing import List

class Recipe(BaseModel):
    id: str = Field(..., description="레시피 고유 ID")
    title: str = Field(..., description="레시피 제목")
    description: str = Field(..., description="레시피 설명")
    difficulty: str = Field(..., description="난이도")
    prepTime: str = Field(..., description="준비 시간")
    cookTime: str = Field(..., description="조리 시간")
    ingredients: List[str] = Field(..., description="재료 목록")
    image: str = Field(..., description="이미지 URL")
    rating: float = Field(..., description="평점")
    suitableFor: str = Field(..., description="적합 대상 설명")
    tags: List[str] = Field(..., description="태그 목록")
    steps: List[str] = Field(..., description="조리 단계 리스트")
    servings: str = Field(..., description="인분 정보")
    nutritionalInfo: str = Field(..., description="영양 정보") 