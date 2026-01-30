from typing import Any
from datetime import datetime
from sqlalchemy import JSON, ForeignKey, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.models.base import Base


class WeatherDataModel(Base):
    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"))
    data: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

    city: Mapped["CityModel"] = relationship(back_populates="measurements")
