from datetime import datetime
from typing import Any

import aiohttp

from src.mappers.weather import WeatherMapper
from src.schemas.responses.weather import WeatherDataResponse
from src.use_cases.fetch_weather_data import FetchWeatherData


class CurrentCityWeather:
    def __init__(self, mapper: WeatherMapper) -> None:
        self.mapper: WeatherMapper = mapper

    async def __call__(
        self, latitude: float, longitude: float, session: aiohttp.ClientSession
    ) -> WeatherDataResponse:
        data: dict[str, Any] = await FetchWeatherData()(latitude, longitude, session)
        timestamp: int = datetime.now().hour
        return self.mapper.to_response_model(data, timestamp)
