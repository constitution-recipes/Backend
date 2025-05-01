from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from typing import List

from schemas.chat import (
    ChatSessionCreate,
    ChatSessionOut,
    ChatMessageCreate,
    ChatMessageOut
)
from crud.chat import (
    create_chat_session as crud_create_chat_session,
    get_user_chat_sessions,
    add_chat_message as crud_add_chat_message,
    get_session_messages,
    delete_session_and_messages
)
from db.session import get_chat_db

router = APIRouter()

@router.post(
    "/session",
    response_model=ChatSessionOut,
    status_code=status.HTTP_201_CREATED,
    summary="새 채팅 세션 생성",
    description="사용자 ID를 받아 새로운 채팅 세션을 생성하고 ID를 반환합니다."
)
async def create_session(
    session: ChatSessionCreate,
    db=Depends(get_chat_db)
):
    try:
        result = await crud_create_chat_session(db, session.user_id, session.title)
        # 디버깅: 생성된 세션 로그 출력
        print(f"[CHAT_SESSION] Created new session for user {session.user_id}: {result['id']}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/session/{user_id}",
    response_model=List[ChatSessionOut],
    summary="사용자 채팅 세션 목록 조회",
    description="주어진 사용자 ID의 모든 채팅 세션 목록을 반환합니다."
)
async def get_sessions(
    user_id: str,
    db=Depends(get_chat_db)
):
    try:
        return await get_user_chat_sessions(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/message",
    response_model=ChatMessageOut,
    status_code=status.HTTP_201_CREATED,
    summary="채팅 메시지 저장",
    description="세션 ID, 역할, 내용을 받아 새로운 메시지를 저장합니다."
)
async def send_message(
    msg: ChatMessageCreate,
    db=Depends(get_chat_db)
):
    try:
        return await crud_add_chat_message(db, msg.session_id, msg.role, msg.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/messages/{session_id}",
    response_model=List[ChatMessageOut],
    summary="세션별 채팅 메시지 조회",
    description="주어진 세션 ID의 모든 채팅 메시지를 시간순으로 반환합니다."
)
async def get_messages(
    session_id: str,
    db=Depends(get_chat_db)
):
    try:
        return await get_session_messages(db, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/session/{session_id}",
    response_model=dict,
    summary="채팅 세션 및 메시지 삭제",
    description="주어진 세션 ID의 채팅 세션과 모든 메시지를 삭제합니다."
)
async def delete_session(
    session_id: str,
    db=Depends(get_chat_db)
):
    try:
        return await delete_session_and_messages(db, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 