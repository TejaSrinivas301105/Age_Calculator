from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import Base, SessionLocal, engine
from app.models import Bus, Route, RouteStop, Stop


def seed():
	Base.metadata.create_all(bind=engine)
	session: Session = SessionLocal()
	try:
		# Clear existing
		session.query(RouteStop).delete()
		session.query(Bus).delete()
		session.query(Route).delete()
		session.query(Stop).delete()
		session.commit()

		# Stops
		stops = [
			Stop(name="Village A", latitude=12.9716, longitude=77.5946),
			Stop(name="Village B", latitude=12.9762, longitude=77.6033),
			Stop(name="Village C", latitude=12.9830, longitude=77.6071),
			Stop(name="Village D", latitude=12.9900, longitude=77.6120),
		]
		session.add_all(stops)
		session.flush()

		# Route
		route = Route(name="A-B-C-D")
		session.add(route)
		session.flush()

		rs = [
			RouteStop(route_id=route.id, stop_id=stops[0].id, sequence_index=1),
			RouteStop(route_id=route.id, stop_id=stops[1].id, sequence_index=2),
			RouteStop(route_id=route.id, stop_id=stops[2].id, sequence_index=3),
			RouteStop(route_id=route.id, stop_id=stops[3].id, sequence_index=4),
		]
		session.add_all(rs)

		# Buses
		buses = [
			Bus(
				registration_number="KA-01-AB-1234",
				route_id=route.id,
				capacity_seated=30,
				capacity_standing=20,
				device_api_key="device-key-1234",
				last_stop_id=stops[0].id,
			),
			Bus(
				registration_number="KA-01-AB-5678",
				route_id=route.id,
				capacity_seated=28,
				capacity_standing=22,
				device_api_key="device-key-5678",
				last_stop_id=stops[1].id,
			),
		]
		session.add_all(buses)

		session.commit()
		print("Seeded sample data.")
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()


if __name__ == "__main__":
	seed()
