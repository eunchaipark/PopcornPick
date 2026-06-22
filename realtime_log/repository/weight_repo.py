from db import get_connection
from collections import defaultdict

from pyspark.sql.functions import when, sum as spark_sum, explode, split, col, row_number, coalesce, lit
from pyspark.sql.window import Window


def aggregate_spark(df, history_df):
    print("df : ",df.columns, " history_df : ", history_df.printSchema())
    # 서로 다른 dataFrame은 동시에 쓸 수 없으므로 join
    joined_df = (
        df.alias("new")
        .join(
            history_df.alias("old"),
            (   # join 조건
                (col("new.user_id") == col("old.user_id")) &
                (col("new.movie_id") == col("old.movie_id")) &
                (col("old.logged_at") < col("new.logged_at")) &
                (col("old.log_id") < col("new.log_id"))
            ),
            "left"
        )
        .select(
            col("new.log_id").alias("log_id"),
            col("new.user_id").alias("user_id"),
            col("new.movie_id").alias("movie_id"),
            col("new.genres").alias("genres"),
            col("new.action_type").alias("action_type"),
            col("new.rating_value").alias("rating_value"),
            col("old.rating_value").alias("prev_rating"),
            col("old.log_id").alias("prev_log_id"),
            col("old.logged_at").alias("prev_logged_at")
        )
    )
    
    # 기존 입력된 값 중 최근 값 가져오기
    window = (
        Window.partitionBy("log_id")
        .orderBy(
            col("prev_logged_at").desc(),
            col("prev_log_id").desc()
        )
    )

    joined_df = (
        joined_df.withColumn(
            "rn",
            row_number().over(window)
        )
        .filter(col("rn") == 1)
        
    )

    # 장르가 여러개인 경우 split해서 가중치 부여  ex)액션,코미디라면 액션, 코미디 나눠서 부여
    explode_df = (
        joined_df.withColumn(
            "genre_name",
            explode(split(col("genres"),"\\|"))
        )
    )
    return (
        explode_df
        .withColumn(
            "score",
            when(col("action_type") == "LIKE", 5)
            .when(col("action_type") == "RATING", (col("rating_value") - coalesce(col("prev_rating"), lit(0))) * 3)
            .otherwise(1)
        ).groupBy(
            "user_id",
            "genre_name"
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