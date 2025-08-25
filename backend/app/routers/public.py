from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Bus, Route, RouteStop, Stop
from ..schemas import BusAvailability, BusStatus


router = APIRouter(prefix="", tags=["public"])


@router.get("/search", response_model=list[BusAvailability])
def search_buses(from_stop: str, to_stop: str, db: Session = Depends(get_db)):
	start = db.query(Stop).filter(Stop.name.ilike(from_stop)).first()
	end = db.query(Stop).filter(Stop.name.ilike(to_stop)).first()
	if not start or not end:
		raise HTTPException(status_code=404, detail="One or both stops not found")

	# Find routes that contain both stops in correct order
	routes_with_start = (
		db.query(RouteStop).filter(RouteStop.stop_id == start.id).subquery()
	)
	routes_with_end = (
		db.query(RouteStop).filter(RouteStop.stop_id == end.id).subquery()
	)

	# Join on route id and sequence order
	matching_routes = (
		db.query(Route)
		.join(routes_with_start, routes_with_start.c.route_id == Route.id)
		.join(routes_with_end, routes_with_end.c.route_id == Route.id)
		.filter(routes_with_start.c.sequence_index < routes_with_end.c.sequence_index)
		.all()
	)

	availabilities: list[BusAvailability] = []
	for route in matching_routes:
		for bus in route.buses:
			seats_available = max(0, bus.capacity_seated - bus.seats_occupied)
			standing_available = max(0, bus.capacity_standing - bus.standing_occupied)
			availabilities.append(
				BusAvailability(
					bus_id=bus.id,
					registration_number=bus.registration_number,
					route_name=route.name,
					seats_available=seats_available,
					standing_available=standing_available,
					is_full=(seats_available == 0 and standing_available == 0),
					last_latitude=bus.last_latitude,
					last_longitude=bus.last_longitude,
					last_stop_name=bus.last_stop.name if bus.last_stop else None,
				)
			)

	return availabilities


@router.get("/bus/{bus_id}", response_model=BusStatus)
def get_bus_status(bus_id: int, db: Session = Depends(get_db)):
	bus = db.get(Bus, bus_id)
	if not bus:
		raise HTTPException(status_code=404, detail="Bus not found")
	return _bus_to_status(bus)


@router.get("/bus/by-registration/{registration}", response_model=BusStatus)
def get_bus_status_by_registration(registration: str, db: Session = Depends(get_db)):
	bus = db.query(Bus).filter(Bus.registration_number == registration).first()
	if not bus:
		raise HTTPException(status_code=404, detail="Bus not found")
	return _bus_to_status(bus)


def _bus_to_status(bus: Bus) -> BusStatus:
	seats_available = max(0, bus.capacity_seated - bus.seats_occupied)
	standing_available = max(0, bus.capacity_standing - bus.standing_occupied)
	return BusStatus(
		bus_id=bus.id,
		registration_number=bus.registration_number,
		route_name=bus.route.name,
		capacity_seated=bus.capacity_seated,
		capacity_standing=bus.capacity_standing,
		seats_occupied=bus.seats_occupied,
		standing_occupied=bus.standing_occupied,
		seats_available=seats_available,
		standing_available=standing_available,
		is_full=(seats_available == 0 and standing_available == 0),
		last_latitude=bus.last_latitude,
		last_longitude=bus.last_longitude,
		last_stop_name=bus.last_stop.name if bus.last_stop else None,
		last_reported_at=bus.last_reported_at,
	)
