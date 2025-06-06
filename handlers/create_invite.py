from aiohttp import web
from database import crud
from utils import getUUIDtoNickname

async def create_invite(request: web.Request):
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)
    
    realm = crud.get_realm(realm_id)
    if not realm:
        return web.Response(status=404)
    
    uuid = request.get("AuthData", {}).get("uuid")
    if uuid != realm.ownerUUID:
        return web.Response(status=403)

    invited_username = (await request.json()).get("name")
    invite = crud.get_invite(realm_id, invited_username)
    if invite:
        return web.Response(status=204)

    invited_uuid = await getUUIDtoNickname(invited_username)
    invite = crud.create_invite(realm_id, invited_username, invited_uuid)
    return web.Response(status=204)