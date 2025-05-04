from fastapi import APIRouter, Depends, HTTPException, status, Security
from schemas.recipe import BookmarkCreate, BookmarkOut
from crud.recipe import add_bookmark, remove_bookmark, get_user_bookmarks
from crud.user import get_current_user, oauth2_scheme
from typing import List

router = APIRouter()

@router.post("/", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    bookmark: BookmarkCreate,
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
):
    return await add_bookmark(user_id, bookmark.recipe_id)

@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    recipe_id: str,
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
):
    result = await remove_bookmark(user_id, recipe_id)
    if result["deleted"] == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return

@router.get("/", response_model=List[BookmarkOut])
async def list_bookmarks(
    token: str = Security(oauth2_scheme),
    user_id: str = Depends(get_current_user),
):
    return await get_user_bookmarks(user_id) 