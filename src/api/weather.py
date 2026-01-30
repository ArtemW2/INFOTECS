import aiohttp
from fastapi import APIRouter, Depends, Query

from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.dependencies import (
    get_city_repo,
    get_http_session,
    get_weather_mapper,
    get_weather_repo,
)
from src.mappers.weather import WeatherMapper
from src.schemas.responses.weather import WeatherDataResponse, WeatherWithFiltersResponse
from src.enums import WeatherFilters
from src.use_cases import CurrentCityWeather, CityWithWeather

weather_router = APIRouter(prefix="/weather")



@weather_router.get("/current")
async def collect_weather_by_coordinates(
    latitude: float = Query(ge=-90, le=90, description="Ширина"),
    longitude: float = Query(ge=-180, le=180, description="Долгота"),
    mapper: WeatherMapper = Depends(get_weather_mapper),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
) -> WeatherDataResponse:
    use_case = CurrentCityWeather(mapper)

    return await use_case(latitude, longitude, http_session)


@weather_router.get("/")
async def collect_weather_by_city_name(
    city_name: str,
    hour: int = Query(ge=0, le=23, description="Час дня(0-23)"),
    weather_repo: WeatherRepository = Depends(get_weather_repo),
    city_repo: CityRepository = Depends(get_city_repo),
    weather_mapper: WeatherMapper = Depends(get_weather_mapper),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
    filters: list[WeatherFilters] | None = Query(
        default=None,
        title="Фильтры погоды",
        description="Выберите данные для получения(Может быть пустым)"
    ),
) -> WeatherDataResponse | WeatherWithFiltersResponse:
    use_case = CityWithWeather(weather_repo, city_repo, weather_mapper)

    return await use_case(city_name, hour, http_session, filters)