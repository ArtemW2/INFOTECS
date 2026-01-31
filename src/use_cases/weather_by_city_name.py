import aiohttp

from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.enums import WeatherFilters
from src.mappers.weather import WeatherMapper
from src.schemas.responses.weather import (
    WeatherDataResponse,
    WeatherWithFiltersResponse,
)
from src.use_cases.city_service import CityService


class CityWithWeather:
    def __init__(
        self,
        weather_repo: WeatherRepository,
        city_repo: CityRepository,
        mapper: WeatherMapper,
    ) -> None:
        self.city_repo: CityRepository = city_repo
        self.weather_repo: WeatherRepository = weather_repo
        self.mapper: WeatherMapper = mapper

    async def __call__(
        self,
        city_name: str,
        timestamp: int,
        session: aiohttp.ClientSession,
        filters: list[WeatherFilters] | None = None,
    ) -> WeatherDataResponse | WeatherWithFiltersResponse:
        _, weather_data = await CityService(self.weather_repo, self.city_repo)(
            city_name, session
        )

        if filters is None:
            return self.mapper.to_response_model(weather_data, timestamp)

        return self.mapper.to_optional_response_model(weather_data, timestamp, filters)