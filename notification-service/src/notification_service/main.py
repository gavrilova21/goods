from fastapi import FastAPI
from .models import db
import logging
from importlib_metadata import entry_points

logger = logging.getLogger(__name__)


def load_modules(app=None):
    for ep in entry_points()["notification_service.modules"]:
        logger.info("Loading module: %s", ep.name)
        mod = ep.load()
        if app:
            init_app = getattr(mod, "init_app", None)
            if init_app:
                init_app(app)


def get_app():
    app = FastAPI(title="Notification service")
    db.init_app(app)
    load_modules(app)
    return app
