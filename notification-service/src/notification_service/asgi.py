import asyncio
from .listener import listener

from .main import get_app

app = get_app()


@app.on_event("startup")
def startup():
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(listener(loop))
