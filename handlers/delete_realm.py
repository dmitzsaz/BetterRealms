from aiohttp import web
from database import crud

async def delete_realm(request: web.Request):
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.json_response({"error": "Realm not found."}, status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.json_response({"error": "Forbidden: you are not a owner of this realm."}, status=403)

    crud.delete_realm(realm_id)

    return web.json_response({"success": True}, status=200)