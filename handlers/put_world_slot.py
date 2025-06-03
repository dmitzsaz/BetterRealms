from aiohttp import web
from database import crud
from database.models import RealmState
import os


DEFAULT_WORLD_TEMPLATE = {
    "picture": "",
    "type": "NORMAL",
    "gameMode": 0,
    "isHardcore": False,
}

async def put_world_slot(request: web.Request):
    realm_id_raw = request.match_info.get("id")
    slot_raw = request.match_info.get("slot")

    try:
        realm_id = int(realm_id_raw)
        slot = int(slot_raw)
        if slot < 1 or slot > 4:
            raise ValueError
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid id or slot."}, status=400)

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.Response(status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.Response(status=403)

    # Всегда открываем Realm перед сменой слота
    crud.update_realm(realm_id, state=RealmState.OPEN)

    worlds = realm.worlds or []
    existing = next((w for w in worlds if w.get("id") == slot - 1), None)
    if not existing:
        worlds.append({
            **DEFAULT_WORLD_TEMPLATE,
            "id": slot,
            "name": f"World {slot}",
        })
        crud.update_realm(realm_id, active_world=slot, worlds=worlds)
    else:
        crud.update_realm(realm_id, active_world=slot)

    return web.json_response(True) 