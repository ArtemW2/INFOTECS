class CityNotFoundError(Exception):
    def __init__(self, city_name: str):
        super().__init__(
            f"Город '{city_name} не найден в списке доступных городов для получения данных о погоде"
        )
