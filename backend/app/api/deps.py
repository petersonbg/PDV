from typing import AsyncGenerator, Sequence

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.session import get_session
from app.models.user import Role, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)
) -> User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await session.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions),
            selectinload(User.roles),
        )
        .where(User.email == email)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user


async def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def authorize(
    roles: Sequence[str] | None = None, permissions: Sequence[str] | None = None
):
    async def dependency(current_user: User = Depends(get_active_user)) -> User:
        if current_user.is_superuser:
            return current_user

        role_names: set[str] = {role.name for role in current_user.roles}
        permission_codes: set[str] = {
            permission.code
            for role in current_user.roles
            for permission in role.permissions
        }

        if roles and not role_names.intersection(roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Perfil insuficiente")

        if permissions and not set(permissions).issubset(permission_codes):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permissão insuficiente")

        return current_user

    return dependency
