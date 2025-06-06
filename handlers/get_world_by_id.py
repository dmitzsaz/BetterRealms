from aiohttp import web
from database import crud
from .get_worlds import _realm_to_dict  # reuse converter


async def get_world_by_id(request: web.Request):
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.json_response({"error": "Realm not found."}, status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid not in (realm.members or []) and user_uuid not in (realm.owner or []):
        return web.json_response({"error": "Forbidden: you are not a member/owner of this realm."}, status=403)

    return web.json_response(_realm_to_dict(realm, True)) 