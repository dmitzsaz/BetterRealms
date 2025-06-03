from aiohttp import web
from database import crud


async def delete_invite(request: web.Request):
    invite_id_raw = request.match_info.get("id")
    try:
        invite_id = int(invite_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid invite id."}, status=400)

    invite = next((i for i in crud.get_invites() if i.id == invite_id), None)
    if not invite:
        return web.Response(status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if invite.invited_uuid != user_uuid:
        return web.Response(status=403)

    crud.delete_invite(invite_id)
    return web.Response(status=204) 