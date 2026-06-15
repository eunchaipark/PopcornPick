import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from auth.repository.user_repo import create_user, get_user_by_email

# JWT 설정 환경변수 및 상수
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "popcornpick_secret_key_change_in_production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

def hash_password(password: str) -> str:
    """
    비밀번호 평문을 안전하게 해시화합니다.
    """
    # TODO: 해시 패키지(예: bcrypt)를 사용해 비밀번호를 단방향 암호화하여 반환하세요.
    pass

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시 비밀번호를 비교합니다.
    """
    # TODO: 입력 비밀번호와 DB 해시 비밀번호의 일치 여부를 검증하세요.
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token을 생성하여 반환합니다.
    """
    # TODO: PyJWT를 활용해 sub(사용자 식별정보)와 exp(만료시간)가 포함된 토큰을 인코딩하세요.
    pass

def register_user(username: str, email: str, password_raw: str) -> dict:
    """
    회원가입의 비즈니스 논리를 처리합니다.
    1. 이메일 중복 체크
    2. 비밀번호 평문 해시화
    3. 레포지토리를 통한 회원 정보 DB 영속화
    """
    # TODO: 회원가입 성공 시 생성된 회원 정보를 딕셔너리 형태로 반환하세요.
    pass

def authenticate_user(email: str, password_raw: str) -> str:
    """
    로그인(인증)의 비즈니스 논리를 처리합니다.
    1. 이메일로 사용자 조회
    2. 비밀번호 불일치 시 HTTP 401 Unauthorized 에러 발생
    3. 성공 시 JWT Access Token 발급 및 반환
    """
    # TODO: 로그인 검증 성공 시 JWT 토큰을 발급하여 문자열로 반환하세요.
    pass
