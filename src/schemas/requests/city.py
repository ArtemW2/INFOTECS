from pydantic import BaseModel, Field

class NewCityRequest(BaseModel):
    name: str
    latitude: float = Field(ge=-90, le=90, description="Широта")
    longitude: float = Field(ge=-180, le=180, description="Долгота")