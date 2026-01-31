from typing import Any

import aiohttp

from src.schemas.responses.city import CityDataResponse
from src.database.repositories.cities import CityRepository
from src.database.repositories.weather_data import WeatherRepository
from src.use_cases.city_service import CityService
from src.mappers.city import CityMapper

class GetOrCreateNewCity:
    def __init__(
        self, city_repo: CityRepository, weather_repo: WeatherRepository, mapper: CityMapper
    ) -> None:
        self.city_repo: CityRepository = city_repo
        self.weather_repo: WeatherRepository = weather_repo
        self.mapper: CityMapper = mapper

    async def __call__(
        self,
        city_name: str,
        latitude: float,
        longitude: float,
        session: aiohttp.ClientSession,
    )  -> CityDataResponse:
        city, _ = await CityService(self.weather_repo, self.city_repo)(
            city_name, session, latitude=latitude, longitude=longitude
        )

        return self.mapper.to_response_model(city)
