import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from chatbot.service.chat_service import chat
from chatbot.repository.chat_repo import get_recent_history

router = APIRouter()


class ChatRequest(BaseModel):
    user_id:    int
    message:    str
    session_id: Optional[str] = None  # 없으면 새 세션 생성


class ChatResponse(BaseModel):
    session_id: str
    reply:      str


class HistoryResponse(BaseModel):
    session_id: str
    messages:   list[dict]


@router.post("", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest):
    """챗봇 메시지 전송"""
    # 세션 없으면 새로 생성
    session_id = payload.session_id or str(uuid.uuid4())

    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="메시지를 입력하세요.")

    try:
        reply = chat(
            session_id=session_id,
            user_id=payload.user_id,
            user_message=payload.message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 오류: {str(e)}")

    return ChatResponse(session_id=session_id, reply=reply)


@router.get("/history/{session_id}", response_model=HistoryResponse)
def get_history(session_id: str):
    """대화 이력 조회"""
    history = get_recent_history(session_id, limit=20)
    messages = [{"role": r, "content": c} for r, c in history]
    return HistoryResponse(session_id=session_id, messages=messages)


@router.get("/sessions/{user_id}")
def get_sessions(user_id: int):
    """날짜별 세션 목록"""
    from chatbot.repository.chat_repo import get_sessions_by_user
    return get_sessions_by_user(user_id)

@router.get("/today/{user_id}")
def get_today(user_id: int):
    """오늘 세션 ID 조회"""
    from chatbot.repository.chat_repo import get_today_session
    session_id = get_today_session(user_id)
    return {"session_id": session_id}