from typing import Any, AsyncGenerator

import aiohttp
from fastapi import Depends
from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.database.session import create_db_engine, get_session_factory
from src.mappers.city import CityMapper
from src.mappers.weather import WeatherMapper

engine: Engine = create_db_engine()
SessionLocal: Session = get_session_factory(engine)


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_http_session() -> AsyncGenerator[aiohttp.ClientSession, Any]:
    async with aiohttp.ClientSession() as session:
        yield session


def get_weather_mapper() -> WeatherMapper:
    return WeatherMapper()


def get_city_mapper() -> CityMapper:
    return CityMapper()


def get_city_repo(
    session: Session = Depends(get_db_session), mapper=Depends(get_city_mapper)
) -> CityRepository:
    return CityRepository(session, mapper)


def get_weather_repo(
    session: Session = Depends(get_db_session), mapper=Depends(get_weather_mapper)
) -> WeatherRepository:
    return WeatherRepository(session, mapper)
