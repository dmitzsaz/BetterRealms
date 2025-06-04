from aiohttp import web
from database import crud
from database.models import RealmState
import json


def _realm_to_dict(realm: crud.Realm, include_slot: bool = False) -> dict:
    worlds = realm.worlds if isinstance(realm.worlds, list) else []
    world_type = worlds[0].get("type", "NORMAL") if worlds else "NORMAL"

    data =  {
        "id": realm.id,
        "remoteSubscriptionId": realm.id,
        "owner": realm.owner[0] if isinstance(realm.owner, list) and realm.owner else "",
        "ownerUUID": realm.ownerUUID,
        "name": realm.name,
        "motd": realm.motd or "",
        "state": realm.state.value if isinstance(realm.state, RealmState) else str(realm.state),
        "daysLeft": 30,
        "expired": False,
        "expiredTrial": False,
        "worldType": world_type,
        "players": realm.members,
        "maxPlayers": 5,
        "minigameName": None,
        "minigameId": None,
        "minigameImage": None,  
        "activeSlot": realm.active_world + 1 or 1,
        "slots": None,
        "member": True,
    }

    if include_slot:
        data['slots'] = [
            {
                "options": json.dumps({
                    "slotName": world.get("name"),
                    "gameMode": world.get("gameMode"),
                    "hardcore": world.get("isHardcore"),
                    "type": world.get("type"),
                }),
                "settings": [
                    {"name": "hardcore", "value": world.get("isHardcore")}
                ],
                "slotId": world.get("id") + 1,
            }
            for world in worlds
        ]

    return data

async def get_worlds(request: web.Request):
    user_data = request.get("AuthData", {})
    username = user_data.get("username")

    realms = crud.get_realms()

    user_owned_realms = [r for r in realms if username in (r.owner or [])]
    if not user_owned_realms and username:
        default_name = f"{username or 'Player'}'s Realm"
        new_realm = crud.create_realm(
            name=default_name,
            motd="BetterRealms",
            worlds=[],
            owner=[username],
            ownerUUID=user_data.get("uuid"),
            members=[username],
            state=RealmState.UNINITIALIZED,
            active_world=None,
        )
        realms.append(new_realm)

    visible = [r for r in realms if username in (r.members or []) or username in (r.owner or [])]

    servers = [_realm_to_dict(r) for r in visible]
    return web.json_response({"servers": servers}) 