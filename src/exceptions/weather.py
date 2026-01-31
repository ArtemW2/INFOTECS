from fastapi import status

from src.exceptions.http import APIException

class WeatherNotFoundError(Exception):
    def __init__(self, city_id: int):
        super().__init__(
            f"Данные о погоде не найдены для города с ID={city_id} в БД"
        )


class WeatherAPIError(APIException):
    """Ошибка при проблемах с получением данных от API"""

    def __init__(self, status_code: int, message: str):
        super().__init__(
            status_code, detail=f"API вернул ошибку {status_code}: {message}"
        )


class WeatherAPIConnectionError(APIException):
    """Ошибка при проблемах соединения с API"""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ошибка подключения к API: {message}",
        )


class WeatherServiceError(APIException):
    """Непредвиденная ошибка сервиса погоды"""

    def __init__(self, message: str) -> None:
        super().__init__(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервиса погоды: {message}",
        )


class WeatherAPITimeoutError(APIException):
    """Ошибка при превышении времени ожидания ответа от API"""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Превышено время ожидания ответа API",
        )
