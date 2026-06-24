from db import get_connection


def fetch_vector_movies(query_vector: list, limit: int = 5):
    conn = get_connection()
    try:
        cur = conn.cursor()
        vector_str = "[" + ",".join(str(v) for v in query_vector) + "]"
        cur.execute("""
                    SELECT movie_id, title, title_ko, genres, avg_rating
                    FROM movies
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                        LIMIT %s
                    """, (vector_str, limit))
        rows = cur.fetchall()
        return [
            {
                "movie_id": r[0],
                "title": r[1],
                "title_ko": r[2],
                "genres": r[3],
                "avg_rating": r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def fetch_user_recommendations(user_id: int, limit: int = 5):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
                    SELECT m.movie_id, m.title, m.title_ko, m.genres, r.score, r.rank
                    FROM recommendations r
                             JOIN movies m ON r.movie_id = m.movie_id
                    WHERE r.user_id = %s
                      AND r.batch_run_at = (SELECT MAX(batch_run_at)
                                            FROM recommendations
                                            WHERE user_id = %s)
                    ORDER BY r.rank
                        LIMIT %s
                    """, (user_id, user_id, limit))
        rows = cur.fetchall()
        return [
            {
                "movie_id": r[0],
                "title": r[1],
                "title_ko": r[2],
                "genres": r[3],
                "score": r[4],
                "rank": r[5],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def fetch_user_genre_weights(user_id: int, limit: int = 3):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
                    SELECT genre_name, weight
                    FROM user_genre_weights
                    WHERE user_id = %s
                    ORDER BY weight DESC
                        LIMIT %s
                    """, (user_id, limit))
        rows = cur.fetchall()
        return [{"genre": r[0], "weight": r[1]} for r in rows]
    finally:
        cur.close()
        conn.close()
