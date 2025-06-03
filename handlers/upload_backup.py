from aiohttp import web, ClientSession
import aiohttp
from database import crud
from config import settings
import uuid
import os
import shutil
import zipfile
import gzip
import asyncio

from database.models import RealmState
from database.crud import create_world, update_world
from utils import upload_to_r2

TEMP_DIR = "worlds_tmp"

async def background_upload_and_update(world_id, final_path, final_name):
    try:
        s3_url = await upload_to_r2(final_path, final_name)
        update_world(world_id, s3URL=s3_url, status="idle")
    finally:
        if os.path.exists(final_path):
            os.remove(final_path)

async def upload_backup(request: web.Request):
    """Handles uploading a backup file to RealmsOrchestrator."""
    realm_id_raw = request.match_info.get("id")
    try:
        realm_id = int(realm_id_raw)
    except (TypeError, ValueError):
        return web.json_response({"error": "Invalid realm id."}, status=400)

    realm = crud.get_realm(realm_id)
    if not realm:
        return web.Response(status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.Response(status=403)

    presigned_post = {}
    presigned_post['worldClosed'] = True
    presigned_post['token'] = str(uuid.uuid4())
    presigned_post['uploadEndpoint'] = str(request.url)

    return web.json_response(presigned_post, status=200)

async def background_upload_and_update(world_id, final_path, final_name):
    try:
        s3_url = await upload_to_r2(final_path, final_name)
        print(f"Uploaded to R2: {s3_url}")
        update_world(world_id, s3URL=s3_url, status="idle")
    finally:
        if os.path.exists(final_path):
            os.remove(final_path)

async def prepare_and_pack_world(zip_path: str):
    import glob

    temp_unpack_dir = os.path.join(TEMP_DIR, f"unpack_{uuid.uuid4()}")
    os.makedirs(temp_unpack_dir, exist_ok=True)

    with gzip.open(zip_path, 'rb') as f_in:
        extracted_path = os.path.join(temp_unpack_dir, "extracted_file")
        with open(extracted_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    for root, dirs, files in os.walk(temp_unpack_dir):
        for d in dirs:
            if d == '__MACOSX' or d.startswith('.'):
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
        for f in files:
            if f == '.DS_Store' or f.startswith('.'):
                os.remove(os.path.join(root, f))

    items = [i for i in os.listdir(temp_unpack_dir) if not i.startswith('.') and i != '__MACOSX']
    if len(items) == 1 and os.path.isdir(os.path.join(temp_unpack_dir, items[0])):
        inner = os.path.join(temp_unpack_dir, items[0])
        for f in os.listdir(inner):
            shutil.move(os.path.join(inner, f), temp_unpack_dir)
        os.rmdir(inner)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(temp_unpack_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, temp_unpack_dir)
                zipf.write(abs_path, rel_path)

    shutil.rmtree(temp_unpack_dir)  

async def upload_handler(request: web.Request):
    realmID = request.match_info.get("realmID")
    slot = request.match_info.get("slot")

    realm = crud.get_realm(realmID)
    if not realm:
        return web.Response(status=404)

    user_uuid = request.get("AuthData", {}).get("uuid")
    if user_uuid != realm.ownerUUID:
        return web.Response(status=403)

    # Всегда читаем как octet-stream
    file_data = await request.read()

    os.makedirs(TEMP_DIR, exist_ok=True)
    filename = f"minecraft_temp_{realmID}_{slot}.zip"
    final_path = os.path.join(TEMP_DIR, filename)

    with open(final_path, "wb") as f:
        f.write(file_data)

    newWorlds = []
    for i in realm.worlds:
        if i['id'] != slot:
            newWorlds.append(i)

    world = create_world(name=f"minecraft_{realmID}_{slot}", s3URL="", status="creating", admins=[realm.owner[0]], players=realm.members)
    await prepare_and_pack_world(final_path)

    asyncio.create_task(background_upload_and_update(world.id, final_path, filename))

    newWorlds.append({"name": "minecraft_temp", "id": slot, "picture": "", "type": "NORMAL", "gameMode": 0, "isHardcore": False, "realmsorchestratorID": world.id})



    crud.update_realm(realmID, state=RealmState.OPEN, worlds=newWorlds)
    return web.Response(status=200)