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
from src.enums import WeatherFilters
from src.mappers.weather import WeatherMapper
from src.schemas.responses.weather import (
    WeatherDataResponse,
    WeatherWithFiltersResponse,
)
from src.use_cases.current_weather import CurrentCityWeather
from src.use_cases.weather_by_city_name import CityWithWeather

weather_router = APIRouter(prefix="/weather", tags=["Weather"])


@weather_router.get(
    "/current",
    name="Сведения о погоде на момент запроса",
    description="Возвращает данные о погоде по введённым пользователем координатам. Город, находящийся по этим координатам в БД не вносится, данные не сохраняются!",
)
async def collect_weather_by_coordinates(
    latitude: float = Query(ge=-90, le=90, description="Ширина"),
    longitude: float = Query(ge=-180, le=180, description="Долгота"),
    mapper: WeatherMapper = Depends(get_weather_mapper),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
) -> WeatherDataResponse:
    use_case = CurrentCityWeather(mapper)

    return await use_case(latitude, longitude, http_session)


@weather_router.get(
    "/",
    name="Сведения о погоде в конкретном городе в конкретный час (Регистр не учитывается)",
    description="Поиск данных начинается с собственной БД, если города или данных обнаружено не будет, производится запрос к API, полученные данные сохраняются.",
)
async def collect_weather_by_city_name(
    city_name: str,
    hour: int = Query(ge=0, le=23, description="Час дня(0-23) в искомом городе"),
    weather_repo: WeatherRepository = Depends(get_weather_repo),
    city_repo: CityRepository = Depends(get_city_repo),
    weather_mapper: WeatherMapper = Depends(get_weather_mapper),
    http_session: aiohttp.ClientSession = Depends(get_http_session),
    filters: list[WeatherFilters] | None = Query(
        default=None,
        title="Фильтры погоды",
        description="Выберите данные для получения(Может быть пустым)",
    ),
) -> WeatherDataResponse | WeatherWithFiltersResponse:
    use_case = CityWithWeather(weather_repo, city_repo, weather_mapper)

    return await use_case(city_name, hour, http_session, filters)
