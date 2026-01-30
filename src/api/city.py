from typing import List, Annotated

import aiohttp
from fastapi import APIRouter, Depends, Form


from src.database.models.cities import CityModel
from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.dependencies import (
    get_city_repo,
    get_http_session,
    get_weather_repo,
    get_city_mapper
)
from src.mappers.city import CityMapper
from src.schemas.requests.city import (
    NewCityRequest,
)
from src.schemas.responses.city import CityDataResponse
from src.use_cases import CreateNewCity

city_router = APIRouter(prefix="/cities")



@city_router.get("/")
async def all_cities(
    city_repo: CityRepository = Depends(get_city_repo), mapper: CityMapper = Depends(get_city_mapper)
) -> List[CityDataResponse]:
    cities: List[CityModel] = await city_repo.list()

    return [mapper.to_response_model(city) for city in cities]


@city_router.post("/")
async def add_new_city(
    data: Annotated[NewCityRequest, Form()],
    city_repo: CityRepository = Depends(get_city_repo),
    weather_repo: WeatherRepository = Depends(get_weather_repo),
    session: aiohttp.ClientSession = Depends(get_http_session)
) -> CityDataResponse:
    return await CreateNewCity(city_repo, weather_repo)(
        city_name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        session=session
    )


 
@city_router.delete("/{name}")
async def delete_city(
    name: str, city_repo: CityRepository = Depends(get_city_repo)
) -> dict[str, str]:
    await city_repo.delete(name)

    return {"message": "Город удалён"}
