from db import get_connection

def fetch_popular_movies(limit: int = 10):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT movie_id, title, title_ko, genres,
                   poster_path, vote_average, avg_rating, click_count
            FROM movies
            ORDER BY avg_rating DESC, click_count DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()
    except Exception as e:
        print(f"Error fetching popular movies: {e}")
        return []
    finally:
        cur.close()
        conn.close()