from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas import auth as auth_schema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=auth_schema.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db)
):
    result = await session.execute(User.__table__.select().where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
