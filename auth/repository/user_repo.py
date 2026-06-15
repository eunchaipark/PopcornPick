from typing import Optional, Tuple
from db import get_connection

def create_user(username: str, email: str, password_hash: str) -> Optional[Tuple]:
    """
    새로운 유저를 DB의 users 테이블에 INSERT하고 생성된 레코드를 튜플 형태로 반환합니다.
    """
    # TODO: 데이터베이스 연결(get_connection)을 사용하여 안전한 INSERT 쿼리를 실행하세요.
    pass

def get_user_by_email(email: str) -> Optional[Tuple]:
    """
    이메일을 기반으로 사용자를 조회하여 튜플 형태로 반환합니다.
    """
    # TODO: 데이터베이스 연결(get_connection)을 사용하여 SELECT 쿼리를 실행하세요.
    pass

def get_user_by_id(user_id: int) -> Optional[Tuple]:
    """
    유저 ID를 기반으로 사용자를 조회하여 튜플 형태로 반환합니다.
    """
    # TODO: 데이터베이스 연결(get_connection)을 사용하여 SELECT 쿼리를 실행하세요.
    pass
