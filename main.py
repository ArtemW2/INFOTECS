from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI

from src.api.city import city_router
from src.api.weather import weather_router
from src.dependencies import SessionLocal
from src.background_tasks import WeatherCacheService
from src.exceptions.city import CityNotFoundError
from src.exceptions.weather import WeatherAPIConnectionError, WeatherAPIError, WeatherAPITimeoutError, WeatherServiceError
from src.exceptions.handlers import (
    weather_api_error_handler, weather_connection_error_handler,
    weather_timeout_handler, weather_service_error_handler, city_not_found_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    http_session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))

    weather_cache = WeatherCacheService(http_session, SessionLocal)

    await weather_cache.start()
    yield

    await weather_cache.stop()
    await http_session.close()

app = FastAPI(title="Open-Meteo API", lifespan=lifespan)

app.include_router(city_router)
app.include_router(weather_router)

app.add_exception_handler(WeatherAPIError, weather_api_error_handler)
app.add_exception_handler(WeatherAPIConnectionError, weather_connection_error_handler)
app.add_exception_handler(WeatherAPITimeoutError, weather_timeout_handler)
app.add_exception_handler(WeatherServiceError, weather_service_error_handler)
app.add_exception_handler(CityNotFoundError, city_not_found_handler)

async def main() -> None:
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
