from pydantic import BaseModel, ConfigDict


class WeatherDataResponse(BaseModel):
    temperature: float
    wind_speed: float
    pressure_msl: float

    model_config = ConfigDict(from_attributes=True)


class WeatherWithFiltersResponse(BaseModel):
    temperature: float | None = None
    wind_speed: float | None = None
    pressure_msl: float | None = None
    humidity: float | None = None
    precipitation: float | None = None
