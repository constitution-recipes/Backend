import os
import requests
import random
from core.config import settings

CONSTITUTIONS = [
    "목양체질","목음체질","토양체질","토음체질",
    "금양체질","금음체질","수양체질","수음체질"
]
CATEGORIES = ["한식","중식","일식","양식","디저트","음료"]
DIFFICULTIES = ["쉬움","중간","어려움"]
INGREDIENTS = ["육류","해산물","채소","과일","유제품","견과류"]

API_URL = f"{settings.AI_DATA_URL}/api/v1/recipes/auto_generate"
def generate_recipe_payload():
    return {
        "constitution": random.choice(CONSTITUTIONS),
        "category": random.choice(CATEGORIES),
        "difficulty": random.choices(DIFFICULTIES, weights=[0.7,0.2,0.1])[0],
        "keyIngredients": random.sample(
            INGREDIENTS,
            k=random.choices([1,2,3], weights=[0.8,0.15,0.05])[0]
        )
    }

def generate_recipes_batch(count=30):
    recipes = []
    for i in range(count):
        payload = generate_recipe_payload()
        try:
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()
            result = response.json()
            recipes.extend(result)
        except Exception as e:
            print(f"[자동생성] {i+1}/{count} 실패: {e}")
    print(f"[자동생성] {len(recipes)}개 레시피 생성 완료")
    return recipes

if __name__ == "__main__":
    generate_recipes_batch(30)
