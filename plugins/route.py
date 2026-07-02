# TitanXBots
# File Path: plugins/route.py

from aiohttp import web

routes = web.RouteTableDef()


@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """
    Health check endpoint.
    Used by hosting platforms such as Heroku, Render and Railway.
    """
    return web.json_response(
        {
            "status": "ok",
            "bot": "TitanXBots",
            "message": "Server is running smoothly"
        }
    )
