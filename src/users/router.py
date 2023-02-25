import base64
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import AVATAR_SIZES
from src.core.exceptions import (
    AvatarException,
    InvalidLoginDataException,
    UserExistException,
)
from src.core.services import Avatar, get_avatars_root
from src.db.database import get_db
from src.users.authentication import (
    authenticate_user,
    create_access_token,
    get_active_user,
    get_hash_password,
)
from src.users.forms import PhoneAuthForm
from src.users.models import UserTable, orm
from src.users.schemes import (
    CreateUserScheme,
    DbUserScheme,
    ResponseUserScheme,
    TokenScheme,
    UpdateUserScheme,
)

MIN_AVATAR = str(min(AVATAR_SIZES)[0])

router = APIRouter()


@router.post(
    path='/registration',
    response_model=ResponseUserScheme,
    status_code=status.HTTP_201_CREATED,
    summary='Registering a new user',
    response_model_exclude_none=True,
)
async def sign(
    new_user: CreateUserScheme,
    background_tasks: BackgroundTasks,
    avatars_dir: Path = Depends(get_avatars_root),
    db: AsyncSession = Depends(get_db),
) -> None:
    user = DbUserScheme(
        username=new_user.username,
        phone=new_user.phone,
        password=get_hash_password(new_user.password),
        is_active=True,
    )
    err = await orm.create(db, user.dict())
    if err is not None:
        raise UserExistException(detail=err)

    if new_user.avatar is not None:
        avatar: Avatar = await Avatar(
            new_user.avatar, str(user.id), avatars_dir
        )
        if avatar.image is None:
            raise AvatarException(status.HTTP_201_CREATED)

        update_data = UpdateUserScheme(avatars_dir=str(avatar.save_dir))
        background_tasks.add_task(
            orm.update, db, user.id, update_data.dict(exclude_none=True)
        )
        background_tasks.add_task(avatar.save_resized_avatars)

    user = await orm.get_user_by_phone(db, user.phone)
    response_user = ResponseUserScheme.from_orm(user)
    if user.avatars_dir is not None:
        avatar: Path = Path(
            ''.join((user.avatars_dir, '/', MIN_AVATAR, '.png'))
        )
        if avatar.exists():
            response_user.avatar = base64.b64encode(avatar.read_bytes())
    return response_user


@router.post(
    path='/token',
    response_model=TokenScheme,
    summary='Obtaining an access token'
)
async def get_access_token(
    form: PhoneAuthForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> TokenScheme:
    user = await authenticate_user(db, form.username, form.password)
    if user is None:
        raise InvalidLoginDataException

    access_token = create_access_token(data={'sub': str(user.phone)})
    return TokenScheme(access_token=access_token)


@router.get(
    path='/users/me',
    response_model=ResponseUserScheme,
    summary='Get the user who is the owner of the token',
    response_model_exclude_none=True,
)
async def read_users_me(current_user: UserTable = Depends(get_active_user)):
    return current_user


@router.patch(
    path='/users/me',
    response_model=ResponseUserScheme,
    summary='Self-update the user',
    response_model_exclude_none=True,
)
async def update_users_me(
    update_data: UpdateUserScheme,
    background_tasks: BackgroundTasks,
    current_user: UserTable = Depends(get_active_user),
    db: AsyncSession = Depends(get_db)
):
    if update_data.password:
        update_data.password = get_hash_password(update_data.password)

    new_avatar = False
    if update_data.avatar is not None:
        media_root = get_avatars_root()
        avatar = Avatar(update_data.avatar, str(current_user.id), media_root)
        if avatar.image is None:
            raise AvatarException

        update_data.avatars_dir = str(avatar.save_dir)
        update_data.avatar = None
        new_avatar = True

    db.expunge(current_user)
    err = await orm.update(
        db, current_user.id, update_data.dict(exclude_none=True)
    )
    if err is not None:
        raise UserExistException(detail=err)

    if new_avatar:
        background_tasks.add_task(avatar.save_resized_avatars)
    return await orm.get(db, current_user.id)
