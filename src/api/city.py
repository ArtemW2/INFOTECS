from typing import Annotated

import aiohttp
from fastapi import APIRouter, Depends, Form

from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.dependencies import (
    get_city_mapper,
    get_city_repo,
    get_http_session,
    get_weather_repo,
)
from src.mappers.city import CityMapper
from src.schemas.requests.city import (
    NewCityRequest,
)
from src.schemas.responses.city import CityDataResponse
from src.use_cases.create_new_city import GetOrCreateNewCity
from src.use_cases.get_city_list import GetCityList

city_router = APIRouter(prefix="/cities", tags=["Cities"])


@city_router.get(
    "/", 
    name="Список городов",
    description="Список всех городов, хранящихся в собственной БД, для которых хранятся данные о погоде с актуальностью 15 минут"
)
async def all_cities(
    city_repo: CityRepository = Depends(get_city_repo),
    mapper: CityMapper = Depends(get_city_mapper),
) -> list[CityDataResponse]:
    return await GetCityList(city_repo, mapper)()


@city_router.post(
    "/",
    name="Добавление нового города в БД (Регистр не учитывается)",
    description="Город добавляется в БД и добавляется к списку городов, получающих актуальные данные о погоде каждые 15 минут. Сразу после добавления будут доступны данные о погоде для этого города. Если город уже есть в БД, вернутся данные о нём, данные запроса внесены в БД не будут (Проверка корректности координат для города не предусмотрено)",
)
async def add_new_city(
    data: Annotated[NewCityRequest, Form()],
    city_repo: CityRepository = Depends(get_city_repo),
    weather_repo: WeatherRepository = Depends(get_weather_repo),
    mapper: CityMapper = Depends(get_city_mapper),
    session: aiohttp.ClientSession = Depends(get_http_session),
) -> CityDataResponse:
    return await GetOrCreateNewCity(city_repo, weather_repo, mapper)(
        city_name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        session=session,
    )


@city_router.delete(
    "/{name}", 
    name="Удаление города (Регистр не учитывается)",
    description="Сервис больше не станет отслеживать данные о погоде для этого города. Все новые данные придётся получать либо по координатам, либо добавлять город в БД вновь"
)
async def delete_city(
    name: str, city_repo: CityRepository = Depends(get_city_repo)
) -> dict[str, str]:
    await city_repo.delete(name)

    return {"message": "Город удалён"}
