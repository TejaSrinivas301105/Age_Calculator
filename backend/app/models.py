from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
	DateTime,
	Float,
	ForeignKey,
	Integer,
	String,
	UniqueConstraint,
	func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Stop(Base):
	__tablename__ = "stops"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
	latitude: Mapped[float] = mapped_column(Float, nullable=False)
	longitude: Mapped[float] = mapped_column(Float, nullable=False)

	route_stops: Mapped[list[RouteStop]] = relationship("RouteStop", back_populates="stop")
	buses_here: Mapped[list[Bus]] = relationship("Bus", back_populates="last_stop")


class Route(Base):
	__tablename__ = "routes"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)

	route_stops: Mapped[list[RouteStop]] = relationship("RouteStop", back_populates="route")
	buses: Mapped[list[Bus]] = relationship("Bus", back_populates="route")


class RouteStop(Base):
	__tablename__ = "route_stops"
	__table_args__ = (
		UniqueConstraint("route_id", "stop_id", name="uq_route_stop"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False, index=True)
	stop_id: Mapped[int] = mapped_column(ForeignKey("stops.id"), nullable=False, index=True)
	sequence_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

	route: Mapped[Route] = relationship("Route", back_populates="route_stops")
	stop: Mapped[Stop] = relationship("Stop", back_populates="route_stops")


class Bus(Base):
	__tablename__ = "buses"
	__table_args__ = (
		UniqueConstraint("registration_number", name="uq_bus_registration"),
		UniqueConstraint("device_api_key", name="uq_device_api_key"),
	)

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	registration_number: Mapped[str] = mapped_column(String(50), nullable=False)
	route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False, index=True)

	capacity_seated: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
	capacity_standing: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
	seats_occupied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
	standing_occupied: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

	last_latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	last_longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
	last_stop_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stops.id"), nullable=True)
	last_reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

	device_api_key: Mapped[str] = mapped_column(String(128), nullable=False)

	route: Mapped[Route] = relationship("Route", back_populates="buses")
	last_stop: Mapped[Optional[Stop]] = relationship("Stop", back_populates="buses_here")
