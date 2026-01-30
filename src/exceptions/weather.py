class WeatherNotFoundError(Exception):
    def __init__(self):
        super().__init__(
            "Данные о погоде для выбранного города не найдены"
        )


class WeatherAPIError(Exception):
    """Ошибка при проблемах с получением данных от API"""


class WeatherAPIConnectionError(Exception):
    """Ошибка при проблемах соединения с API"""


class WeatherServiceError(Exception):
    """Ошибка при непредвиденных сбоях во время взаимодействия с API"""


class WeatherAPITimeoutError(Exception):
    """Ошибка при превышении времени ожидания ответа от API"""