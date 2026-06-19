from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Tuple

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, password: str) -> Optional[Tuple]:
        """
        새로운 유저를 DB의 users 테이블에 INSERT하고 생성된 레코드를 튜플 형태로 반환합니다.
        """
        sql = text("""
                    insert into users (username, email, password) 
                    values (:username, :email, :password) 
                    returning user_id, email, username, created_at
                   """)
        result = self.db.execute(sql,{"username":username,"email":email,"password":password})
        self.db.commit()
        row = result.fetchone()
        return dict(row._mapping) if row else None

    def get_user_by_email(self, email: str) -> Optional[Tuple]:
        """
        이메일을 기반으로 사용자를 조회하여 튜플 형태로 반환합니다.
        """
        sql = text("""select user_id, username, email, password, created_at 
                     from users
                     where email = (:email)
                  """)
        result = self.db.execute(sql,{"email":email})
        row = result.fetchone()
        return dict(row._mapping) if row else None

    def get_user_by_id(self, user_id: int) -> Optional[Tuple]:
        """
        유저 ID를 기반으로 사용자를 조회하여 튜플 형태로 반환합니다.
        """
        sql = text("""select user_id, username, email, password, created_at
                      from users
                      where user_id = (:user_id)
                    """)
        result = self.db.execute(sql,{"user_id":user_id})
        row = result.fetchone()
        return dict(row._mapping) if row else None
