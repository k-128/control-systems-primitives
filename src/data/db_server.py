'''
requirements:
- databases[sqlite], SQLAlchemy, starlette, uvicorn, pyyaml
'''

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime as dt
from random import random, randint
from typing import Literal

import databases
import sqlalchemy
import uvicorn
import yaml
from starlette.applications import Starlette
from starlette.config import Config
from starlette.routing import Route
from starlette.endpoints import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.schemas import SchemaGenerator
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.testclient import TestClient


# ------
# Config
# -----------------------------------------------------------------------------
CONFIG      = Config(".env")
PATH_DATA   = Path().cwd() / "bin"
os.makedirs(PATH_DATA, exist_ok=True)

# Database
HOST    = CONFIG("HOST",    cast=str, default="localhost")
PORT    = CONFIG("PORT",    cast=int, default=3333)
DB_URL  = CONFIG("DB_URL",  cast=str, default="bin/data.db")
DB_URL  = f"sqlite:///{DB_URL}"
DB      = databases.Database(DB_URL)
MTA     = sqlalchemy.MetaData()
SENSORS = sqlalchemy.Table("sensors", MTA,
    sqlalchemy.Column("id", sqlalchemy.INTEGER, primary_key=True),
    sqlalchemy.Column("ts", sqlalchemy.TEXT),
    sqlalchemy.Column("sensor_id", sqlalchemy.TEXT),
    sqlalchemy.Column("value", sqlalchemy.REAL),
)
ENGINE = sqlalchemy.create_engine(DB_URL)
MTA.create_all(ENGINE)

# Server
SCHEMAS = SchemaGenerator(
    {"openapi": "3.0.0", "info": {"title": "Sensors DB API", "version": "1.0"}}
)


# ---------
# Endpoints
# -----------------------------------------------------------------------------
class Sensors(HTTPEndpoint):
    async def get(self, r: Request) -> JSONResponse:
        '''
        responses:
          '200':
            description: Sensors data.
            example: [
              {"ts": "2021-...", "sensor_id": "sen_01", "value": 26.1},
              {"ts": "2021-...", "sensor_id": "sen_02", "value": 54},
              {"ts": "2021-...", "sensor_id": "sen_03", "value": 26}
            ]
        '''
        try:
            whereclause = None
            order_by    = None
            limit       = None
            for k, v in r.query_params.items():
                if k == "where":
                    whereclause = sqlalchemy.sql.text(v)
                elif k == "order_by":
                    order_by = sqlalchemy.sql.text(v)
                elif k == "limit":
                    limit = v

            q = SENSORS.select() \
                .where(whereclause) \
                .order_by(order_by) \
                .limit(limit)
            resp = []
            for r in await DB.fetch_all(q):
                resp.append(tuple(r))

            return JSONResponse(resp, status_code=200)
        except Exception as e:
            return JSONResponse(f"{type(e).__name__}: {e}", status_code=400)

    async def post(self, r: Request) -> JSONResponse:
        '''
        responses:
          200:
            description: Sensors data.
            example: [
              {"ts": "2021-...", "sensor_id": "sen_01", "value": 26.1},
              {"ts": "2021-...", "sensor_id": "sen_02", "value": 54},
              {"ts": "2021-...", "sensor_id": "sen_03", "value": 26}
            ]
        '''
        try:
            v = await r.json()
            q = SENSORS.insert()
            await DB.execute_many(query=q, values=v)
            return JSONResponse(status_code=200)
        except Exception as e:
            return JSONResponse(f"{type(e).__name__}: {e}", status_code=400)


def openapi_schema(request):
    return SCHEMAS.OpenAPIResponse(request=request)


# ------
# Server
# -----------------------------------------------------------------------------
async def on_startup() -> None:
    print("Starting db server...")
    await DB.connect()


async def on_shutdown() -> None:
    await DB.disconnect()
    print("DB server stopped, io cleaned up, db disconnected.")


APP = Starlette(
    debug=True,
    routes=[
        Route("/sensors", endpoint=Sensors, methods=["GET", "POST"]),
        Route("/schema", endpoint=openapi_schema, include_in_schema=False)
    ],
    middleware=[
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_headers=["*"],
            allow_methods=["GET", "POST"],
            allow_credentials=["*"],
        ),
        Middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost","testserver"]
        )
    ],
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
)


def print_schema() -> None:
    s = SCHEMAS.get_schema(routes=APP.routes)
    print(yaml.dump(s, default_flow_style=False))


def run() -> None:
    uvicorn.run(APP, host=HOST, port=int(PORT))


# -----
# Tests
# -----------------------------------------------------------------------------
c = TestClient(APP)


class TestsClient:
    def __init__(self) -> None:
        self.log = logging.getLogger("test")
        self.log.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(levelname)s\t[%(asctime)s] %(name)s - %(message)s",
            "%H:%M:%S"
        )
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def _get_sensors_inputs(self):
        ts = dt.now()
        return [
            {
                "ts": f"{ts}",
                "sensor_id": "sen_01",
                "value": random() * randint(1, 40)
            },
            {
                "ts": f"{ts}",
                "sensor_id": "sen_02",
                "value": random() * randint(1, 100)
            },
            {
                "ts": f"{ts}",
                "sensor_id": "sen_03",
                "value": random() * randint(1, 40)
            },
        ]

    def test_schema(self) -> None:
        r = c.get("/schema")
        if r.status_code != 200:
            self.log.error(f"err: {r.status_code}: {r.content}")
        self.log.debug(f"Schema.get[{r.status_code}]")

    def test_endpoints(self, test: Literal["GET", "POST"]) -> None:
        if test == "GET":
            r = c.get("/sensors")
            if r.status_code != 200:
                self.log.error(f"err: {r.status_code}: {r.content}")
            self.log.debug(f"Sensors.get[{r.status_code}] - {r.content}")

            params = {
                "where": "sensor_id == 'sen_02'",
                "order_by": "id desc",
                "limit": 2
            }
            r = c.get("/sensors", params=params)
            if r.status_code != 200:
                self.log.error(f"err: {r.status_code}: {r.content}")
            self.log.debug(f"Sensors.get[{r.status_code}] - {r.content}")

        elif test == "POST":
            body = json.dumps(self._get_sensors_inputs())
            r = c.post("/sensors", data=body)
            if r.status_code != 200:
                self.log.error(f"err: {r.status_code}: {r.content}")
            self.log.debug(f"Sensors.post[{r.status_code}]")

    def run_tests(self) -> None:
        self.test_schema()
        self.test_endpoints("GET")
        self.test_endpoints("POST")


if __name__ == "__main__":
    assert sys.argv[-1] in ("run", "schema", "tests"), "arg: [run|schema|tests]"
    if sys.argv[-1] == "run":
        run()
    elif sys.argv[-1] == "schema":
        print_schema()
    elif sys.argv[-1] == "tests":
        t = TestsClient()
        t.run_tests()
