from aiohttp import web
from database import crud


async def put_invite_accept(request: web.Request):
    invite_id_raw = request.match_info.get("id")
    try:
        invite_id = int(invite_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid invite id."}, status=400)

    invite = next((i for i in crud.get_invites() if i.id == invite_id), None)
    if not invite:
        return web.Response(status=404)

    username = request.get("AuthData", {}).get("username")
    if invite.invited_username != username:
        return web.Response(status=403)

    crud.accept_invite(invite_id)
    realm = crud.get_realm(invite.realms_id)
    if not realm:
        return web.Response(status=404)

    realm.members.append(invite.invited_username)
    crud.update_realm(realm.id, members=realm.members)

    return web.Response(status=204) 