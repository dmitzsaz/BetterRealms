from aiohttp import web
import aiohttp
from database import crud
from database.models import RealmState
from config import settings


async def initialize_world(request: web.Request):
    """Инициализация Realms: создаёт первый мир и обновляет данные Realm.
    Тело запроса: {"name": "world_name", "description": "motd"}
    Делегирует создание мира RealmsOrchestrator.`"""
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)

    payload = await request.json(loads=lambda x: x) if request.can_read_body else {}
    world_name = payload.get("name", "My world")
    description = payload.get("description", "")

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.Response(status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.Response(status=403)

    # Обновляем Realm локально
    realm.state = RealmState.OPEN
    realm.worlds = [
        {
            "name": world_name,
            "id": 1,
            "picture": "",
            "type": "NORMAL",
            "gameMode": 0,
            "isHardcore": False,
        }
    ]
    realm.active_world = 1

    crud.update_realm(realm_id, name=realm.name, motd=realm.motd, state=realm.state, worlds=realm.worlds, active_world=realm.active_world)

    return web.json_response({"realmId": realm_id, "initialized": True}) 