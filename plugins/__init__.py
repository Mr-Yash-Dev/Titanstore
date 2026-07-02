# TitanXBots
# File Path: plugins/__init__.py

from aiohttp import web

from .route import routes


async def web_server() -> web.Application:
    """
    Creates and returns the aiohttp web application.
    """

    app = web.Application(
        client_max_size=30 * 1024 * 1024  # 30 MB
    )

    app.add_routes(routes)

    return app
