from time import sleep
from realtime_log.repository.offset_repo import get_last_offset, update_offset, get_current_max_id, load_logs_spark, load_rating_history_spark
from realtime_log.repository.weight_repo import aggregate_spark, upsert_weights
from pyspark.sql import SparkSession
from pyspark.sql.functions import col

spark = (
        SparkSession.builder \
        .appName("PopcornPick") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.shuffle.partitions", "4") \
        .getOrCreate()
    )


while True:
    try:
        last_offset = get_last_offset()

        max_log_id = get_current_max_id()

        if max_log_id <= last_offset:
            print("no new logs")
            sleep(20)
            continue
        
        #새로 입력된 데이터 있는지 확인
        df = load_logs_spark(spark, last_offset, max_log_id)

        if df.rdd.isEmpty():
            print("no new logs")
            sleep(20)
            continue

        #기존 입력된 별점여부 확인
        targets = (
            df.select("user_id", "movie_id")
            .distinct()
        )
        history_df = (
            #spark.read.table("user_click_logs")
            load_rating_history_spark(spark)
            #.filter(col("action_type") == "RATING")
            .join(
                targets,
                ["user_id", "movie_id"],
                "inner"
            )
        )            

        #가중치 부여
        result_df = aggregate_spark(df, history_df)

        upsert_weights(result_df)
        
        update_offset(max_log_id)
        
        print(f"processed {max_log_id} logs")

    except Exception as e:
        print(f"[STREAM ERROR] : {e}")
    
    sleep(20)
