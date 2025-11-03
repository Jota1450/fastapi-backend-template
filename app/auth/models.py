import uuid
from typing import Optional, TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.auth.models import Role


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = Field(default=None, max_length=255)
    avatar_url: Optional[str] = Field(default=None, max_length=500)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: Optional[str] = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: Optional[EmailStr] = Field(default=None, max_length=255)  # type: ignore
    password: Optional[str] = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Role Models
class RoleBase(SQLModel):
    name: str = Field(unique=True, index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


class RoleCreate(RoleBase):
    pass


class RoleUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)


# Link table for many-to-many relationship between User and Role
class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"
    __table_args__ = {'schema': 'users'}
    user_id: uuid.UUID = Field(
        foreign_key="users.user.id",
        primary_key=True,
        ondelete="CASCADE"
    )
    role_id: uuid.UUID = Field(
        foreign_key="users.role.id",
        primary_key=True,
        ondelete="CASCADE"
    )


# Database model for Role
class Role(RoleBase, table=True):
    __table_args__ = {'schema': 'users'}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    users: list["User"] = Relationship(back_populates="roles", link_model=UserRole)


class RolePublic(RoleBase):
    id: uuid.UUID


class RolesPublic(SQLModel):
    data: list[RolePublic]
    count: int


# Database model, database table inferred from class name
class User(UserBase, table=True):
    __table_args__ = {'schema': 'users'}
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: Optional[str] = Field(default=None)
    oauth_provider_data: Optional[str] = Field(default=None)  # JSON as text from OAuth provider
    roles: list["Role"] = Relationship(back_populates="users", link_model=UserRole)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    avatar_url: Optional[str] = None
    roles: Optional[list[RolePublic]] = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
