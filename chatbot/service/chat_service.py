import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

from chatbot.repository.chat_repo import get_recent_history, save_message
from chatbot.repository.rag_repo import (
    fetch_vector_movies,
    fetch_user_recommendations,
    fetch_user_genre_weights,
)

_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def build_rag_context(user_id: int, query: str) -> dict:
    model = get_embedding_model()
    query_vector = model.encode(query).tolist()

    return {
        "vector_movies":   fetch_vector_movies(query_vector, limit=5),
        "recommendations": fetch_user_recommendations(user_id, limit=5),
        "genre_weights":   fetch_user_genre_weights(user_id, limit=3),
    }


def build_system_prompt(rag_context: dict) -> str:
    vm_lines = "\n".join(
        f"  - {m['title_ko'] or m['title']} ({m['genres']}, 평점 {m['avg_rating']:.1f})"
        for m in rag_context["vector_movies"]
    ) or "  - 없음"

    rec_lines = "\n".join(
        f"  - {m['title_ko'] or m['title']} ({m['genres']}, 추천점수 {m['score']:.2f})"
        for m in rag_context["recommendations"]
    ) or "  - 아직 추천 데이터 없음 (평점을 매기면 생성됩니다)"

    genre_lines = "\n".join(
        f"  - {g['genre']} (가중치 {g['weight']:.1f})"
        for g in rag_context["genre_weights"]
    ) or "  - 아직 행동 데이터 없음"

    return f"""당신은 PopcornPick의 영화 추천 챗봇입니다.
유저의 질문에 친절하고 자연스럽게 답변하세요.

아래 데이터를 참고하여 개인화된 추천과 설명을 제공하세요.

[검색 관련 영화 Top 5]
{vm_lines}

[유저 개인화 추천 Top 5]
{rec_lines}

[유저 장르 선호도 Top 3]
{genre_lines}

규칙:
- 위 데이터를 자연스럽게 활용하되, 데이터가 없으면 일반적인 추천을 해주세요.
- 영화 제목은 한국어 제목을 우선 사용하세요.
- 답변은 간결하고 친근하게 유지하세요.
- 추천 이유를 간단히 설명해주세요.
"""


def chat(session_id: str, user_id: int, user_message: str) -> str:
    # 1. RAG 컨텍스트 생성
    rag_context = build_rag_context(user_id, user_message)

    # 2. 슬라이딩 윈도우 — 최근 5턴(10행)
    history = get_recent_history(session_id, limit=10)

    # 3. Gemini API 초기화
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",  # gemini-2.5-pro도 가능
        system_instruction=build_system_prompt(rag_context),
    )

    # 4. 히스토리 Gemini 포맷으로 변환
    # Gemini는 role이 'user'/'model' 두 가지
    gemini_history = [
        {
            "role": "user" if role == "user" else "model",
            "parts": [content]
        }
        for role, content in history
    ]

    # 5. 대화 세션 시작 후 메시지 전송
    chat_session = model.start_chat(history=gemini_history)
    response = chat_session.send_message(user_message)
    assistant_message = response.text

    # 6. 대화 이력 저장
    save_message(session_id, user_id, "user", user_message, rag_context)
    save_message(session_id, user_id, "assistant", assistant_message)

    return assistant_message