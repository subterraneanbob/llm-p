from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.core.errors import UnauthorizedError, UserConflictError, UserNotFound
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase


router = APIRouter(prefix="/auth")


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest, auth: AuthUseCase = Depends(get_auth_usecase)
):
    try:
        return await auth.register(data.email, data.password)
    except UserConflictError as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(ex)
        ) from ex


@router.post("/login", response_model=TokenResponse)
async def login(
    data: OAuth2PasswordRequestForm = Depends(),
    auth: AuthUseCase = Depends(get_auth_usecase),
):
    try:
        token = await auth.login(data.username, data.password)
        return TokenResponse(access_token=token)
    except UnauthorizedError as ex:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(ex),
            headers={"WWW-Authenticate": "Bearer"},
        ) from ex


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: int = Depends(get_current_user_id),
    auth: AuthUseCase = Depends(get_auth_usecase),
):
    try:
        return await auth.get_user_profile(user_id)
    except UserNotFound as ex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ex),
        ) from ex
