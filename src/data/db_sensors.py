'''
requirements:
- aiosqlite, apscheduler, starlette
'''

import asyncio
import atexit
import os
from pathlib import Path
from datetime import datetime as dt
from dataclasses import dataclass, field
from random import randint, random

import aiosqlite
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from starlette.config import Config


# ------
# Config
# -----------------------------------------------------------------------------
CONFIG      = Config(".env")
JOB_SECONDS = 5  # Seconds, cronjob executions
PATH_DATA   = Path().cwd() / "bin"
os.makedirs(PATH_DATA, exist_ok=True)

# Database
DB_URL = CONFIG("DB_URL", cast=str, default="bin/data.db")


# -------
# Sensors
# -----------------------------------------------------------------------------
@dataclass
class SensorsData:
    ts: dt        = field(default=dt.fromtimestamp(0), init=True)
    sen_01: bool  = False
    sen_02: float = -273.15
    sen_03: float = -273.15
    sen_04: float = -1.0


def read_sensor_data() -> SensorsData:
    data = SensorsData()
    data.sen_01 = True if randint(-1, 1) > 0 else False
    data.sen_02 = random() * randint(-1_000, 1_000)
    data.sen_03 = random() * randint(-1_000, 1_000)
    data.sen_04 = random() * randint(-1_000, 1_000)
    return data


# ---------
# Execution
# -----------------------------------------------------------------------------
async def save_sensors_data(
    db_conn: aiosqlite.Connection,
    data: SensorsData,
) -> None:
    d = [(data.ts, k, v) for k, v in data.__dict__.items() if k != "ts"]

    async with db_conn.cursor() as c:
        await c.execute(
            '''CREATE TABLE IF NOT EXISTS sensors
            (
                id INTEGER PRIMARY KEY,
                ts TEXT,
                sensor_id TEXT,
                value REAL
            )'''
        )
        await c.executemany(
            "INSERT INTO sensors (ts, sensor_id, value) VALUES (?, ?, ?)",
            d
        )

    await db_conn.commit()


async def db_job() -> None:
    t_init  = dt.now()
    data    = read_sensor_data()
    data.ts = t_init

    async with aiosqlite.connect(DB_URL) as db:
        await save_sensors_data(db, data)

    cycle_duration = (dt.now() - t_init).total_seconds()
    print(f"db_job took {cycle_duration:.6f}s, data: {data.__repr__()}")


def cleanup():
    print("db job stopped. io cleaned up.")


async def run() -> None:
    atexit.register(cleanup)

    job_defaults = {"max_instances": 2, "coalesce": False}
    scheduler = AsyncIOScheduler(job_defaults=job_defaults)
    scheduler.add_job(db_job, "cron", second=f"*/{JOB_SECONDS}", args=[])

    print(f"Starting db job, run every {JOB_SECONDS} seconds...")
    scheduler.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.create_task(run())
        loop.run_forever()
    finally:
        loop.close()
