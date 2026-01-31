from typing import Any

from src.database.models.weather import WeatherDataModel
from src.enums import WeatherFilters
from src.schemas.responses.weather import (
    WeatherDataResponse,
    WeatherWithFiltersResponse,
)


class WeatherMapper:
    FILTERS_MAPPING: dict[WeatherFilters, str] = {
        WeatherFilters.TEMPERATURE: "temperature_2m",
        WeatherFilters.WIND_SPEED: "wind_speed_10m",
        WeatherFilters.PRESSURE: "pressure_msl",
        WeatherFilters.HUMIDITY: "relative_humidity_2m",
        WeatherFilters.PRECIPITATION: "precipitation",
    }

    def to_response_model(
        self, data: dict[str, Any], timestamp: int
    ) -> WeatherDataResponse:
        return WeatherDataResponse(
            temperature=data["hourly"]["temperature_2m"][timestamp],
            wind_speed=data["hourly"]["wind_speed_10m"][timestamp],
            pressure_msl=data["hourly"]["pressure_msl"][timestamp],
        )

    def to_optional_response_model(
        self, data: dict[str, Any], timestamp: int, filters: list[WeatherFilters]
    ) -> WeatherWithFiltersResponse:
        result = {}

        for f in filters:
            key = self.FILTERS_MAPPING[f]
            result[f.value] = data["hourly"][key][timestamp]

        return WeatherWithFiltersResponse(**result)

    def to_dto(self, model: WeatherDataModel) -> dict[str, Any]:
        return {
            "city_id": model.city_id,
            "data": model.data,
            "updated_at": model.updated_at,
        }
