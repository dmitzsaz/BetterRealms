from aiohttp import web
import json
import ssl
import aiohttp
import time

verifiedTokens = {}


servers = {
    1: {
        "id": 1,
        "remoteSubscriptionId": "aaaa0000bbbb1111cccc2222dddd3333",
        "owner": "_zsaz_",
        "ownerUUID": "f78b7324b9a544e2b4c769ef0d0148c1",
        "name": "Максим - гей!",
        "motd": "This is a testing server!",
        "state": "OPEN",
        "daysLeft": 30,
        "expired": False,
        "expiredTrial": False,
        "worldType": "NORMAL",
        "players": [],
        "maxPlayers": 10,
        "minigameName": None,
        "minigameId": None,
        "minigameImage": None,
        "activeSlot": 1,
        "slots": None,
        "member": True
    }
}

pending_invites = []
exited_realms = set()

async def get_worlds(request):
    # Показываем только те реалмы, из которых пользователь не вышел
    visible_servers = [srv for rid, srv in servers.items() if rid not in exited_realms]
    return web.json_response({"servers": visible_servers})

async def mco_available(request):
    return web.Response(text='true', content_type='text/plain')

async def mco_client_compatible(request):
    return web.Response(text='COMPATIBLE', content_type='text/plain')

async def get_world_by_id(request):
    try:
        server_id = int(request.match_info.get('id'))
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid server id."}, status=400)
    server = servers.get(server_id)
    if server:
        return web.json_response(server)
    else:
        return web.json_response({"error": "Forbidden: you are not the owner of this server."}, status=403)

async def get_notifications(request):
    print(request['AuthData'])
    return web.json_response({"notifications": []})

async def get_invites_pending(request):
    print(request['AuthData'])
    # Показываем только инвайты по exited_realms
    filtered = [inv for inv in pending_invites if int(inv["invitationId"]) in exited_realms]
    return web.json_response({"invites": filtered})

async def get_activities_liveplayerlist(request):
    return web.json_response({"livePlayerList": []})

async def delete_invite(request):
    realm_id = request.match_info.get('id')
    try:
        realm_id_int = int(realm_id)
    except Exception:
        return web.Response(status=400)
    exited_realms.add(realm_id_int)
    # Добавляем инвайт в pending_invites только если его ещё нет
    if not any(inv["invitationId"] == realm_id for inv in pending_invites):
        invite = {
            "invitationId": realm_id,
            "worldName": servers.get(realm_id_int, {}).get("name", f"Realm {realm_id}"),
            "worldDescription": servers.get(realm_id_int, {}).get("motd", ""),
            "worldOwnerName": servers.get(realm_id_int, {}).get("owner", ""),
            "worldOwnerUuid": servers.get(realm_id_int, {}).get("ownerUUID", ""),
            "date": 0
        }
        pending_invites.append(invite)
    return web.Response(status=204)

async def put_invite_accept(request):
    realm_id = request.match_info.get('id')
    try:
        realm_id_int = int(realm_id)
    except Exception:
        return web.Response(status=400)
    # Убираем из exited_realms
    exited_realms.discard(realm_id_int)
    # Удаляем инвайт из pending_invites
    global pending_invites
    pending_invites = [inv for inv in pending_invites if inv["invitationId"] != realm_id]
    return web.Response(status=204)

async def get_mco_news(request):
    return web.json_response({})

async def get_uuid_by_username(username: str) -> str | None:
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("id")  # UUID без дефисов
            else:
                return None

async def join_world_pc(request):
    url = "http://171.22.16.162:8080/worlds/2/start"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                address = f"171.22.16.162:{data.get('mc_port', data.get('mcPort', '25565'))}"
                return web.json_response({
                    "address": address,
                    "pendingUpdate": False
                })
            else:
                return web.json_response({"error": "Failed to start remote world"}, status=500)

@web.middleware
async def logging_middleware(request, handler):
    method = request.method
    path = request.path
    query = dict(request.query)
    try:
        body = await request.text()
    except Exception:
        body = ''

    print(f"[LOG] {method} {path} | query={query} | body={body}")
    response = await handler(request)
    return response

app = web.Application(middlewares=[logging_middleware, validateAuth])
app.router.add_get('/worlds', get_worlds)
app.router.add_get('/mco/available', mco_available)
app.router.add_get('/mco/client/compatible', mco_client_compatible)
app.router.add_get('/worlds/{id}', get_world_by_id)
app.router.add_get('/notifications', get_notifications)
app.router.add_get('/invites/pending', get_invites_pending)
app.router.add_get('/activities/liveplayerlist', get_activities_liveplayerlist)
app.router.add_delete('/invites/{id}', delete_invite)
app.router.add_put('/invites/accept/{id}', put_invite_accept)
app.router.add_get('/mco/v1/news', get_mco_news)
app.router.add_get('/worlds/v1/{id}/join/pc', join_world_pc)

if __name__ == '__main__':
    web.run_app(app, port=80)
