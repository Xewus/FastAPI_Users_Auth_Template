from pydantic import BaseModel, Field, PositiveInt, validator


class TokenScheme(BaseModel):
    """Scheme for `Bearer Token`
    """
    access_token: str = Field(
        description='JWT token',
    )
    token_type: str = 'bearer'


class PhoneScheme(BaseModel):
    """Scheme for phone number
    """
    phone: int = Field(
        title='User`s phone number',
        description='Restrictions set for Russian mobile phone numbers.',
        example=79220001133,
        ge=7_900_000_0000,
        le=7_999_999_9999,
    )


class BaseUserScheme(PhoneScheme):
    username: str = Field(
        title='User`s username',
        example='Xewus',
        min_length=3,
        max_length=16,
    )


class CreateUserScheme(BaseUserScheme):
    """Scheme for user creation
    """
    password: str = Field(
        title='Password for authorization',
        description='NIST recommends using a password of at least 8 '
        'characters in length. Non-letter characters are not important.',
        example='qwe7RTY8asd',
        min_length=8,
        max_length=64,
    )
    avatar: bytes | None = Field(
        default=None,
        title='Image as base64',
        description='The first base64 must be a multiple of 4.',
    )

    @validator('password')
    def simple_password_validator(cls, password: str) -> str:
        if len(set(password)) < len(password) >> 1:
            raise ValueError('Password is too simple')
        return password

    @validator('avatar')
    def avatar_validator(cls, avatar: bytes | None) -> bytes | None:
        if avatar and len(avatar) != len(avatar) >> 2 << 2:
            raise ValueError('Avatar is invalid')
        return avatar


class ResponseUserScheme(BaseUserScheme):
    """Scheme for data of user for issuing to the outside
    """
    is_active: bool = Field(
        title='User is active',
        description='Inactive user does not have authorization rights.',
    )
    avatar: bytes | None = Field(
        default=None,
        title='Avatar image`',
        description='`base64` image format.',
    )

    class Config:
        orm_mode = True


class DbUserScheme(BaseUserScheme):
    """Scheme for storing user data in the database
    """
    id: PositiveInt | None = Field(
        default=None,
        description='User ID in database.',
    )
    is_active: bool = Field(
        title='User is active',
        description='Inactive user does not have authorization rights.',
    )
    password: str = Field(
        description='Hashed password.',
    )
    avatars_dir: str | None = Field(
        default=None,
        title='Directory with avatars',
    )

    class Config:
        orm_mode = True


class UpdateUserScheme(BaseModel):
    """Scheme for updating user data in the database
    """
    username: str | None = Field(
        title='User`s username',
        example='Xewus',
        min_length=3,
        max_length=16,
    )
    phone: int | None = Field(
        default=None,
        title='User`s phone number',
        description='Restrictions set for Russian mobile phone numbers.',
        example=79220001133,
        ge=7_900_000_0000,
        le=7_999_999_9999,
    )
    password: str | None = Field(
        default=None,
        title='Password for authorization',
        description='NIST recommends using a password of at least 8 '
        'characters in length. Non-letter characters are not important.',
        example='qwe7RTY8asd',
        min_length=8,
        max_length=64,
    )
    avatar: bytes | None = Field(
        title='Avatar image`',
        description='`base64` image format.',
    )
