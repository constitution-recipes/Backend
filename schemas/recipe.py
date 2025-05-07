from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Recipe(BaseModel):
    id: Optional[str] = Field(None, description="레시피 고유 ID")
    title: str = Field(..., description="레시피 제목")
    description: str = Field(..., description="레시피 설명")
    difficulty: str = Field(..., description="난이도")
    cookTime: str = Field(..., description="조리 시간")
    ingredients: list[str] = Field(..., description="재료 목록")
    image: str = Field(..., description="이미지 URL")
    rating: float = Field(..., description="평점")
    suitableFor: str = Field(..., description="적합 대상 설명")
    suitableBodyTypes: list[str] = Field(default_factory=list, description="이 음식에 적합한 체질 리스트 (목양체질, 목음체질, 토양체질, 토음체질, 금양체질, 금음체질, 수양체질, 수음체질)")
    reason: Optional[str] = Field(None, description="레시피 생성 이유 설명")
    tags: list[str] = Field(..., description="태그 목록")
    steps: list[str] = Field(..., description="조리 단계 리스트")
    servings: str = Field(..., description="인분 정보")
    nutritionalInfo: str = Field(..., description="영양 정보")
    category: str = Field(..., description="카테고리 (한식, 중식 등)")
    keyIngredients: list[str] = Field(..., description="중요 재료 목록 (육류, 해산물 등)")
    lastEditReason: Optional[str] = Field(None, description="최신 수정 사유")

class BookmarkCreate(BaseModel):
    recipe_id: str = Field(..., description="레시피 ID")

class BookmarkOut(BaseModel):
    id: Optional[str] = Field(None, description="북마크 고유 ID")
    user_id: str = Field(..., description="유저 ID")
    recipe_id: str = Field(..., description="레시피 ID")
    created_at: Optional[datetime] = Field(None, description="생성일시")

class RecipeUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, description="레시피 제목")
    description: Optional[str] = Field(None, description="레시피 설명")
    difficulty: Optional[str] = Field(None, description="난이도")
    cookTime: Optional[str] = Field(None, description="조리 시간")
    ingredients: Optional[list[str]] = Field(None, description="재료 목록")
    image: Optional[str] = Field(None, description="이미지 URL")
    rating: Optional[float] = Field(None, description="평점")
    suitableFor: Optional[str] = Field(None, description="적합 대상 설명")
    suitableBodyTypes: Optional[list[str]] = Field(None, description="이 음식에 적합한 체질 리스트 (목양체질, 목음체질, 토양체질, 토음체질, 금양체질, 금음체질, 수양체질, 수음체질)")
    tags: Optional[list[str]] = Field(None, description="태그 목록")
    steps: Optional[list[str]] = Field(None, description="조리 단계 리스트")
    servings: Optional[str] = Field(None, description="인분 정보")
    nutritionalInfo: Optional[str] = Field(None, description="영양 정보")
    category: Optional[str] = Field(None, description="카테고리 (한식, 중식 등)")
    keyIngredients: Optional[list[str]] = Field(None, description="중요 재료 목록 (육류, 해산물 등)")
    editReason: str = Field(..., description="수정 사유")
