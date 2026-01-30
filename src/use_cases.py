import asyncio
from datetime import datetime
from typing import Any

import aiohttp

from src.database.models.cities import CityModel
from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.exceptions.city import CityNotFoundError
from src.exceptions.weather import (
    WeatherAPIConnectionError,
    WeatherAPIError,
    WeatherAPITimeoutError,
    WeatherServiceError,
)
from src.enums import WeatherFilters
from src.mappers.weather import WeatherMapper
from src.schemas.responses.weather import WeatherDataResponse, WeatherWithFiltersResponse
from src.logging import logger


class FetchCityCoordinates:
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

    async def __call__(self, city_name: str, session: aiohttp.ClientSession):
        params = {"name": city_name, "count": 1, "language": "ru"}
        try:
            async with session.get(self.GEO_URL, params=params) as response:
                logger.info(f"Запрос координат города {city_name} по GEO_URL")

                data = await response.json()
                latitude = data["results"][0]["latitude"]
                longitude = data["results"][0]["longitude"]
                logger.info(
                    f"Координаты города {city_name} успешно извлечены из полученных API-данных"
                )

                city_coordinates = {
                    "latitude": latitude,
                    "longitude": longitude,
                }

                return city_coordinates
        except aiohttp.ClientConnectionError as e:
            logger.error(
                f"Ошибка при попытке установки соединения с API для получения координат города {city_name}: {e}"
            )
            raise WeatherAPIConnectionError(f"Ошибка подключения к API: {e}")
        except aiohttp.ClientResponseError as e:
            logger.error(
                f"Ошибка при получении данных от API с координатами города {city_name}: {e}"
            )
            raise WeatherAPIError(f"Ошибка API: {e.status}")
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут запроса к API для города {city_name}: {e} ")
            raise WeatherAPITimeoutError(
                "Превышено время ожидания ответа от сервиса погоды"
            )
        except Exception as e:
            logger.error(
                f"Ошибка при получении данных для города {city_name}: {e}",
                exc_info=True,
            )
            raise WeatherServiceError(f"Внутренняя ошибка сервиса: {e}")


