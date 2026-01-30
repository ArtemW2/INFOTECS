from pydantic import BaseModel, ConfigDict

class CityDataResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)