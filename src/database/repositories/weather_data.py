from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.models.weather import WeatherDataModel
from src.exceptions.repository import RepositoryError, RepositorySaveError
from src.exceptions.weather import WeatherNotFoundError
from src.mappers.weather import WeatherMapper

from src.logging import get_logger
logger = get_logger(__name__)

class WeatherRepository:
    def __init__(self, session: Session, mapper: WeatherMapper) -> None:
        self.session: Session = session
        self.mapper: WeatherMapper = mapper

    async def get(self, city_id: int) -> dict[str, Any]:
        try:
            logger.info(f"Поиск данных о погоде для города с ID={city_id} в собственной БД")
            data = await self.session.execute(
                select(WeatherDataModel).where(WeatherDataModel.city_id == city_id)
            )
            data = data.scalar_one_or_none()

            if not data:
                raise WeatherNotFoundError(city_id)

            logger.info(f"Данные о погоде для города c ID={city_id} успешно извлечены из БД")
            return self.mapper.to_dto(model=data)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД во время извлечения данных о погоде для города с ID={city_id}: {e}")
            raise RepositoryError(
                f"Произошла непредвиденная ошибка при попытке получения данных о погоде в городе: {e}"
            ) from e

    async def save(self, data: dict) -> dict[str, Any]:
        city_id = data["city_id"]
        try:
            logger.info(f"Сохранение данных о погоде для города с ID={city_id} в собственной БД")
            stmp = WeatherDataModel(city_id=data["city_id"], data=data["data"])

            self.session.add(stmp)
            await self.session.flush()
            await self.session.refresh(stmp)

            logger.info(f"Данные о погоде для города c ID={city_id} успешно добавлены")
            return self.mapper.to_dto(stmp)
        except IntegrityError as e:
            logger.info(f"Ошибка согласованности данных во время сохранения данных о погоде для города с ID={city_id}: {e}")
            self.session.rollback()
            raise RepositorySaveError(f"Ошибка целостности данных: {e}") from e
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД во время сохранения данных о погоде для города с ID={city_id}: {e}")
            self.session.rollback()
            raise RepositorySaveError(f"Ошибка сохранения: {e}") from e

    async def update(self, city_id: int, data: dict) -> None:
        weather_record = await self.session.execute(
            select(WeatherDataModel).where(WeatherDataModel.city_id == city_id)
        )
        weather_record = weather_record.scalar_one_or_none()

        if not weather_record:
            raise WeatherNotFoundError(city_id)

        weather_record.data = data
        weather_record.updated_at = datetime.now()

        await self.session.flush()
