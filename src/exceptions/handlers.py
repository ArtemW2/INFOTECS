from fastapi import Request, status
from fastapi.responses import JSONResponse
from src.exceptions.city import CityNotFoundError
from src.exceptions.weather import WeatherAPIConnectionError, WeatherAPIError, WeatherAPITimeoutError, WeatherServiceError

async def weather_api_error_handler(request: Request, exc: WeatherAPIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

async def weather_connection_error_handler(request: Request, exc: WeatherAPIConnectionError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": exc.detail}
    )

async def weather_timeout_handler(request: Request, exc: WeatherAPITimeoutError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        content={"detail": exc.detail}
    )

async def weather_service_error_handler(request: Request, exc: WeatherServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": exc.detail}
    )

async def city_not_found_handler(request: Request, exc: CityNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": exc.args[0]}
    )