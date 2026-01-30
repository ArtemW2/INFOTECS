from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.exceptions.weather import WeatherNotFoundError
from src.database.models.weather import WeatherDataModel
from src.exceptions.repository import RepositoryError, RepositorySaveError
from src.mappers.weather import WeatherMapper


class WeatherRepository:
    def __init__(self, session: Session, mapper: WeatherMapper) -> None:
        self.session: Session = session
        self.mapper: WeatherMapper = mapper

    async def get(self, city_id: int):
        try:
            data= await self.session.execute(
                select(WeatherDataModel).where(WeatherDataModel.city_id == city_id)
            )
            data = data.scalar_one_or_none()

            if not data:
                raise WeatherNotFoundError()
            
            return self.mapper.to_dto(model=data)
        except SQLAlchemyError as e:
            raise RepositoryError(
                f"Произошла непредвиденная ошибка при попытке получения данных о погоде в городе: {e}"
            ) from e

    async def save(self, data: dict):
        try:
            stmp = WeatherDataModel(city_id=data["city_id"], data=data["data"])

            self.session.add(stmp)
            await self.session.flush()
            await self.session.refresh(stmp)

            return self.mapper.to_dto(stmp)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositorySaveError(f"Ошибка сохранения: {e}") from e
        except IntegrityError as e:
            self.session.rollback()
            raise RepositorySaveError(f"Ошибка целостности данных: {e}") from e


    async def update(self, city_id: int, data: dict) -> None:
        weather_record = await self.session.execute(
            select(WeatherDataModel).where(WeatherDataModel.city_id == city_id)
        )
        weather_record = weather_record.scalar_one_or_none()

        if not weather_record:
            raise WeatherNotFoundError()

        weather_record.data = data
        weather_record.updated_at = datetime.now()

        await self.session.flush()