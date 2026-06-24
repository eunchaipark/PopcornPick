import json
from db import get_connection


def get_recent_history(session_id: str, limit: int = 10):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
                    SELECT role, content
                    FROM (SELECT role, content, created_at
                          FROM chat_histories
                          WHERE session_id = %s
                          ORDER BY created_at DESC
                              LIMIT %s) sub
                    ORDER BY created_at ASC
                    """, (session_id, limit))
        return cur.fetchall()  # [(role, content), ...]
    finally:
        cur.close()
        conn.close()


def save_message(session_id: str, user_id: int, role: str,
                 content: str, rag_context: dict = None):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
                    INSERT INTO chat_histories
                        (session_id, user_id, role, content, rag_context)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (
                        session_id,
                        user_id,
                        role,
                        content,
                        json.dumps(rag_context) if rag_context else None
                    ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def get_sessions_by_user(user_id: int):
    """유저의 날짜별 세션 목록 조회"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                session_id,
                MIN(content) AS preview,
                DATE(MIN(created_at)) AS date,
                MIN(created_at) AS started_at
            FROM chat_histories
            WHERE user_id = %s AND role = 'user'
            GROUP BY session_id
            ORDER BY MIN(created_at) DESC
        """, (user_id,))
        rows = cur.fetchall()
        return [
            {
                "session_id": r[0],
                "preview":    r[1][:30] + "..." if len(r[1]) > 30 else r[1],
                "date":       str(r[2]),
                "started_at": str(r[3]),
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def get_today_session(user_id: int):
    """오늘 가장 최근 세션 ID 조회"""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT session_id
            FROM chat_histories
            WHERE user_id = %s
              AND DATE(created_at) = CURRENT_DATE
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        cur.close()
        conn.close()