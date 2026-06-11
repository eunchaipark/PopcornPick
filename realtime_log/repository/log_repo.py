from db import get_connection


def insert_log(payload):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = """
            INSERT INTO user_click_logs
            (
                user_id,
                movie_id,
                genres,
                action_type,
                rating_value
            )
            VALUES (%s,%s,%s,%s,%s)
            """

            cursor.execute(
                sql,
                (
                    payload.user_id,
                    payload.movie_id,
                    payload.genres,
                    payload.action_type,
                    payload.rating_value
                )
            )

        conn.commit()
    finally:
        cursor.close()
        conn.close()