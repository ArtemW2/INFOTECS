import asyncio
import logging

import aiohttp
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from src.exceptions.weather import (
    WeatherAPIConnectionError,
    WeatherAPIError,
    WeatherAPITimeoutError,
    WeatherServiceError,
)
from src.logging import get_logger

logger: logging.Logger = get_logger(__name__)


class FetchCityCoordinates:
    GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (aiohttp.ClientConnectionError, asyncio.TimeoutError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    async def fetch_coordinates(self, session: aiohttp.ClientSession, params: dict):
        async with session.get(self.GEO_URL, params=params) as response:
            return await response.json()

    async def __call__(
        self, city_name: str, session: aiohttp.ClientSession
    ) -> dict[str, float]:
        params = {"name": city_name, "count": 1, "language": "ru"}
        try:
            logger.info(f"Запрос координат города {city_name} по GEO_URL")
            data = await self.fetch_coordinates(session, params)

            latitude = data["results"][0]["latitude"]
            longitude = data["results"][0]["longitude"]

            logger.info(
                f"Координаты города {city_name} успешно извлечены из полученных API-данных"
            )

            city_coordinates: dict[str, float] = {
                "latitude": latitude,
                "longitude": longitude,
            }

            return city_coordinates
        except aiohttp.ClientConnectionError as e:
            logger.error(
                f"Ошибка при попытке установки соединения с API для получения координат города {city_name}: {e}"
            )
            raise WeatherAPIConnectionError(str(e))
        except aiohttp.ClientResponseError as e:
            logger.error(
                f"Ошибка при получении данных от API с координатами города {city_name}: {e}"
            )
            raise WeatherAPIError(e.status, e.message)
        except asyncio.TimeoutError as e:
            logger.error(f"Таймаут запроса к API для города {city_name}: {e} ")
            raise WeatherAPITimeoutError()
        except Exception as e:
            logger.error(
                f"Ошибка при получении данных для города {city_name}: {e}",
                exc_info=True,
            )
            raise WeatherServiceError(str(e))
