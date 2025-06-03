from aiohttp import web

from database.db import create_database
from config import settings
from utils import validateAuth, logging_middleware

from handlers.other import get_mco_news, get_notifications, mco_available, mco_client_compatible, regions_ping_stat, get_activities_liveplayerlist, get_world_templates
from handlers.get_worlds import get_worlds
from handlers.get_world_by_id import get_world_by_id
from handlers.get_invites_pending import get_invites_pending
from handlers.delete_invite import delete_invite
from handlers.put_invite_accept import put_invite_accept
from handlers.join_world_pc import join_world_pc
from handlers.initialize_world import initialize_world
from handlers.upload_backup import upload_backup, upload_handler
from handlers.put_world_slot import put_world_slot
from handlers.post_world_slot import post_world_slot
from handlers.delete_realm import delete_realm
from handlers.edit_realm import edit_realm
from handlers.create_invite import create_invite

create_database()

app = web.Application(client_max_size=4096**3)

async def index(request):
    return web.Response(text='Hello, World!')

routes = [
    web.get('/worlds', get_worlds),
    web.get('/mco/available', mco_available),
    web.get('/mco/client/compatible', mco_client_compatible),
    web.get('/worlds/{id}', get_world_by_id),
    web.post('/worlds/{id}', edit_realm),
    web.get('/notifications', get_notifications),
    web.get('/invites/pending', get_invites_pending),
    web.get('/activities/liveplayerlist', get_activities_liveplayerlist),
    web.delete('/invites/{id}', delete_invite),
    web.put('/invites/accept/{id}', put_invite_accept),
    web.get('/mco/v1/news', get_mco_news),
    web.get('/worlds/v1/{id}/join/pc', join_world_pc),
    web.post('/worlds/{id}/initialize', initialize_world),
    web.put('/worlds/{id}/backups/upload', upload_backup),
    web.put('/worlds/{id}/slot/{slot}', put_world_slot),
    web.post('/worlds/{id}/slot/{slot}', post_world_slot),

    web.get('/worlds/templates/{template}', get_world_templates),
    web.post('/regions/ping/stat', regions_ping_stat),
    web.post("/upload/{realmID}/{slot}", upload_handler),

    web.put('/worlds/{id}/close', delete_realm),
    web.post('/invites/{id}', create_invite),
]

app.middlewares.append(validateAuth)
app.middlewares.append(logging_middleware)
app.add_routes(routes)

listen_addr = settings.LISTEN_ADDR.split(":")
listen_port = int(listen_addr[1])
listen_host = listen_addr[0]
web.run_app(app, host=listen_host, port=listen_port)
