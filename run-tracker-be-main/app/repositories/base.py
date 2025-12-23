from datetime import datetime
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    async def create_one(self, data: dict) -> ModelType:
        row: ModelType = self.model(**data)
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def create_many(self, data: list[dict]) -> None:
        query = pg_insert(self.model).values(data).on_conflict_do_nothing()
        await self.session.execute(query)
        await self.session.commit()

    async def get_one(
        self,
        filters: list | None = None,
        options: list | None = None,
        **params: Any,
    ) -> ModelType:
        query = select(self.model).filter_by(**params)
        if filters:
            for condition in filters:
                query = query.filter(condition)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        db_row = result.scalar_one_or_none()
        return db_row

    async def get_many(
        self,
        page: int = 1,
        limit: int = 10,
        filters: list | None = None,
        options: list | None = None,
        order_by: list | None = None,
        **params: Any,
    ) -> tuple[list[ModelType], int]:
        offset = (page - 1) * limit

        # Base query with filter_by for simple equality filters
        query = select(self.model).filter_by(**params).offset(offset).limit(limit)
        total_query = select(func.count()).select_from(self.model).filter_by(**params)

        # Apply advanced filters
        if filters:
            for condition in filters:
                query = query.filter(condition)
                total_query = total_query.filter(condition)
        if order_by:
            query = query.order_by(*order_by)

        if options:
            query = query.options(*options)

        result = await self.session.execute(query)
        total = await self.session.execute(total_query)
        db_rows = result.scalars().all()
        return db_rows, total.scalar()

    async def list_all_by_ids(self, uuids: list[UUID]) -> list[ModelType]:
        if not uuids:
            return []

        query = select(self.model).where(self.model.uuid.in_(uuids))
        result = await self.session.execute(query)
        db_rows = result.scalars().all()
        return db_rows

    async def get_all(
        self,
        filters: list | None = None,
        order_by: list | None = None,
        **params: Any,
    ) -> list[ModelType]:
        query = select(self.model).filter_by(**params)

        if filters:
            for condition in filters:
                query = query.filter(condition)

        if order_by:
            query = query.order_by(*order_by)

        result = await self.session.execute(query)
        db_rows = result.scalars().all()
        return db_rows

    async def update_one(self, uuid_: UUID, data: dict) -> ModelType:
        query = select(self.model).where(self.model.uuid == uuid_)
        data["updated_at"] = datetime.now()
        result = await self.session.execute(query)
        obj = result.scalar_one()
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_one_by_id(self, id_: int, data: dict) -> ModelType:
        query = select(self.model).where(self.model.id == id_)
        data["updated_at"] = datetime.now()
        result = await self.session.execute(query)
        obj = result.scalar_one()
        for key, value in data.items():
            setattr(obj, key, value)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def delete_one(self, uuid_: UUID) -> ModelType:
        query = delete(self.model).where(self.model.uuid == uuid_).returning(self.model)
        res = await self.session.execute(query)
        await self.session.commit()
        return res.scalar_one()

    async def delete_many(self, filters: list | None = None, **params: Any) -> None:
        query = delete(self.model).filter_by(**params)
        if filters:
            for condition in filters:
                query = query.filter(condition)
        await self.session.execute(query)
