from pydantic import BaseModel, Field
from typing import List, Optional

class AutoGenerateRecipeRequest(BaseModel):
    """체질 및 선택 항목 기반 자동 레시피 생성을 위한 요청 모델"""
    constitution: str = Field(..., description="체질")
    category: Optional[str] = Field(None, description="카테고리 (한식, 중식, 일식, 양식, 디저트, 음료)")
    difficulty: Optional[str] = Field(None, description="난이도 (쉬움, 중간, 어려움)")
    keyIngredients: Optional[List[str]] = Field(
        None, description="중요 재료 목록 (육류, 해산물, 채소, 과일, 유제품, 견과류)"
    ) 