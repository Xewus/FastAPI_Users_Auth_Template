from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import Base


class CRUD:
    """The set of basic `CRUD` operations.
    """
    def __init__(self, model: Base) -> None:
        self.model = model

    async def create(self, db: AsyncSession, new_obj: dict) -> None | str:
        """Create a new object in the database.

        #### Args:
          - db (AsyncSession):
            Connecting to the database.
          - new_obj (dict):
            Data to save to the database.

        #### Returns:
          - None | str:
            None if the save is successful else the error description.
        """
        db_obj = self.model(**new_obj)
        db.add(db_obj)
        try:
            await db.commit()
        except IntegrityError as err:
            return err.args[0].split('.')[-1]

    async def update(
        self, db: AsyncSession, obj_id: int, update_data: dict
    ) -> None | str:
        """Update an object in the database.

        #### Args:
          - db (AsyncSession):
            Connecting to the database.
          - obj_id (int):
            ID of the object being updated.
          - update_data (dict):
            Updated data.

        #### Returns:
          - None | str:
            None if the update is successful else the error description.
        """
        if not update_data:
            return 'No update data'

        query = update(
            self.model
        ).where(
            self.model.id == obj_id
        ).values(
            update_data
        )
        try:
            await db.execute(query)
            await db.commit()
        except IntegrityError as err:
            return err.args[0].split('.')[-1]

    async def get(self, db: AsyncSession, id: int) -> Base | None:
        """Get an object from the database by ID.

        #### Args:
          - db (AsyncSession):
            Connecting to the database.
          - id (int):
            Object ID.

        #### Returns:
          - Base | None:
            An object if it exists in the database else None.
        """
        return await db.get(self.model, id)
