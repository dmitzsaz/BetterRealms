from aiohttp import web
from database import crud
import time


async def get_invites_pending(request: web.Request):
    user_uuid = request.get("AuthData", {}).get("uuid")
    username = request.get("AuthData", {}).get("username")
    if not user_uuid:
        return web.json_response({"invites": []})

    invites = crud.get_invite_by_username(username)

    result = []
    for inv in invites:
        realm = crud.get_realm(inv.realms_id)
        if not realm:
            continue
        owner_name = realm.owner[0] if isinstance(realm.owner, list) and realm.owner else ""
        owner_uuid = realm.ownerUUID
        result.append({
            "invitationId": str(inv.id),
            "worldName": realm.name,
            "worldDescription": realm.motd or "",
            "worldOwnerName": owner_name,
            "worldOwnerUuid": owner_uuid,
            "date": int(time.time() * 1000),
        })

    return web.json_response({"invites": result}) 