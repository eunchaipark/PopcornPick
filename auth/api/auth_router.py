from fastapi import APIRouter, HTTPException, status
from auth.schema.user import UserRegisterRequest, UserRegisterResponse, UserLoginRequest, TokenResponse
from auth.service import auth_service

router = APIRouter()

@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegisterRequest):
    """
    신규 사용자 등록(회원가입) API 엔드포인트입니다.
    """
    # TODO: auth_service.register_user 함수를 호출하여 회원가입을 완료하고 결과를 반환하세요.
    pass

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest):
    """
    사용자 로그인 및 JWT 발급 API 엔드포인트입니다.
    """
    # TODO: auth_service.authenticate_user 함수를 호출하여 JWT를 발급받고 TokenResponse 형태로 반환하세요.
    pass
