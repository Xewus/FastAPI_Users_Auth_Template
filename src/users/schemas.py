import base64
from pathlib import Path

from pydantic import BaseModel, Field, PositiveInt, root_validator

from src.config import AVATAR_SIZES

MIN_AVATAR = str(min(AVATAR_SIZES)[0])


class TokenSchema(BaseModel):
    access_token: str = Field(
        description='JWT token'
    )
    token_type: str = 'bearer'


class TokenDataSchema(BaseModel):
    phone: str


class BaseUserSchema(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=16,
    )
    phone: int = Field(
        title='User`s phone number',
        ge=7_900_000_0000,
        le=7_999_999_9999,
    )


class CreateUserSchema(BaseUserSchema):
    password: str
    avatar: bytes | None = Field(
        default=None,
        title='Image as base64',
    )


class ResponseUserSchema(BaseUserSchema):
    is_active: bool = False
    avatars_dir: str | None = Field(
        default=None,
        title='Directory with avatars',
    )
    avatar: bytes | None = None

    class Config:
        orm_mode = True

    @root_validator
    def get_min_avatar(cls, values: dict) -> dict:
        if values['avatars_dir'] is None:
            return values

        avatar = Path(
            ''.join((values['avatars_dir'], '/', MIN_AVATAR, '.png'))
        )
        if avatar.exists():
            values['avatar'] = base64.b64encode(avatar.read_bytes())
        values['avatars_dir'] = None
        return values


class DbUserSchema(BaseUserSchema):
    id: PositiveInt | None = None
    is_active: bool = False
    password: str
    avatars_dir: str | None = Field(
        default=None,
        title='Directory with avatars',
    )

    class Config:
        orm_mode = True


class UpdateUserSchema(BaseModel):
    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=16,
    )
    phone: int | None = Field(
        default=None,
        title='User`s phone number',
        ge=7_900_000_0000,
        le=7_999_999_9999,
    )
    password: str | None = None
    avatars_dir: str | None = Field(
        default=None,
        title='Directory with avatars',
    )
    avatar: bytes | str | None = Field(
        default=None,
        title='Image as base64',
    )
