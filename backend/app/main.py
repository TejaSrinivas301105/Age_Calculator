from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import Base, engine
from .routers import device, public


@asynccontextmanager
async def lifespan(app: FastAPI):
	# Create tables on startup for demo
	Base.metadata.create_all(bind=engine)
	yield


app = FastAPI(title="Village Bus Service", lifespan=lifespan)

app.include_router(device.router)
app.include_router(public.router)


@app.get("/")
def root():
	return {"ok": True, "service": "Village Bus Service"}
