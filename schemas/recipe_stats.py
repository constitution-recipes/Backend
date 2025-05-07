from pydantic import BaseModel, Field
from typing import Literal, Union

CuisineType = Literal['한식','중식','일식','양식','디저트','음료']
DifficultyLevel = Literal['쉬움','중간','어려움']
ConstitutionType = Literal[
    '목양체질','목음체질','토양체질','토음체질',
    '금양체질','금음체질','수양체질','수음체질'
]
MainIngredient = Literal['육류','해산물','채소','과일','유제품','견과류']

class RecipeStat(BaseModel):
    """레시피 통계 스키마: 차원(dimension)별 값(value)과 카운트(count)을 저장합니다."""
    dimension: Literal['category', 'difficulty', 'constitution', 'ingredient'] = Field(
        ..., description="통계 차원 (분류, 난이도, 체질, 주요 재료)"
    )
    value: Union[CuisineType, DifficultyLevel, ConstitutionType, MainIngredient] = Field(
        ..., description="해당 차원에서의 세부 값"
    )
    count: int = Field(..., description="해당 값에 대한 레시피 갯수") 