from typing import Sequence, Type, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute

from src.database.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    """
    Base class for CRUD operations: create, read, update, delete.
    It's meant to be extended by specific model CRUD classes,
    providing basic CRUD operations for a given SQLAlchemy model.
    """

    def __init__(self, model: Type[ModelType]) -> None:
        """
        Initialize the CRUDBase class with the model type.
        Args:
            model (Type[ModelType]): SQLAlchemy model class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: int | UUID) -> ModelType | None:
        """
        Get a specific record by id.
        Args:
            db (AsyncSession): Database session
            id (int): Id of the record to fetch
        Returns:
            Instance of the ModelType if found, else None
        """
        return await db.get(self.model, id)

    async def get_by_filters(
        self,
        db: AsyncSession,
        filters: list[InstrumentedAttribute],
    ) -> ModelType | None:
        """
        Get a specific record by filters.
        Args:
            db (AsyncSession): Database session
            filters (list[InstrumentedAttribute]): List of filters to apply
        Returns:
            Instance of the ModelType if found, else None
        """
        query = select(self.model).where(*filters)
        result = await db.execute(query)

        return result.scalar_one_or_none()

    async def filter(
        self,
        db: AsyncSession,
        *,
        order_on: list[InstrumentedAttribute] | None = None,
        offset: int = 0,
        limit: int = 10,
        filters: list[InstrumentedAttribute] | None = None,
    ) -> Sequence[ModelType]:
        """
        Get multiple records from the database based on the provided filters and
        pagination parameters.
        Args:
            db (AsyncSession): Database session
            order_on (list[InstrumentedAttribute] | None, optional): Ordering of records. Defaults to None.
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to retrieve. Defaults to 10.
            filters (list[InstrumentedAttribute] | None, optional): Filters to apply. Defaults to None.
        Returns:
            Sequence[ModelType]: List of instances of the ModelType
        """
        if order_on is None:
            # Default ordering by model's ID
            order_on = [self.model.id]
        query = select(self.model)
        if filters:
            query = query.where(*filters)
        query = query.order_by(*order_on).offset(offset).limit(limit)
        items = await db.scalars(query)
        return items.all()

    async def count(
        self,
        db: AsyncSession,
        *,
        filters: list[InstrumentedAttribute] | None = None,
    ) -> int:
        """
        Count the number of records in the database based on the provided filters.

        Args:
            db (AsyncSession): Database session.
            filters (list[InstrumentedAttribute] | None, optional): Filters to apply. Defaults to None.

        Returns:
            int: Count of records.
        """
        query = select(func.count()).select_from(self.model)
        if filters:
            query = query.where(*filters)
        result = await db.execute(query)
        return result.scalar()

    async def create_obj(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """
        Create a new record with provided object.
        Args:
            db (AsyncSession): Database session
            obj (ModelType): Instance of the ModelType
        Returns:
            ModelType: Instance of the ModelType for the created record
        """
        db.add(obj)
        return obj

    async def update_obj(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """
        Update the record with provided object.
        Args:
            db (AsyncSession): Database session
            obj (ModelType): Instance of the ModelType
        Returns:
            ModelType: Instance of the ModelType for the created record
        """
        db.add(obj)
        return obj

    async def remove_obj(self, db: AsyncSession, obj: ModelType) -> ModelType:
        """
        Delete a specific record by instance.
        Args:
            db (AsyncSession): Database session
            obj (ModelType): Instance of the ModelType
        Returns:
            ModelType: Instance of the ModelType for the deleted record if found, else None
        """
        await db.delete(obj)
        return obj
