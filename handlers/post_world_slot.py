from aiohttp import web
from database import crud

async def post_world_slot(request: web.Request):
    realmID = request.match_info.get("id")
    slot = request.match_info.get("slot")

    realm = crud.get_realm(realmID)
    if not realm:
        return web.json_response({"error": "Realm not found."}, status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.json_response({"error": "Forbidden: you are not a owner of this realm."}, status=403)

    payload = await request.json()

    for i in range(len(realm.worlds)):
        if realm.worlds[i]['id'] == slot:
            realm.worlds[i]['name'] = payload.get('slotName')
            break

    crud.update_realm(realmID, active_world=slot, worlds=realm.worlds)

    return web.json_response(status=204)