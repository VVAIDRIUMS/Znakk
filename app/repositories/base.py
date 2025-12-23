from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError


from app.database.database import Base
from app.exceptions.base import ObjectAlreadyExistsError


class BaseRepository:
    model: Base = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(
        self,
        limit: int | None = None,
        offset: int | None = None,
        *filter,
        **filter_by,
    ) -> list[BaseModel]:
        filter_by = {k: v for k, v in filter_by.items() if v is not None}
        filter_ = [v for v in filter if v is not None]

        query = select(self.model).filter(*filter_).filter_by(**filter_by)

        if limit is not None and offset is not None:
            query = query.limit(limit).offset(offset)
        # print(query.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        result = [
            self.schema.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]

        return result

    async def get_all(self, *args, **kwargs) -> list[BaseModel]:
        """Возращает все записи в БД из связаной таблицы"""
        return await self.get_filtered(*args, **kwargs)

    async def get_one_or_none(self, **filter_by) -> None | BaseModel:
        query = select(self.model).filter_by(**filter_by)

        result = await self.session.execute(query)

        model = result.scalars().one_or_none()
        if model is None:
            return None
        result = self.schema.model_validate(model, from_attributes=True)
        return result

    async def add(self, data: BaseModel):
        try:
            add_stmt = (
                insert(self.model).values(**data.model_dump()).returning(self.model)
            )
            # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))

            result = await self.session.execute(add_stmt)

            model = result.scalars().one_or_none()
            if model is None:
                return None
            return self.schema.model_validate(model, from_attributes=True)

        except IntegrityError as exc:
            raise ObjectAlreadyExistsError from exc

    async def add_bulk(self, data: list[BaseModel]) -> None | BaseModel:
        """
        Метод для множественного добавления данных в таблицу
        """
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        # print(add_stmt.compile(compile_kwargs={"literal_binds": True}))
        await self.session.execute(add_stmt)

    async def delete(self, *filters, **filter_by) -> None:
        delete_stmt = delete(self.model)
        if filters:
            delete_stmt = delete_stmt.where(*filters)
        if filter_by:
            delete_stmt = delete_stmt.filter_by(**filter_by)

        await self.session.execute(delete_stmt)
        await self.session.commit()

    async def edit(
        self, data: BaseModel, exclude_unset: bool = False, **filter_by
    ) -> None:
        edit_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
        )
        await self.session.execute(edit_stmt)
