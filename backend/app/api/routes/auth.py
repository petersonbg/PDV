from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import authorize, get_db
from app.core.config import get_settings
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from app.models.user import User
from app.schemas import auth as auth_schema
from app.schemas import user as user_schema
from app.services.audit import log_action
from app.models.refresh_token import RefreshToken

router = APIRouter(prefix="/auth", tags=["auth"])


async def _issue_refresh_token(session: AsyncSession, user: User) -> str:
    settings = get_settings()
    refresh_token = generate_refresh_token()
    session.add(
        RefreshToken(
            token_hash=hash_token(refresh_token),
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
        )
    )
    await session.flush()
    return refresh_token


@router.post("/token", response_model=auth_schema.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)
):
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inativo")

    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = await _issue_refresh_token(session, user)
    await session.commit()
    await log_action(session, user, "login", "User", user.id, {"email": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=auth_schema.Token)
async def refresh_access_token(
    payload: auth_schema.RefreshRequest, session: AsyncSession = Depends(get_db)
):
    token_hash = hash_token(payload.refresh_token)
    result = await session.execute(
        select(RefreshToken)
        .options(selectinload(RefreshToken.user).selectinload(User.roles))
        .where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()
    if not stored or stored.revoked or stored.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token inválido")

    user = stored.user
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário inválido")

    stored.revoked = True
    access_token = create_access_token({"sub": user.email})
    new_refresh_token = await _issue_refresh_token(session, user)
    await session.commit()
    await log_action(session, user, "refresh_token", "User", user.id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/usuarios", response_model=user_schema.User, status_code=status.HTTP_201_CREATED)
async def criar_usuario(
    payload: user_schema.UserCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(roles=["GERENTE"])),
):
    existing = await session.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    await log_action(session, current_user, "create_user", "User", user.id, {"email": user.email})
    return user
