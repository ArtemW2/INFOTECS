from typing import Any

import aiohttp

from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.exceptions.city import CityNotFoundError
from src.exceptions.weather import WeatherNotFoundError
from src.use_cases.fetch_coordinates import FetchCityCoordinates
from src.use_cases.fetch_weather_data import FetchWeatherData

from src.logging import get_logger
logger = get_logger(__name__)

class CityService:
    def __init__(
        self, weather_repo: WeatherRepository, city_repo: CityRepository
    ) -> None:
        self.weather_repo: WeatherRepository = weather_repo
        self.city_repo: CityRepository = city_repo

    async def __call__(
        self,
        city_name: str,
        session: aiohttp.ClientSession,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        try:
            city: dict[str, Any] = await self.city_repo._get(city_name)

            latitude, longitude = city["latitude"], city["longitude"]
            try:
                city_weather_data: dict[str, Any] = await self.weather_repo.get(
                    city["id"]
                )

                return city, city_weather_data["data"]
            except WeatherNotFoundError:
                logger.info(f"Данные о погоде для города {city_name} не найдены в БД")
                city_weather_data = await FetchWeatherData()(
                    latitude, longitude, session
                )

                await self.weather_repo.save(
                    {"city_id": city["id"], "data": city_weather_data}
                )

                return city, city_weather_data

        except CityNotFoundError:
            logger.info(f"Город {city_name} не найден в БД")
            if latitude is None or longitude is None:
                coordinates: dict[str, float] = await FetchCityCoordinates()(
                    city_name, session
                )
                latitude, longitude = coordinates["latitude"], coordinates["longitude"]

            
            new_city: dict[str, Any] = await self.city_repo.save(
                {"name": city_name, "latitude": latitude, "longitude": longitude}
            )

            city_weather_data = await FetchWeatherData()(latitude, longitude, session)
            await self.weather_repo.save(
                {"city_id": new_city["id"], "data": city_weather_data}
            )

            return new_city, city_weather_data
