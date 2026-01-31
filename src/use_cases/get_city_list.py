from typing import Any
from src.schemas.responses.city import CityDataResponse
from src.database.repositories.cities import CityRepository
from src.mappers.city import CityMapper

class GetCityList:
    def __init__(self, city_repo: CityRepository, mapper: CityMapper) -> None:
        self.repo: CityRepository = city_repo
        self.mapper: CityMapper = mapper

    async def __call__(self, ) -> list[CityDataResponse]:
        cities: list[dict[str, Any]] = await self.repo.all()

        return [self.mapper.to_response_model(city) for city in cities]