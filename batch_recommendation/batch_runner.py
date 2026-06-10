import os
from apscheduler.schedulers.blocking import BlockingScheduler

def run_batch():
    print("배치 시작 - 아직 미구현")

interval = int(os.getenv('BATCH_INTERVAL_MINUTES', 60))
scheduler = BlockingScheduler()
scheduler.add_job(run_batch, 'interval', minutes=interval)

print(f"배치 스케줄러 시작 ({interval}분 주기)")
run_batch()
scheduler.start()