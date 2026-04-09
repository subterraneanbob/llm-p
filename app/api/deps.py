from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.config import settings
from app.core.security import decode_token
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.repositories.chat_messages import ChatMessagesOrmRepo
from app.repositories.users import UsersOrmRepo
from app.services.openrouter_client import OpenRouterClient
from app.usecases.auth import AuthUseCase
from app.usecases.chat import ChatUseCase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@asynccontextmanager
async def lifespan(app: FastAPI):
    openrouter_client = OpenRouterClient(
        settings.openrouter_base_url,
        settings.openrouter_api_key,
        settings.openrouter_app_name,
        settings.openrouter_site_url,
    )
    app.state.openrouter_client = openrouter_client

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()
    await openrouter_client.close()


def get_openrouter_client(request: Request) -> OpenRouterClient:
    return request.app.state.openrouter_client


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


def get_users_repo(db: AsyncSession = Depends(get_db)) -> UsersOrmRepo:
    return UsersOrmRepo(db)


def get_chat_messages_repo(
    db: AsyncSession = Depends(get_db),
) -> ChatMessagesOrmRepo:
    return ChatMessagesOrmRepo(db)


def get_auth_usecase(
    users_repo: UsersOrmRepo = Depends(get_users_repo),
) -> AuthUseCase:
    return AuthUseCase(users_repo)


def get_chat_usecase(
    chat_messages_repo: ChatMessagesOrmRepo = Depends(get_chat_messages_repo),
    openrouter_client: OpenRouterClient = Depends(get_openrouter_client),
) -> ChatUseCase:
    return ChatUseCase(chat_messages_repo, openrouter_client)


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    def raise_unauthorized(detail: str, cause: Exception = None):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail, {"WWW-Authenticate": "Bearer"}
        ) from cause

    try:
        payload = decode_token(token)

        token_type = payload.get("type")
        subject = payload.get("sub")

        if token_type != "access" or not subject:
            raise_unauthorized("Invalid access token.")

        return int(subject)

    except ExpiredSignatureError as ex:
        raise_unauthorized("Access token expired.", ex)
    except (JWTError, ValueError) as ex:
        raise_unauthorized("Invalid access token.", ex)
