from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


DATABASE_URL: str = "sqlite:////workspace/backend/transport.db"

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
	"""FastAPI dependency that yields a SQLAlchemy session."""
	db: Session = SessionLocal()
	try:
		yield db
	finally:
		db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
	"""Provide a transactional scope around a series of operations."""
	session: Session = SessionLocal()
	try:
		yield session
		session.commit()
	except Exception:
		session.rollback()
		raise
	finally:
		session.close()
