import asyncio
from typing import Any

import aiohttp
import logging
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log
) 

from src.exceptions.weather import (
    WeatherAPIConnectionError,
    WeatherAPIError,
    WeatherAPITimeoutError,
    WeatherServiceError,
)
from src.logging import get_logger
logger = get_logger(__name__)


class FetchWeatherData:
    URL = "https://api.open-meteo.com/v1/forecast"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (aiohttp.ClientConnectionError, asyncio.TimeoutError)
        ),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )
    async def fetch_data(self, session: aiohttp.ClientSession, params: dict) -> dict:
        async with session.get(
            self.URL, params=params, timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
            logger.info(f"Статус запроса к API Open Meteo: {response.status}")

            data = await response.json()
        
            return data

    async def __call__(
        self, latitude: float, longitude: float, session: aiohttp.ClientSession
    ):
        params: dict[str, Any] = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": "true",
            "hourly": "temperature_2m,pressure_msl,precipitation,relative_humidity_2m,wind_speed_10m,wind_direction_10m",
            "forecast_days": "1",
            "timezone": "auto",
        }
        try:
            logger.info(
                f"Запрос погоды по координатам: latitude={latitude}, longitude={longitude}"
            )
            data = await self.fetch_data(session, params)

            logger.info(
                f"Данные по координатам latitude={latitude}, longitude={longitude} получены"
            )

            return data
        
        except aiohttp.ClientResponseError as e:
            logger.error(
                f"Ошибка при поиске данных для координат latitude={latitude}, longitude={longitude}: {e.status} {e.message}"
            )
            raise WeatherAPIError(e.status, e.message)

        except aiohttp.ClientConnectionError as e:
            logger.error(f"Ошибка подключения к API: {e}")
            raise WeatherAPIConnectionError(str(e))

        except asyncio.TimeoutError as e:
            logger.error(
                f"Таймаут запроса к Open-Meteo: {e} для lat={latitude}, lon={longitude}"
            )
            raise WeatherAPITimeoutError()

        except Exception as e:
            logger.error(
                f"Ошибка при получении данных о погоде по координатам: {e}",
                exc_info=True,
            )
            raise WeatherServiceError(str(e))
