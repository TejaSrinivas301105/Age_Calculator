from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Bus
from ..schemas import LocationUpdate, OccupancyEvent


router = APIRouter(prefix="/device", tags=["device"])


def get_bus_by_device_key(
	x_device_key: str | None = Header(default=None, alias="X-Device-Key"),
	db: Session = Depends(get_db),
):
	if not x_device_key:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing X-Device-Key header")
	bus: Bus | None = db.query(Bus).filter(Bus.device_api_key == x_device_key).first()
	if bus is None:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid device key")
	return bus


@router.post("/occupancy")
def post_occupancy(
	event: OccupancyEvent,
	bus: Bus = Depends(get_bus_by_device_key),
	db: Session = Depends(get_db),
):
	# Update occupancy based on in/out deltas
	new_total = max(0, bus.seats_occupied + bus.standing_occupied + event.people_in - event.people_out)

	# First fill seats, then standing
	seats_to_fill = min(new_total, bus.capacity_seated)
	standing_to_fill = max(0, min(new_total - seats_to_fill, bus.capacity_standing))

	bus.seats_occupied = seats_to_fill
	bus.standing_occupied = standing_to_fill

	db.add(bus)
	db.commit()
	db.refresh(bus)

	return {
		"bus_id": bus.id,
		"seats_occupied": bus.seats_occupied,
		"standing_occupied": bus.standing_occupied,
		"seats_available": max(0, bus.capacity_seated - bus.seats_occupied),
		"standing_available": max(0, bus.capacity_standing - bus.standing_occupied),
	}


@router.post("/location")
def post_location(
	update: LocationUpdate,
	bus: Bus = Depends(get_bus_by_device_key),
	db: Session = Depends(get_db),
):
	bus.last_latitude = update.latitude
	bus.last_longitude = update.longitude
	if update.stop_id is not None:
		bus.last_stop_id = update.stop_id

	db.add(bus)
	db.commit()
	db.refresh(bus)

	return {"bus_id": bus.id, "ok": True}
