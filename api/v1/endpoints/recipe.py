from fastapi import APIRouter, Depends, HTTPException, status, Security
from db.session import get_recipe_db
from schemas.recipe import Recipe, BookmarkCreate, BookmarkOut
from crud.recipe import create_recipe as crud_create_recipe, get_recipe_by_id as crud_get_recipe_by_id, add_bookmark, remove_bookmark, get_user_bookmarks
from crud.user import get_current_user, oauth2_scheme
from typing import List

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