from aiohttp import web
import aiohttp
from config import settings
from database import crud
import asyncio

async def join_world_pc(request: web.Request):
    """Запрашивает RealmsOrchestrator на запуск мира и возвращает IP:Port для подключения."""
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.Response(status=400)

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.Response(status=404)

    username = request.get("AuthData", {}).get("username")
    if username not in (realm.members or []) and username not in (realm.owner or []):
        return web.Response(status=403)

    realmsorchestratorID = realm.worlds[realm.active_world]['realmsorchestratorID']
    orchestrator_url = f"{settings.REALMSORCHESTRATOR_URL}/worlds/{realmsorchestratorID}/start"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(orchestrator_url) as resp:
                if resp.status != 200:
                    return web.json_response({"error": "Failed to start remote world"}, status=500)
                data = await resp.json()
    except Exception as e:
        return web.json_response({"error": "Failed to contact orchestrator", "details": str(e)}, status=500)

    host = settings.REALMSORCHESTRATOR_IP
    port = data.get("mc_port") or data.get("mcPort") or 25565
    address = f"{host}:{port}"

    await asyncio.sleep(2) # waiting for docker to spin up the world

    print(address)

    return web.json_response({
        "address": address,
        "pendingUpdate": False
    }) 