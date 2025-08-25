from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class OccupancyEvent(BaseModel):
	people_in: int = Field(0, ge=0)
	people_out: int = Field(0, ge=0)
	timestamp: Optional[datetime] = None


class LocationUpdate(BaseModel):
	latitude: float
	longitude: float
	stop_id: Optional[int] = None
	timestamp: Optional[datetime] = None


class BusAvailability(BaseModel):
	bus_id: int
	registration_number: str
	route_name: str
	seats_available: int
	standing_available: int
	is_full: bool
	last_latitude: Optional[float] = None
	last_longitude: Optional[float] = None
	last_stop_name: Optional[str] = None


class BusStatus(BaseModel):
	bus_id: int
	registration_number: str
	route_name: str
	capacity_seated: int
	capacity_standing: int
	seats_occupied: int
	standing_occupied: int
	seats_available: int
	standing_available: int
	is_full: bool
	last_latitude: Optional[float] = None
	last_longitude: Optional[float] = None
	last_stop_name: Optional[str] = None
	last_reported_at: Optional[datetime] = None


class SearchQuery(BaseModel):
	from_stop: str
	to_stop: str
