from __future__ import annotations

import random
import time
from typing import Iterator

import requests


BASE_URL = "http://127.0.0.1:8000"


def jitter(values: list[int]) -> Iterator[int]:
	for v in values:
		yield max(0, v + random.randint(-1, 2))


def simulate(device_key: str, steps: int = 20) -> None:
	session = requests.Session()
	session.headers.update({"X-Device-Key": device_key})

	# Send a few location updates
	lat, lon = 12.9716, 77.5946
	for i in range(steps):
		lat += random.uniform(-0.0005, 0.0005)
		lon += random.uniform(-0.0005, 0.0005)
		resp = session.post(f"{BASE_URL}/device/location", json={"latitude": lat, "longitude": lon})
		resp.raise_for_status()

		# Send occupancy deltas
		people_in = random.choice([0, 1, 2, 3])
		people_out = random.choice([0, 1, 2])
		resp = session.post(
			f"{BASE_URL}/device/occupancy",
			json={"people_in": people_in, "people_out": people_out},
		)
		resp.raise_for_status()

		print("Step", i + 1, resp.json())
		time.sleep(0.3)


if __name__ == "__main__":
	simulate(device_key="device-key-1234", steps=30)
