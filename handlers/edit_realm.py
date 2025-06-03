from aiohttp import web
from database import crud

async def edit_realm(request: web.Request):
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)

    realm = crud.get_realm(realm_id)
    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.json_response({"error": "Forbidden: you are not a owner of this realm."}, status=403)

    payload = await request.json()
    name = payload.get("name", realm.name)
    motd = payload.get("motd", realm.motd)

    crud.update_realm(realm_id, name=name, motd=motd)

    return web.json_response(status=204)