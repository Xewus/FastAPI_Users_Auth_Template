from sqlalchemy import Boolean, Column, Integer, String, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud import CRUD
from src.db.database import Base


class UserTable(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True, index=True, nullable=False)
    phone = Column(Integer, unique=True, index=True, nullable=False)
    password = Column(String(128), name='password', nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    avatars_dir = Column(String(128))


class UserCRUD(CRUD):
    """The set of `CRUD` operations for model `UserTable`.
    """
    async def get(self, db: AsyncSession, id: int) -> UserTable | None:
        """Get a user by ID.

        #### Args:
          - db (AsyncSession):
            Connecting to the database.
          - id (int):
            User ID.

        #### Returns:
          - UserTable | None:
            The user object from the database if it exist else None.
        """
        return await super().get(db, id)

    async def get_user_by_phone(
        self, db: AsyncSession, phone: int
    ) -> UserTable | None:
        """Get user by phone_number.

        #### Args:
          - db (Session):
            Connecting to the database.
          - phone (int):
            User's phone number.

        #### Returns:
          - UserTable | None:
            The user object from the database if it exist else None.
        """
        return await db.scalar(
            select(self.model).where(UserTable.phone == phone).limit(1)
        )


orm = UserCRUD(UserTable)
