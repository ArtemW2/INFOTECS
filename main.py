from contextlib import asynccontextmanager

import aiohttp
import uvicorn
from fastapi import FastAPI

from src.api.city import city_router
from src.api.weather import weather_router
from src.dependencies import SessionLocal
from src.background_tasks import WeatherCacheService


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


async def main() -> None:
    pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_level="info")
