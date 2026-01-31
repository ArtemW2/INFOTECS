from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from src.database.models.cities import CityModel
from src.exceptions.city import CityNotFoundError
from src.exceptions.repository import RepositoryError, RepositorySaveError
from src.logging import get_logger
from src.mappers.city import CityMapper

logger = get_logger(__name__)


class CityRepository:
    def __init__(self, session: Session, mapper: CityMapper) -> None:
        self.session: Session = session
        self.mapper: CityMapper = mapper

    async def all(self) -> list[dict[str, Any]]:
        logger.info("Обращение к БД для получения полного списка доступных городов")
        cities = await self.session.execute(select(CityModel))
        cities = cities.scalars().all()
        logger.info(f"Успешно извлечены данные о {len(cities)} городах")

        return [self.mapper.to_dto(city) for city in cities]

    async def _get(self, name: str) -> dict[str, Any]:
        try:
            name = name.strip().title()
            logger.info(f"Поиск города {name} в собственной БД")
            result = await self.session.execute(
                select(CityModel).where(CityModel.name == name)
            )

            city = result.scalar_one_or_none()

            if not city:
                raise CityNotFoundError(name)

            logger.info(f"Город {name} найден в собственной БД(ID={city.id})")
            return self.mapper.to_dto(city)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при поиске города {name}: {e}")
            raise RepositoryError(
                f"Произошла непредвиденная ошибка при поиске города '{name}': {e}"
            ) from e

    async def save(self, data: dict) -> dict[str, Any]:
        data["name"] = data["name"].strip().title()

        name = data["name"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        try:
            logger.info(
                f"Сохранение данных о городе {name} с координатам latitude={latitude}, longitude={longitude} в собственной БД"
            )
            city = CityModel(**data)
            self.session.add(city)
            await self.session.flush()

            await self.session.refresh(city)
            logger.info(f"Город {name} успешно сохранен в БД(ID={city.id})")
            return self.mapper.to_dto(city)
        except IntegrityError as e:
            logger.error(
                f"Ошибка согласованности данных при сохранениее данных о городе {name}: {e}"
            )
            raise RepositorySaveError(f"Ошибка целостности данных: {e}") from e
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД во время сохранения данных о городе {name}: {e}")
            raise RepositorySaveError(f"Ошибка сохранения '{name}': {e}") from e

    async def delete(self, name: str) -> None:
        try:
            name = name.strip().title()
            logger.info(f"Поиск города {name} для удаления в БД")

            result = await self.session.execute(
                select(CityModel).where(CityModel.name == name)
            )

            city = result.scalar_one_or_none()

            if not city:
                raise CityNotFoundError(name)

            logger.info(f"Город {name} найден в БД для удаления")
            await self.session.delete(city)
            logger.info(f"Город {name} удалён из БД")
        except SQLAlchemyError as e:
            raise RepositoryError(f"Ошибка удаления '{name}': {e}") from e
