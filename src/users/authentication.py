from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.core.exceptions import CredentialsException, NotActiveUserException
from src.db.database import get_db
from src.users.models import UserTable, orm
from src.users.schemas import TokenDataSchema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def verify_password(password: str, hash_password: str) -> bool:
    """Check the password and hash password match.

    #### Args:
      - password (str):
        The password for verification.
      - hash_password (str):
        The password hash from the database.

    #### Returns:
      - bool:
        Does the password and hash password match.
    """
    return pwd_context.verify(secret=password, hash=hash_password)


def get_hash_password(password: str) -> str:
    """Get a hash from a password.

    #### Args:
      - password (str):
        Password for hashing.

    Returns:
      - str:
        The hash of the password.
    """
    return pwd_context.hash(secret=password)


async def authenticate_user(
    db: AsyncSession, phone: int, password: str
) -> UserTable | None:
    """Get the user from the database if the password matches.

    #### Args:
      - db (AsyncSession):
        Connecting to the database.
      - phone (int):
        Unique phone number as an identifier.
      - password (str):
        Password.

    #### Returns:
      - UserTable | None:
        The user object from the database if the password matches else None.
    """
    user = await orm.get_user_by_phone(db, phone)
    if user is not None and pwd_context.verify(password, user.password):
        return user


def create_access_token(data: dict[str, str]) -> str:
    """Create JWT token.

    #### Args:
      - data (dict[str, str]):
        Data for creating a token.

    #### Returns:
      - str: JWT token.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({'exp': expire})
    jwt_token = jwt.encode(
        claims=to_encode,
        key=settings.secret_key,
        algorithm=settings.algorithm,
    )
    return jwt_token


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserTable:
    """Get a user by token.

    #### Args:
      - db (AsyncSession):
        Connecting to the database.
      - token (str):
        JWT token.

    #### Raises:
      - CredentialsException:
        The token is invalid.

    #### Returns:
      - UserTable:
        The user object from the database.
    """
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=(settings.algorithm,)
        )
        phone = payload.get('sub')
        if phone is None:
            raise CredentialsException
        token_data = TokenDataSchema(phone=phone)
    except JWTError:
        raise CredentialsException

    user = await orm.get_user_by_phone(db, int(token_data.phone))
    if user is None:
        raise CredentialsException
    return user


async def get_active_user(
    user: UserTable = Depends(get_current_user)
) -> UserTable:
    """Get the user if it is not deactivated.

    #### Args:
      - user (UserTable):
        The user object from the database.

    #### Raises:
      - NotActiveUserException:
        The user is not active.

    #### Returns:
      - UserTable:
        The user object from the database.
    """
    if not user.is_active:
        raise NotActiveUserException
    return user
