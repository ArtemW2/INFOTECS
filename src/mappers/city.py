from src.database.models.cities import CityModel
from src.schemas.responses.city import CityDataResponse


class CityMapper:
    def to_response_model(self, orm_model: CityModel) -> CityDataResponse:
        return CityDataResponse(
            id=orm_model.id,
            name=orm_model.name,
            latitude=orm_model.latitude,
            longitude=orm_model.longitude
        )


    def to_dto(self, model: CityModel):
        return {
            "id": model.id,
            "name": model.name,
            "latitude": model.latitude,
            "longitude": model.longitude
        }  
    