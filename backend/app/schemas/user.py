from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr


class PermissionBase(BaseModel):
    code: str
    description: Optional[str] = None


class Permission(PermissionBase):
    id: int

    class Config:
        orm_mode = True


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class Role(RoleBase):
    id: int
    permissions: List[Permission] = []

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[Role] = []

    class Config:
        orm_mode = True
