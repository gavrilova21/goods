import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import aiohttp_session
import aioredis
from aiohttp import web
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_swagger import setup_swagger
import uvloop
import sqlalchemy as sa

from .routes import setup_routes
from .utils import get_config, connect_to_db
from .middlewares import error_middleware, auth_middleware

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
middlewares = [error_middleware, auth_middleware]


def create_app(config=None):
    if not config:
        config = get_config()

    cpu_count = multiprocessing.cpu_count()
    loop = asyncio.get_event_loop()
    redis_pool = loop.run_until_complete(aioredis.create_pool(("redis", 6379),))
    storage = RedisStorage(redis_pool, max_age=config["REFRESH_LIFETIME"] * 3600)
    session_middleware = aiohttp_session.session_middleware(storage)
    middlewares.append(session_middleware)
    app = web.Application(loop=loop, middlewares=middlewares)
    app["executor"] = ProcessPoolExecutor(cpu_count)
    app["config"] = config
    app.on_startup.append(init_database)
    setup_routes(app)
    setup_swagger(app, swagger_url="/api/doc")

    return app


async def init_database(app):
    app["pg"] = await connect_to_db(app["config"])
    app["pg"] = sa.create_engine(
        "postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}".format(
            **app["config"]
        )
    )
