from bson import ObjectId
from datetime import datetime

async def create_chat_session(db, user_id: str, title: str):
    data = {
        "user_id": user_id,
        "title": title,
        "last_message": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = await db["chat_sessions"].insert_one(data)
    # 디버깅: 세션 생성 로그
    print(f"[DEBUG][chat] Created session {result.inserted_id} for user {user_id}")
    return {"id": str(result.inserted_id), **data}

async def get_user_chat_sessions(db, user_id: str):
    sessions = await db["chat_sessions"].find({"user_id": user_id}).sort("updated_at", -1).to_list(100)
    # 디버깅: 세션 조회 로그
    print(f"[DEBUG][chat] Retrieved {len(sessions)} sessions for user {user_id}")
    print("전메세지:",  sessions[0])
    return [
        {
            "id": str(s["_id"]),
            "user_id": s["user_id"],
            "title": s.get("title"),
            "last_message": s.get("last_message"),
            "created_at": s["created_at"],
            "updated_at": s["updated_at"]
        }
        for s in sessions
    ]

async def add_chat_message(db, session_id: str, role: str, content: str):
    msg_data = {
        "session_id": ObjectId(session_id),
        "role": role,
        "content": content,
        "created_at": datetime.utcnow()
    }
    result = await db["chat_messages"].insert_one(msg_data)
    # 세션 업데이트
    await db["chat_sessions"].update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"last_message": content, "updated_at": datetime.utcnow()}}
    )
    return {"id": str(result.inserted_id), **msg_data, "session_id": session_id}

async def get_session_messages(db, session_id: str):
    msgs = await db["chat_messages"].find({"session_id": ObjectId(session_id)}).sort("created_at", 1).to_list(1000)
    print("메세지:", msgs)
    return [
        {
            "id": str(m["_id"]),
            "session_id": str(m["session_id"]),
            "role": m["role"],
            "content": m["content"],
            "created_at": m["created_at"]
        }
        for m in msgs
    ]

async def delete_session_and_messages(db, session_id: str):
    await db["chat_messages"].delete_many({"session_id": ObjectId(session_id)})
    await db["chat_sessions"].delete_one({"_id": ObjectId(session_id)})
    return {"status": "deleted", "session_id": session_id} 