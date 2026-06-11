from db import get_connection
from collections import defaultdict

from pyspark.sql.functions import when, sum as spark_sum, exploded, split

def aggregate_spark(df):
    print(df.columns)
    # 장르가 여러개인 경우 split해서 가중치 부여  ex)액션,코미디라면 액션, 코미디 나눠서 부여
    exploded_df = (
        df.withColumn(
            "genre_name",
            exploded(split("genres","|"))
        )
    )
    return (
        exploded_df
        .withColumn(
            "score",
            when(df.action_type == "LIKE", 5)
            .when(df.action_type == "RATING", df.rating_value * 3)
            .otherwise(1)
        ).groupBy(
            "user_id",
            "genres"
        ).agg(
            spark_sum("score").alias("weight")
        )
    )


def upsert_weights(df):
    rows = df.collect()
    conn = get_connection()

    try:
        cur = conn.cursor()

        for row in rows:
            cur.execute("""
                INSERT INTO user_genre_weights
                (
                    user_id,
                    genre_name,
                    weight,
                    updated_at
                )
                VALUES (%s,%s,%s,NOW())

                ON CONFLICT(user_id, genre_name)
                DO UPDATE SET
                    weight =
                        user_genre_weights.weight
                        + EXCLUDED.weight,
                    updated_at = NOW()
            """,
            (
                row["user_id"],
                row["genre_name"],
                row["weight"]
            ))

        conn.commit()

    finally:
        cur.close()
        conn.close()