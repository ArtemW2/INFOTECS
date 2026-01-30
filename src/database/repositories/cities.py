from typing import List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.database.models.cities import CityModel
from src.exceptions.city import CityNotFoundError
from src.exceptions.repository import RepositoryError, RepositorySaveError
from src.mappers.city import CityMapper


class CityRepository:
    def __init__(self, session: Session, mapper: CityMapper) -> None:
        self.session: Session = session
        self.mapper: CityMapper = mapper

    async def list(self) -> List[CityModel]:
        result = await self.session.execute(select(CityModel))

        return result.scalars().all()

    async def _get(self, name: str):
        try:
            result = await self.session.execute(
                select(CityModel).where(CityModel.name == name)
            )

            city = result.scalar_one_or_none()

            if not city:
                raise CityNotFoundError(name)

            return self.mapper.to_dto(city)
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Произошла непредвиденная ошибка при поиске города '{name}': {e}"
            ) from e

    async def save(self, data: dict) -> CityModel:
        name = data["name"]
        try:
            city = CityModel(**data)

            self.session.add(city)
            await self.session.flush()

            await self.session.refresh(city)
            return self.mapper.to_dto(city)
        except SQLAlchemyError as e:
            raise RepositorySaveError(f"Ошибка сохранения '{name}': {e}") from e
        except IntegrityError as e:
            raise RepositorySaveError(f"Ошибка целостности данных: {e}") from e

    async def delete(self, name: str):
        try:
            result = await self.session.execute(
                select(CityModel).where(CityModel.name == name)
            )

            city = result.scalar_one_or_none()
            print(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA {city}")

            await self.session.delete(city)
        except SQLAlchemyError as e:
            raise RepositoryError(f"Ошибка удаления '{name}': {e}") from e
