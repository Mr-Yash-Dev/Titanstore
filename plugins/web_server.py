from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({
        "status": "ok",
        "bot": "TitanXBots",
        "message": "Server is running smoothly"
    })

async def web_server() -> web.Application:
    app = web.Application(client_max_size=30000000)
    app.add_routes(routes)
    return app
  
