from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional
import requests
from core.config import AI_DATA_URL
import json
from db.session import get_recipe_db, get_chat_db
from crud.recipe import create_recipe as crud_create_recipe
from crud.chat import add_chat_message as crud_add_chat_message
import httpx

router = APIRouter()

@router.post("/")
async def evaluate_recipe(qa_history_json: str):
    url = f"{AI_DATA_URL}/api/v1/evaluate_recipe"
    payload = {"qa_history_json": qa_history_json}
    response = requests.post(url, json=payload)
    return response.json()
