from src.database.models.cities import CityModel
from src.schemas.responses.city import CityDataResponse
from typing import Any

class CityMapper:
    def to_response_model(self, dto: dict[str, Any]) -> CityDataResponse:
        return CityDataResponse(
            id=dto["id"],
            name=dto["name"],
            latitude=dto["latitude"],
            longitude=dto["longitude"]
        )


    def to_dto(self, model: CityModel) -> dict[str, Any]:
        return {
            "id": model.id,
            "name": model.name,
            "latitude": model.latitude,
            "longitude": model.longitude
        }  
    