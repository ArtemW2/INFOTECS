import asyncio

import aiohttp

from src.logging import logger
from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.mappers.city import CityMapper
from src.mappers.weather import WeatherMapper
from src.use_cases import CityWeather


class WeatherCacheService:
    def __init__(self, http_session: aiohttp.ClientSession, db_session_factory):
        self.http_session: aiohttp.ClientSession = http_session
        self.SessionLocal = db_session_factory
        self.city_mapper = CityMapper()
        self.weather_mapper = WeatherMapper()
        self.city_weather = CityWeather()

    async def start(self):
        self.task = asyncio.create_task(self._update_loop())
        logger.info("WeatherCacheService запущен")

    async def stop(self):
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            logger.info("WeatherCacheService остановлен")

    async def _update_loop(self):
        while True:
            try:
                await self._update_all_cities()
            except Exception as e:
                logger.error(f"Ошибка обновления кэша: {e}")

            await asyncio.sleep(900)

    async def _update_all_cities(self):
        async with self.SessionLocal() as db_session:
            city_repo = CityRepository(db_session, self.city_mapper)
            weather_repo = WeatherRepository(db_session, self.weather_mapper)

            cities = await city_repo.list()
            logger.info(f"Обновление данных о погоде для {len(cities)} городов")

            weather_datas = await asyncio.gather(
                *[
                    self.city_weather(city.latitude, city.longitude, self.http_session)
                    for city in cities
                ],
                return_exceptions=True,
            )

            updated = 0
            for city, weather_data in zip(cities, weather_datas):
                if not isinstance(weather_data, Exception):
                    await weather_repo.update(city.id, weather_data)
                    updated += 1

            logger.info(f"Обновлено {updated}/{len(cities)} городов")
            await db_session.commit()
