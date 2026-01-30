from enum import Enum

class WeatherFilters(Enum):
    TEMPERATURE = "temperature"
    PRECIPITATION = "precipitation"
    PRESSURE = "pressure_msl"
    WIND_SPEED = "wind_speed"
    HUMIDITY = "humidity"