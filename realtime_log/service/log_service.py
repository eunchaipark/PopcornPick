from realtime_log.repository.log_repo import insert_log


def save_log(payload):
    print("입력정보 : ",payload)
    action_type = payload.action_type.upper()

    if action_type not in ["CLICK", "LIKE", "RATING"]:
        raise ValueError("invalid action_type")

    insert_log(payload)