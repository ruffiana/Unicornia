import asyncio
import json
import logging

from aiohttp import web

from . import const


class WebServer:
    REQUEST_HEADERS = {"User-Agent": "ToyBot/beep-boop"}

    def __init__(self, parent=None, port=const.WEBSERVER_PORT, callback=None):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.setLevel(const.LOGGER_LEVEL)

        self.parent = parent
        self.port = port
        self.callback = callback
        self.app = web.Application()
        self.app.add_routes([web.post("/", self.handle_post)])

    async def handle_post(self, request: web.Request):
        data = await request.json()  # Assuming the POST request contains JSON data
        print(f"Received POST data: {data}")
        if self.callback:
            self.callback(data)  # Call the parent class's method
        return web.Response(body=json.dumps({"status": "OK"}))

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        self.site = web.TCPSite(runner, "localhost", self.port)
        await self.site.start()
        print(f"Server running on http://localhost:{self.port}")

    async def run(self):
        await self.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())
