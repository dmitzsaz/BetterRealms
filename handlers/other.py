from aiohttp import web

async def get_mco_news(request):
    return web.json_response({"news": []})

async def get_notifications(request):
    return web.json_response({"notifications": []})

async def mco_available(request):
    return web.Response(text='true', content_type='text/plain')

async def mco_client_compatible(request):
    return web.Response(text='COMPATIBLE', content_type='text/plain')

async def regions_ping_stat(request: web.Request):
    return web.Response(status=204)

async def get_activities_liveplayerlist(request: web.Request):
    return web.json_response({"livePlayerList": []}) 

async def get_world_templates(request: web.Request):
    page = int(request.query.get("page", 1))
    size = int(request.query.get("pageSize", 10))
    return web.json_response({
        "templates": [],
        "page": page,
        "size": 0,
        "total": 0
    }) 