import asyncio
import json
import logging

from aiohttp import web

from . import const


class Webserver:
    REQUEST_HEADERS = {"User-Agent": "ToyBot/beep-boop"}
    CALLBACK_PORT = 8000

    def __init__(self, parent=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent
        self.bot = self.parent.bot
        self.controller = self.parent.controller
        self.guilds = self.parent.guilds

        self.site = None

    async def start(self):
        async def handler(request: web.Request):
            if request.body_exists and request.can_read_body:
                body = await request.json()
                pieces = body.get("uid").split(":")
                self.guilds.add_user(pieces[0], pieces[1], body)

            return web.Response(body=json.dumps({"status": "OK"}))

        app = web.Application()
        app.router.add_get("/", handler)
        app.router.add_post("/", handler)
        runner = web.AppRunner(app)

        await runner.setup()

        self.site = web.TCPSite(runner, port=self.CALLBACK_PORT)

        await self.bot.wait_until_ready()

        await self.site.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())
