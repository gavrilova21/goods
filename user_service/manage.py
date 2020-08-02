import asyncio
import logging

import uvloop
from aio_manager import Command, Manager
from aio_manager.commands.runserver import RunServer as BaseRunServer
from aiohttp import web

from user_service.app import create_app
from user_service.utils import create_database, drop_database, get_config, migrate

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

app = create_app()
manager = Manager(app)
config = get_config()


class RunServer(BaseRunServer):
    def run(self, app, args):
        logging.basicConfig(level=args.level)
        logging.getLogger().setLevel(args.level)
        web.run_app(app, host=args.hostname, port=args.port, access_log=None)


manager.add_command(RunServer(app))


class CreateDatabase(Command):
    def run(self, app, args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(create_database(config))


manager.add_command(CreateDatabase("create_database", app))


class DropDatabase(Command):
    def run(self, app, args):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(drop_database(config))


manager.add_command(DropDatabase("drop_database", app))


class Migrate(Command):
    def run(self, app, args):
        migrate(config)


manager.add_command(Migrate("migrate", app))


class ResetDB(Command):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._commands = [
            DropDatabase(*args, **kwargs),
            CreateDatabase(*args, **kwargs),
            Migrate(*args, **kwargs),
        ]

    def run(self, app, args):
        for cm in self._commands:
            cm.run(app, args)


manager.add_command(ResetDB("reset_db", app))

if __name__ == "__main__":
    manager.run()