class CityWeather:
    URL = "https://api.open-meteo.com/v1/forecast"

    async def __call__(
        self, latitude: float, longitude: float, session: aiohttp.ClientSession
    ):
        try:
            logger.info(
                f"Запрос погоды по координатам: latitude={latitude}, longitude={longitude}"
            )

            params: dict[str, Any] = {
                "latitude": latitude,
                "longitude": longitude,
                "current_weather": "true",
                "hourly": "temperature_2m,pressure_msl,precipitation,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
                "forecast_days": "1",
                "timezone": "auto",
            }

            async with session.get(
                self.URL, params=params, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                logger.info(f"Статус запроса к API Open Meteo: {response.status}")

                data = await response.json()
                logger.info(
                    f"Данные по координатам latitude={latitude}, longitude={longitude} получены"
                )

                return data
        except aiohttp.ClientResponseError as e:
            logger.error(
                f"Ошибка при поиске данных для координат latitude={latitude}, longitude={longitude}: {e.status} {e.message}"
            )
            raise WeatherAPIError(f"Ошибка API: {e.status}")

        except aiohttp.ClientConnectionError as e:
            logger.error(f"Ошибка подключения к API: {e}")
            raise WeatherAPIConnectionError(f"Ошибка подключения к API: {e}")

        except asyncio.TimeoutError as e:
            logger.error(
                f"Таймаут запроса к Open-Meteo: {e} для lat={latitude}, lon={longitude}"
            )
            raise WeatherAPITimeoutError(
                "Превышено время ожидания ответа от сервиса погоды"
            )

        except Exception as e:
            logger.error(
                f"Ошибка при получении данных о погоде по координатам: {e}",
                exc_info=True,
            )
            raise WeatherServiceError(f"Внутренняя ошибка сервиса: {e}")


class CurrentCityWeather:
    def __init__(self, mapper: WeatherMapper) -> None:
        self.mapper: WeatherMapper = mapper

    async def __call__(
        self, latitude: float, longitude: float, session: aiohttp.ClientSession
    ) -> WeatherDataResponse:
        data = await CityWeather()(latitude, longitude, session)
        timestamp: int = datetime.now().hour
        return self.mapper.to_response_model(data, timestamp)


class CityWithWeather:
    def __init__(
        self,
        weather_repo: WeatherRepository,
        city_repo: CityRepository,
        mapper: WeatherMapper
    ) -> None:
        self.city_repo: CityRepository = city_repo
        self.weather_repo: WeatherRepository = weather_repo
        self.mapper: WeatherMapper = mapper

    async def __call__(
        self,
        city_name: str,
        timestamp: int,
        session: aiohttp.ClientSession,
        filters: list[WeatherFilters] | None = None
    ) -> WeatherDataResponse | WeatherWithFiltersResponse:
        try:
            logger.info(f"Поиск города {city_name} в собственной БД")
            city = await self.city_repo._get(city_name)

            logger.info(f"Город {city_name} успешно найден в собственной БД")
            logger.info(
                f"Поиск данных о погоде для города {city_name} в собственной БД"
            )
            weather: dict[str, Any] = await self.weather_repo.get(city["id"])

            logger.info(f"Данные о погоде успешно извлечены для города {city_name}")

            if filters is None:
                return self.mapper.to_response_model(weather["data"], timestamp)
            
            return self.mapper.to_optional_response_model(weather['data'], timestamp, filters)
        
        except CityNotFoundError:
            logger.info(f"Город {city_name} не найден в собственной БД")
            city_info = await FetchCityCoordinates()(city_name, session)

            latitude, longitude = city_info["latitude"], city_info["longitude"]

            new_city: CityModel = await CreateNewCity(
                self.city_repo, self.weather_repo
            )(city_name, latitude, longitude, session)

            weather_data = await CityWeather()(latitude, longitude, session)

            logger.info(f"Создание записи с данными о погоде для города {city_name}")
            weather_record: dict[str, Any] = {"city_id": new_city["id"], "data": weather_data}
            new_city_weather_data: dict[str, Any] = await self.weather_repo.save(weather_record)
            logger.info("Запись успешно создана в БД")

            if filters is None:
                return self.mapper.to_response_model(weather["data"], timestamp)
            
            return self.mapper.to_optional_response_model(new_city_weather_data['data'], timestamp, filters)


class CreateNewCity:
    def __init__(self, city_repo: CityRepository, weather_repo: WeatherRepository) -> None:
        self.city_repo: CityRepository = city_repo
        self.weather_repo: WeatherRepository = weather_repo

    async def __call__(
        self, city_name: str, latitude: float, longitude: float, session: aiohttp.ClientSession
    )  -> CityModel:
        try:
            logger.info(f"Поиск города {city_name} в собственной БД")
            city = await self.city_repo._get(city_name)
            logger.info(f"Город {city_name} найден в БД")

            return city
        except CityNotFoundError:
            logger.info(f"Город {city_name} не найден в БД")
            logger.info(
                f"Создание записи о городе {city_name} с координатами latitude={latitude}, longitude={longitude} в БД"
            )
            new_city_data = {
                "name": city_name,
                "latitude": latitude,
                "longitude": longitude,
            }
            new_city: CityModel = await self.city_repo.save(new_city_data)
            logger.info("Запись успешно создана в БД")

            weather_data = await CityWeather()(latitude, longitude, session)

            logger.info(f"Создание записи с данными о погоде для города {city_name}")
            weather_record: dict[str, Any] = {"city_id": new_city["id"], "data": weather_data}
            await self.weather_repo.save(weather_record)
            logger.info("Запись успешно создана в БД")

            return new_city



