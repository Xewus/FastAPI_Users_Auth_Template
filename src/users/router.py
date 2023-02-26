from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

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
    db_user = DbUserScheme(
        username=new_user.username,
        phone=new_user.phone,
        password=get_hash_password(new_user.password),
        is_active=True,
    )
    user, err = await orm.create(db, db_user.dict(), refresh=True)
    if err is not None:
        raise UserExistException(detail=err)

    if new_user.avatar is not None:
        avatar = await Avatar(
            new_user.avatar, str(user.id), avatars_dir
        )
        if avatar.image is None:
            raise AvatarException(status.HTTP_206_PARTIAL_CONTENT)

        background_tasks.add_task(avatar.save_resized_avatars)

    return user


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
async def read_users_me(
    current_user: UserTable = Depends(get_active_user),
    avatars_dir: Path = Depends(get_avatars_root)
):
    user = ResponseUserScheme.from_orm(current_user)
    user.avatar = await Avatar.base64_min_avatar(
        avatars_dir, str(current_user.id)
    )
    return user


@router.patch(
    path='/users/me',
    summary='Self-update the user',
    status_code=status.HTTP_202_ACCEPTED,
)
async def update_users_me(
    update_data: UpdateUserScheme,
    background_tasks: BackgroundTasks,
    current_user: UserTable = Depends(get_active_user),
    db: AsyncSession = Depends(get_db)
):
    if update_data.password:
        update_data.password = get_hash_password(update_data.password)

    if update_data.avatar is not None:
        avatars_root = get_avatars_root()
        avatar = await Avatar(
            update_data.avatar, str(current_user.id), avatars_root
        )
        if avatar.image is None:
            raise AvatarException

        background_tasks.add_task(avatar.save_resized_avatars)

    update_dict = update_data.dict(exclude_none=True, exclude={'avatar'})
    if update_dict:
        err = await orm.update(db, current_user.id, update_dict)
        if err is not None:
            raise UserExistException(detail=err)

    return None
